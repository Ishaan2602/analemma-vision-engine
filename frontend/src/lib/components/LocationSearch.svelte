<script lang="ts">
	import { autocomplete, type GeocodingResult } from '$lib/utils/geocoding';

	interface Props {
		onLocationSelected: (lat: number, lon: number, displayName: string) => void;
		initialValue?: string;
	}

	let { onLocationSelected, initialValue = '' }: Props = $props();

	let query = $state(initialValue); // eslint-disable-line
	let results = $state<GeocodingResult[]>([]);
	let isOpen = $state(false);
	let loading = $state(false);
	let activeIndex = $state(-1);
	let debounceTimer: ReturnType<typeof setTimeout> | undefined;

	function onInput() {
		activeIndex = -1;
		if (debounceTimer) clearTimeout(debounceTimer);
		if (query.length < 3) {
			results = [];
			isOpen = false;
			return;
		}
		loading = true;
		debounceTimer = setTimeout(async () => {
			results = await autocomplete(query);
			isOpen = results.length > 0;
			loading = false;
		}, 300);
	}

	function selectResult(result: GeocodingResult) {
		query = result.displayName;
		isOpen = false;
		onLocationSelected(result.latitude, result.longitude, result.displayName);
	}

	function onKeydown(e: KeyboardEvent) {
		if (!isOpen) return;
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			activeIndex = Math.min(activeIndex + 1, results.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			activeIndex = Math.max(activeIndex - 1, 0);
		} else if (e.key === 'Enter' && activeIndex >= 0) {
			e.preventDefault();
			selectResult(results[activeIndex]);
		} else if (e.key === 'Escape') {
			isOpen = false;
		}
	}

	function onBlur() {
		// Delay to allow click on result
		setTimeout(() => {
			isOpen = false;
		}, 200);
	}
</script>

<div class="relative">
	<div class="relative">
		<input
			type="text"
			bind:value={query}
			oninput={onInput}
			onkeydown={onKeydown}
			onblur={onBlur}
			onfocus={() => {
				if (results.length > 0) isOpen = true;
			}}
			placeholder="Search for a city..."
			class="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-slate-100 placeholder-slate-400 text-sm focus:outline-none focus:border-amber-400 transition-colors"
		/>
		{#if loading}
			<svg
				class="absolute right-2 top-2.5 animate-spin h-4 w-4 text-slate-400"
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
		{/if}
	</div>

	{#if isOpen}
		<ul
			class="absolute z-50 mt-1 w-full bg-slate-700 border border-slate-600 rounded-md shadow-lg max-h-60 overflow-auto"
		>
			{#each results as result, i}
				<li>
					<button
						type="button"
						class="w-full text-left px-3 py-2 text-sm cursor-pointer transition-colors {i ===
						activeIndex
							? 'bg-amber-400/20 text-amber-200'
							: 'text-slate-200 hover:bg-slate-600'}"
						onmousedown={() => selectResult(result)}
					>
						{result.displayName}
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</div>
