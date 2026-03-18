<script lang="ts">
	interface Props {
		previewUrl: string;
		imageWidth: number;
		imageHeight: number;
		onConfirm: (x: number, y: number) => void;
		onCancel: () => void;
	}

	let { previewUrl, imageWidth, imageHeight, onConfirm, onCancel }: Props = $props();

	let selectedX: number | null = $state(null);
	let selectedY: number | null = $state(null);
	let markerDisplayX = $state(0);
	let markerDisplayY = $state(0);
	let imgEl: HTMLImageElement | undefined = $state();

	function onImageClick(e: MouseEvent) {
		if (!imgEl) return;
		const rect = imgEl.getBoundingClientRect();
		const clickX = e.clientX - rect.left;
		const clickY = e.clientY - rect.top;

		// Convert display coordinates to natural image pixel coordinates
		selectedX = Math.round((clickX / rect.width) * imageWidth);
		selectedY = Math.round((clickY / rect.height) * imageHeight);

		// Store display coords for marker positioning
		markerDisplayX = clickX;
		markerDisplayY = clickY;
	}

	function confirm() {
		if (selectedX != null && selectedY != null) {
			onConfirm(selectedX, selectedY);
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onCancel();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Modal backdrop -->
<div
	class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 p-4"
	role="dialog"
	aria-modal="true"
	aria-label="Select sun position"
>
	<!-- Header -->
	<div class="text-center mb-3">
		<h3 class="text-lg font-semibold text-slate-100">Click on the center of the sun</h3>
		{#if selectedX != null && selectedY != null}
			<p class="text-sm text-slate-400 mt-1">
				Selected: ({selectedX}, {selectedY}) -- click again to reposition
			</p>
		{:else}
			<p class="text-sm text-slate-400 mt-1">Click anywhere on the image to mark the sun's position</p>
		{/if}
	</div>

	<!-- Image container -->
	<!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div class="relative max-w-full max-h-[70vh] overflow-hidden flex-shrink-0">
		<img
			bind:this={imgEl}
			src={previewUrl}
			alt="Select sun position"
			class="max-w-full max-h-[70vh] object-contain cursor-crosshair rounded-lg"
			onclick={onImageClick}
			role="button"
			tabindex="0"
		/>

		<!-- Marker overlay -->
		{#if selectedX != null && imgEl}
			<div
				class="absolute pointer-events-none"
				style="left: {markerDisplayX}px; top: {markerDisplayY}px; transform: translate(-50%, -50%);"
			>
				<!-- Crosshair lines -->
				<div class="absolute w-6 h-px bg-red-500 -left-3 top-0"></div>
				<div class="absolute h-6 w-px bg-red-500 left-0 -top-3"></div>
				<!-- Center dot -->
				<div class="absolute w-3 h-3 border-2 border-red-500 rounded-full -left-1.5 -top-1.5 bg-red-500/30"></div>
			</div>
		{/if}
	</div>

	<!-- Buttons -->
	<div class="flex gap-3 mt-4">
		<button
			onclick={onCancel}
			class="px-5 py-2 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-700 cursor-pointer transition-colors text-sm"
		>
			Cancel
		</button>
		<button
			onclick={confirm}
			disabled={selectedX == null}
			class="px-5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-900 font-semibold cursor-pointer transition-colors text-sm"
		>
			Confirm Position
		</button>
	</div>
</div>
