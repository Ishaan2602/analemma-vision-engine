<script lang="ts">
	import { renderOverlay } from '$lib/utils/api';

	interface Props {
		buildFormData: () => FormData | null;
		disabled?: boolean;
	}

	let { buildFormData, disabled = false }: Props = $props();

	let rendering = $state(false);
	let errorMsg = $state('');

	async function download() {
		errorMsg = '';
		const formData = buildFormData();
		if (!formData) return;

		rendering = true;
		try {
			const blob = await renderOverlay(formData);
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'analemma_overlay.png';
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		} catch (err) {
			errorMsg = err instanceof Error ? err.message : 'Download failed';
		} finally {
			rendering = false;
		}
	}
</script>

<div>
	<button
		type="button"
		onclick={download}
		disabled={disabled || rendering}
		class="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-slate-100 font-medium py-2.5 px-4 rounded-lg cursor-pointer transition-colors"
	>
		{#if rendering}
			<svg
				class="animate-spin h-4 w-4"
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
			Rendering...
		{:else}
			<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
				/>
			</svg>
			Download Overlay
		{/if}
	</button>

	{#if errorMsg}
		<p class="text-rose-400 text-xs mt-1">{errorMsg}</p>
	{/if}
</div>
