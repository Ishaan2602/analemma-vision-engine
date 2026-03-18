<script lang="ts">
	import { fetchCharts, type ChartsResponse } from '$lib/utils/api';

	interface Props {
		latitude: string;
		longitude: string;
		datetime: string;
	}

	let { latitude, longitude, datetime }: Props = $props();

	let isOpen = $state(false);
	let charts: ChartsResponse | null = $state(null);
	let isLoading = $state(false);
	let error = $state('');
	let fetchedKey = $state('');

	async function toggle() {
		isOpen = !isOpen;
		if (!isOpen) return;

		// Lazy load: fetch only on first open or if params changed
		const key = `${latitude}|${longitude}|${datetime}`;
		if (charts && fetchedKey === key) return;

		error = '';
		isLoading = true;
		try {
			charts = await fetchCharts(latitude, longitude, datetime);
			fetchedKey = key;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load charts';
			charts = null;
		} finally {
			isLoading = false;
		}
	}

	function saveChart(base64: string, filename: string) {
		const a = document.createElement('a');
		a.href = `data:image/png;base64,${base64}`;
		a.download = filename;
		a.click();
	}
</script>

<div class="mt-4">
	<button
		type="button"
		class="w-full flex items-center gap-2 text-sm text-slate-300 hover:text-slate-100 cursor-pointer bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2.5 transition-colors"
		onclick={toggle}
	>
		<svg
			class="h-4 w-4 transition-transform {isOpen ? 'rotate-90' : ''}"
			fill="none"
			viewBox="0 0 24 24"
			stroke="currentColor"
			stroke-width="2"
		>
			<path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
		</svg>
		View Sky Chart & Figure-8
	</button>

	{#if isOpen}
		<div class="mt-3 space-y-4">
			{#if isLoading}
				<div class="flex items-center justify-center py-12">
					<svg
						class="animate-spin h-8 w-8 text-amber-400"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
					>
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
					</svg>
					<p class="text-slate-400 ml-3 text-sm">Generating charts...</p>
				</div>
			{:else if error}
				<p class="text-rose-400 text-sm py-4 text-center">{error}</p>
			{:else if charts}
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Sky Chart -->
					<div class="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
						<img
							src="data:image/png;base64,{charts.sky_chart}"
							alt="Sky Chart - Altitude vs Azimuth"
							class="w-full"
						/>
						<div class="px-3 py-2 flex items-center justify-between">
							<span class="text-xs text-slate-400">Altitude vs Azimuth</span>
							<button
								onclick={() => saveChart(charts!.sky_chart, 'analemma_sky_chart.png')}
								class="text-xs text-amber-400 hover:text-amber-300 cursor-pointer flex items-center gap-1"
							>
								<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
								</svg>
								Save
							</button>
						</div>
					</div>

					<!-- Figure-8 -->
					<div class="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
						<img
							src="data:image/png;base64,{charts.figure8}"
							alt="Analemma Figure-8 - EoT vs Declination"
							class="w-full"
						/>
						<div class="px-3 py-2 flex items-center justify-between">
							<span class="text-xs text-slate-400">EoT vs Declination</span>
							<button
								onclick={() => saveChart(charts!.figure8, 'analemma_figure8.png')}
								class="text-xs text-amber-400 hover:text-amber-300 cursor-pointer flex items-center gap-1"
							>
								<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
								</svg>
								Save
							</button>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
