<script lang="ts">
	import ImageUpload from '$lib/components/ImageUpload.svelte';
	import MetadataForm from '$lib/components/MetadataForm.svelte';
	import AnalemmaViewer from '$lib/components/AnalemmaViewer.svelte';
	import SampleGallery from '$lib/components/SampleGallery.svelte';
	import DownloadButton from '$lib/components/DownloadButton.svelte';
	import type { ExifData } from '$lib/utils/exif';
	import { analyzeImage, type AnalyzeResponse } from '$lib/utils/api';
	import type { MetadataFields } from '$lib/components/MetadataForm.svelte';
	import type { SampleImageData } from '$lib/data/samples';

	let uploadedFile: File | null = $state(null);
	let previewUrl = $state('');
	let exifData: ExifData | null = $state(null);
	let analemmaResult: AnalyzeResponse | null = $state(null);
	let isAnalyzing = $state(false);
	let errorMsg = $state('');
	let imageWidth = $state(0);
	let imageHeight = $state(0);

	let metadata: MetadataFields = $state({
		latitude: '',
		longitude: '',
		datetime: '',
		focalLength: '',
		sensorWidth: '',
		sensorHeight: '',
		sunX: '',
		sunY: ''
	});

	let canGenerate = $derived(
		!!metadata.latitude &&
			!!metadata.longitude &&
			!!metadata.datetime &&
			!!metadata.focalLength &&
			!!metadata.sensorWidth &&
			!!metadata.sensorHeight &&
			(!!uploadedFile || !!previewUrl)
	);

	function onFileSelected(file: File, exif: ExifData, url: string) {
		uploadedFile = file;
		previewUrl = url;
		exifData = exif;
		analemmaResult = null;
		errorMsg = '';

		// Get image dimensions from the preview
		const img = new Image();
		img.onload = () => {
			imageWidth = img.naturalWidth;
			imageHeight = img.naturalHeight;
		};
		img.src = url;
	}

	function buildFormData(): FormData | null {
		if (!uploadedFile) return null;
		const fd = new FormData();
		fd.append('file', uploadedFile);
		fd.append('latitude', metadata.latitude);
		fd.append('longitude', metadata.longitude);
		fd.append('datetime_str', metadata.datetime);
		fd.append('focal_length_mm', metadata.focalLength);
		fd.append('sensor_width_mm', metadata.sensorWidth);
		fd.append('sensor_height_mm', metadata.sensorHeight);
		if (metadata.sunX) fd.append('sun_x', metadata.sunX);
		if (metadata.sunY) fd.append('sun_y', metadata.sunY);
		return fd;
	}

	async function generate() {
		errorMsg = '';
		const fd = buildFormData();
		if (!fd) return;

		isAnalyzing = true;
		try {
			analemmaResult = await analyzeImage(fd);
		} catch (err) {
			errorMsg = err instanceof Error ? err.message : 'Analysis failed';
			analemmaResult = null;
		} finally {
			isAnalyzing = false;
		}
	}

	async function onSampleSelected(sample: SampleImageData) {
		errorMsg = '';
		analemmaResult = null;

		// Load the sample image from the backend's input_images
		metadata.latitude = String(sample.latitude);
		metadata.longitude = String(sample.longitude);
		metadata.datetime = sample.datetime;
		metadata.focalLength = String(sample.focalLength);
		metadata.sensorWidth = String(sample.sensorWidth);
		metadata.sensorHeight = String(sample.sensorHeight);
		metadata.sunX = '';
		metadata.sunY = '';
		exifData = null;

		// Fetch the thumbnail as a preview
		previewUrl = sample.thumbnail;

		// We need the actual image file to send to the backend.
		// Fetch the thumbnail and create a File from it.
		try {
			const res = await fetch(sample.thumbnail);
			const blob = await res.blob();
			uploadedFile = new File([blob], `${sample.id}.jpg`, { type: 'image/jpeg' });

			const img = new Image();
			img.onload = () => {
				imageWidth = img.naturalWidth;
				imageHeight = img.naturalHeight;
			};
			img.src = sample.thumbnail;
		} catch {
			errorMsg = 'Failed to load sample image';
		}
	}

	function dismissError() {
		errorMsg = '';
	}
</script>

<svelte:head>
	<title>Analemma Vision -- Visualize the Sun's Path</title>
	<meta
		name="description"
		content="Upload a sky photo and overlay the sun's yearly analemma figure-eight path. Powered by Astropy and JPL ephemeris data."
	/>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
	<!-- Error banner -->
	{#if errorMsg}
		<div
			class="mb-4 bg-rose-900/40 border border-rose-700 text-rose-200 px-4 py-3 rounded-lg flex items-center justify-between"
		>
			<p class="text-sm">{errorMsg}</p>
			<button
				onclick={dismissError}
				class="text-rose-300 hover:text-rose-100 cursor-pointer ml-4"
				aria-label="Dismiss error"
			>
				<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>
	{/if}

	<!-- Main split panel -->
	<div class="flex flex-col lg:flex-row gap-6">
		<!-- Left panel: Image / Viewer (60%) -->
		<div class="lg:w-3/5 min-w-0">
			{#if analemmaResult && previewUrl}
				<AnalemmaViewer {previewUrl} analemmaData={analemmaResult} />
			{:else if isAnalyzing}
				<div class="relative">
					{#if previewUrl}
						<img src={previewUrl} alt="Processing" class="w-full rounded-lg opacity-50" />
					{/if}
					<div
						class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/60 rounded-lg"
					>
						<svg
							class="animate-spin h-10 w-10 text-amber-400 mb-3"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
							></path>
						</svg>
						<p class="text-slate-200 font-medium">Calculating analemma...</p>
						<p class="text-slate-400 text-sm mt-1">This may take a few seconds</p>
					</div>
				</div>
			{:else if previewUrl}
				<ImageUpload {onFileSelected} bind:previewUrl />
			{:else}
				<div class="lg:hidden">
					<ImageUpload {onFileSelected} bind:previewUrl />
				</div>
				<div class="hidden lg:flex items-center justify-center bg-slate-800/50 rounded-xl border border-slate-700 min-h-[400px]">
					<div class="text-center px-8">
						<svg
							class="h-16 w-16 text-slate-600 mx-auto mb-4"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="1"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z"
							/>
						</svg>
						<p class="text-slate-400">Upload a photo or select a sample to get started</p>
					</div>
				</div>
			{/if}
		</div>

		<!-- Right panel: Controls (40%) -->
		<div class="lg:w-2/5 space-y-5">
			<!-- Upload (desktop only when no image) -->
			{#if !previewUrl}
				<div class="hidden lg:block">
					<ImageUpload {onFileSelected} bind:previewUrl />
				</div>
			{:else}
				<!-- Change image button on desktop -->
				<div class="hidden lg:block">
					<ImageUpload {onFileSelected} bind:previewUrl />
				</div>
			{/if}

			<!-- Metadata form -->
			<div class="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
				<h2 class="text-sm font-semibold text-slate-200 mb-4">Photo Metadata</h2>
				<MetadataForm {exifData} {imageWidth} {imageHeight} bind:metadata />
			</div>

			<!-- Generate button -->
			<button
				type="button"
				onclick={generate}
				disabled={!canGenerate || isAnalyzing}
				class="w-full bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-900 font-semibold py-3 px-4 rounded-lg cursor-pointer transition-colors"
			>
				{#if isAnalyzing}
					Generating...
				{:else}
					Generate Analemma
				{/if}
			</button>

			<!-- Download button -->
			{#if analemmaResult}
				<DownloadButton {buildFormData} />

				<!-- Result metadata -->
				<div class="bg-slate-800/50 rounded-xl border border-slate-700 p-4 text-sm space-y-1">
					<p class="text-slate-400">
						<span class="text-slate-300">{analemmaResult.points.length}</span> sun positions plotted
					</p>
					<p class="text-slate-400">
						Timezone: <span class="text-slate-300">{analemmaResult.metadata.timezone}</span>
					</p>
					<p class="text-slate-400">
						Time of day: <span class="text-slate-300">{analemmaResult.metadata.time_of_day}</span>
					</p>
				</div>
			{/if}
		</div>
	</div>

	<!-- Sample Gallery -->
	<SampleGallery {onSampleSelected} />
</div>
