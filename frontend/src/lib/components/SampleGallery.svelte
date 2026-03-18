<script lang="ts">
	import { SAMPLE_IMAGES, type SampleImageData } from '$lib/data/samples';

	interface Props {
		onSampleSelected: (sample: SampleImageData) => void;
	}

	let { onSampleSelected }: Props = $props();
</script>

<section class="mt-8">
	<h2 class="text-lg font-semibold text-slate-200 mb-3">Sample Images</h2>
	<p class="text-sm text-slate-400 mb-4">
		Try these Creative Commons photos to see the analemma engine in action.
	</p>

	<div class="flex gap-4 overflow-x-auto pb-3 -mx-2 px-2 snap-x snap-mandatory">
		{#each SAMPLE_IMAGES as sample}
			<div
				class="flex-none w-56 bg-slate-800 rounded-lg overflow-hidden border border-slate-700 snap-start"
			>
				<img
					src={sample.thumbnail}
					alt={sample.name}
					class="w-full h-32 object-cover"
					loading="lazy"
				/>
				<div class="p-3">
					<p class="text-sm font-medium text-slate-200 truncate">{sample.name}</p>
					<p class="text-xs text-slate-400 mt-0.5">{sample.author}</p>
					<div class="flex items-center justify-between mt-2">
						<span class="text-[10px] text-slate-500 bg-slate-700/50 px-1.5 py-0.5 rounded">
							{sample.license}
						</span>
						<button
							type="button"
							class="text-xs text-amber-400 hover:text-amber-300 font-medium cursor-pointer"
							onclick={() => onSampleSelected(sample)}
						>
							Try it
						</button>
					</div>
				</div>
			</div>
		{/each}
	</div>
</section>
