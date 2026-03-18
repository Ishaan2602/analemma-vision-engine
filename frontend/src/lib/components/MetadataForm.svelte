<script lang="ts">
	import type { ExifData } from '$lib/utils/exif';
	import {
		sensorFromExif,
		sensorFromDatabase,
		type SensorSize
	} from '$lib/utils/sensorLookup';
	import LocationSearch from './LocationSearch.svelte';

	interface Props {
		exifData: ExifData | null;
		imageWidth?: number;
		imageHeight?: number;
		metadata: MetadataFields;
	}

	export interface MetadataFields {
		latitude: string;
		longitude: string;
		datetime: string;
		focalLength: string;
		sensorWidth: string;
		sensorHeight: string;
		sunX: string;
		sunY: string;
	}

	let { exifData, imageWidth, imageHeight, metadata = $bindable() }: Props = $props();

	let locationMode = $state<'search' | 'manual'>('search');
	let locationName = $state('');
	let sensorSource = $state<'exif' | 'database' | 'manual' | ''>('');
	let cameraLabel = $state('');
	let showSunPosition = $state(false);

	// Track whether we've already auto-filled from this EXIF data
	let lastExifRef: ExifData | null = null;

	$effect(() => {
		if (exifData && exifData !== lastExifRef) {
			lastExifRef = exifData;
			applyExif(exifData);
		}
	});

	async function applyExif(exif: ExifData) {
		if (exif.datetime) metadata.datetime = exif.datetime;
		if (exif.latitude != null && exif.longitude != null) {
			metadata.latitude = String(exif.latitude);
			metadata.longitude = String(exif.longitude);
			locationMode = 'manual';
		}
		if (exif.focalLength) metadata.focalLength = String(exif.focalLength);

		// 3-tier sensor detection
		let sensor: SensorSize | null = null;

		// Tier 1: EXIF crop factor
		if (exif.focalLength && exif.focalLength35mm) {
			sensor = sensorFromExif(
				exif.focalLength,
				exif.focalLength35mm,
				exif.imageWidth,
				exif.imageHeight
			);
		}

		// Tier 2: Database lookup
		if (!sensor && (exif.make || exif.model)) {
			sensor = await sensorFromDatabase(
				exif.make || '',
				exif.model || '',
				exif.imageWidth,
				exif.imageHeight
			);
		}

		if (sensor) {
			metadata.sensorWidth = String(sensor.width);
			metadata.sensorHeight = String(sensor.height);
			sensorSource = sensor.source;
			if (exif.make || exif.model) {
				cameraLabel = [exif.make, exif.model].filter(Boolean).join(' ');
			}
		}
	}

	function onLocationSelected(lat: number, lon: number, displayName: string) {
		metadata.latitude = String(lat);
		metadata.longitude = String(lon);
		locationName = displayName;
	}
</script>

<div class="space-y-4">
	<!-- Location -->
	<fieldset class="space-y-2">
		<div class="flex items-center justify-between">
			<legend class="text-sm font-medium text-slate-300">Location</legend>
			<button
				type="button"
				class="text-xs text-amber-400 hover:text-amber-300 cursor-pointer"
				onclick={() => {
					locationMode = locationMode === 'search' ? 'manual' : 'search';
				}}
			>
				{locationMode === 'search' ? 'Enter coordinates' : 'Search location'}
			</button>
		</div>

		{#if locationMode === 'search'}
			<LocationSearch {onLocationSelected} />
			{#if locationName}
				<p class="text-xs text-slate-400 flex items-center gap-1">
					<span class="text-emerald-400">&#10003;</span>
					{locationName}
				</p>
			{/if}
		{:else}
			<div class="grid grid-cols-2 gap-2">
				<label class="block">
					<span class="text-xs text-slate-400">Latitude</span>
					<input
						type="number"
						step="any"
						min="-90"
						max="90"
						bind:value={metadata.latitude}
						placeholder="e.g. 58.37"
						class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
					/>
				</label>
				<label class="block">
					<span class="text-xs text-slate-400">Longitude</span>
					<input
						type="number"
						step="any"
						min="-180"
						max="180"
						bind:value={metadata.longitude}
						placeholder="e.g. 11.45"
						class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
					/>
				</label>
			</div>
			{#if metadata.latitude && metadata.longitude}
				<p class="text-xs text-slate-400 flex items-center gap-1">
					<span class="text-emerald-400">&#10003;</span>
					{metadata.latitude}, {metadata.longitude}
				</p>
			{/if}
		{/if}
	</fieldset>

	<!-- Date/Time -->
	<label class="block space-y-1">
		<span class="text-sm font-medium text-slate-300">Date & Time</span>
		<input
			type="datetime-local"
			bind:value={metadata.datetime}
			class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400"
		/>
		{#if metadata.datetime && exifData?.datetime}
			<p class="text-xs text-slate-400 flex items-center gap-1">
				<span class="text-emerald-400">&#10003;</span> From EXIF
			</p>
		{/if}
	</label>

	<!-- Focal Length -->
	<label class="block space-y-1">
		<span class="text-sm font-medium text-slate-300">Focal Length (mm)</span>
		<input
			type="number"
			step="any"
			min="1"
			bind:value={metadata.focalLength}
			placeholder="e.g. 17.4"
			class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400"
		/>
		{#if metadata.focalLength && exifData?.focalLength}
			<p class="text-xs text-slate-400 flex items-center gap-1">
				<span class="text-emerald-400">&#10003;</span> From EXIF
			</p>
		{/if}
	</label>

	<!-- Sensor Size -->
	<fieldset class="space-y-1">
		<div class="flex items-center gap-2">
			<legend class="text-sm font-medium text-slate-300">Sensor Size (mm)</legend>
			{#if sensorSource}
				<span
					class="text-xs px-1.5 py-0.5 rounded {sensorSource === 'exif'
						? 'bg-emerald-900 text-emerald-300'
						: 'bg-sky-900 text-sky-300'}"
				>
					{sensorSource === 'exif' ? 'From EXIF' : 'From database'}
				</span>
			{/if}
		</div>
		{#if cameraLabel}
			<p class="text-xs text-slate-400">{cameraLabel}</p>
		{/if}
		<div class="grid grid-cols-2 gap-2">
			<label class="block">
				<span class="text-xs text-slate-400">Width</span>
				<input
					type="number"
					step="any"
					min="1"
					bind:value={metadata.sensorWidth}
					placeholder="e.g. 36"
					class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
				/>
			</label>
			<label class="block">
				<span class="text-xs text-slate-400">Height</span>
				<input
					type="number"
					step="any"
					min="1"
					bind:value={metadata.sensorHeight}
					placeholder="e.g. 24"
					class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
				/>
			</label>
		</div>
	</fieldset>

	<!-- Sun Position (optional) -->
	<div>
		<button
			type="button"
			class="text-sm text-slate-400 hover:text-slate-300 cursor-pointer flex items-center gap-1"
			onclick={() => {
				showSunPosition = !showSunPosition;
			}}
		>
			<svg
				class="h-4 w-4 transition-transform {showSunPosition ? 'rotate-90' : ''}"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
				stroke-width="2"
			>
				<path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
			</svg>
			Sun Position (optional)
		</button>
		{#if showSunPosition}
			<div class="grid grid-cols-2 gap-2 mt-2">
				<label class="block">
					<span class="text-xs text-slate-400">X pixel</span>
					<input
						type="number"
						min="0"
						max={imageWidth ?? 99999}
						bind:value={metadata.sunX}
						placeholder="auto"
						class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
					/>
				</label>
				<label class="block">
					<span class="text-xs text-slate-400">Y pixel</span>
					<input
						type="number"
						min="0"
						max={imageHeight ?? 99999}
						bind:value={metadata.sunY}
						placeholder="auto"
						class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-amber-400 mt-0.5"
					/>
				</label>
			</div>
			<p class="text-xs text-slate-500 mt-1">
				Leave blank to auto-detect. Specify if the sun isn't visible or detection fails.
			</p>
		{/if}
	</div>
</div>
