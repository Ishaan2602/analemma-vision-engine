<script lang="ts">
	import { extractExif, type ExifData } from '$lib/utils/exif';
	import { isHeic, convertHeicToJpeg } from '$lib/utils/heic';

	interface Props {
		onFileSelected: (file: File, exif: ExifData, previewUrl: string) => void;
		previewUrl?: string;
	}

	let { onFileSelected, previewUrl = $bindable() }: Props = $props();

	let dragOver = $state(false);
	let processing = $state(false);
	let errorMsg = $state('');
	let fileInputEl: HTMLInputElement | undefined = $state();

	const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.heic', '.heif', '.png', '.webp'];
	const MAX_SIZE = 30 * 1024 * 1024; // 30MB

	function validateFile(file: File): string | null {
		const ext = '.' + file.name.split('.').pop()?.toLowerCase();
		if (!ALLOWED_EXTENSIONS.includes(ext)) {
			return `Unsupported file type. Accepted: ${ALLOWED_EXTENSIONS.join(', ')}`;
		}
		if (file.size > MAX_SIZE) {
			return `File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Maximum is 30MB.`;
		}
		return null;
	}

	async function handleFile(file: File) {
		errorMsg = '';
		const err = validateFile(file);
		if (err) {
			errorMsg = err;
			return;
		}

		processing = true;
		try {
			const exif = await extractExif(file);

			let url: string;
			if (isHeic(file)) {
				const jpegBlob = await convertHeicToJpeg(file);
				url = URL.createObjectURL(jpegBlob);
			} else {
				url = URL.createObjectURL(file);
			}

			previewUrl = url;
			onFileSelected(file, exif, url);
		} catch {
			errorMsg = 'Failed to process image. Try a different file.';
		} finally {
			processing = false;
		}
	}

	function onDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		const file = e.dataTransfer?.files[0];
		if (file) handleFile(file);
	}

	function onDragOver(e: DragEvent) {
		e.preventDefault();
		dragOver = true;
	}

	function onDragLeave() {
		dragOver = false;
	}

	function onInputChange(e: Event) {
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) handleFile(file);
	}

	function triggerUpload() {
		fileInputEl?.click();
	}
</script>

{#if previewUrl && !processing}
	<div class="relative group">
		<img src={previewUrl} alt="Uploaded photo" class="w-full rounded-lg" />
		<button
			onclick={triggerUpload}
			class="absolute bottom-3 right-3 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-sm px-3 py-1.5 rounded-md backdrop-blur-sm cursor-pointer transition-colors"
		>
			Change Image
		</button>
	</div>
{:else}
	<button
		type="button"
		class="w-full border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors {dragOver
			? 'border-amber-400 bg-amber-400/10'
			: 'border-slate-600 hover:border-slate-400 bg-slate-800/50'}"
		ondrop={onDrop}
		ondragover={onDragOver}
		ondragleave={onDragLeave}
		onclick={triggerUpload}
	>
		{#if processing}
			<div class="flex flex-col items-center gap-3">
				<svg
					class="animate-spin h-8 w-8 text-amber-400"
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
				<span class="text-slate-300 text-sm">Processing image...</span>
			</div>
		{:else}
			<div class="flex flex-col items-center gap-3">
				<svg
					class="h-10 w-10 text-slate-400"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"
					/>
				</svg>
				<div>
					<p class="text-slate-200 font-medium">Drop a sky photo here</p>
					<p class="text-slate-400 text-sm mt-1">or click to browse -- JPEG, HEIC, PNG, WebP (max 30MB)</p>
				</div>
			</div>
		{/if}
	</button>
{/if}

{#if errorMsg}
	<p class="text-rose-400 text-sm mt-2">{errorMsg}</p>
{/if}

<input
	bind:this={fileInputEl}
	type="file"
	accept=".jpg,.jpeg,.heic,.heif,.png,.webp"
	class="hidden"
	onchange={onInputChange}
/>
