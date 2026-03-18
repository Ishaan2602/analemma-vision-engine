<script lang="ts">
	import type { AnalyzeResponse } from '$lib/utils/api';
	import { cubicInOut } from 'svelte/easing';

	interface Props {
		previewUrl: string;
		analemmaData: AnalyzeResponse;
	}

	let { previewUrl, analemmaData }: Props = $props();

	let showOverlay = $state(false);
	let animKey = $state(0);

	// Sort points chronologically and build path
	let sortedPoints = $derived(
		[...analemmaData.points].sort(
			(a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
		)
	);

	let curvePath = $derived.by(() => {
		if (sortedPoints.length === 0) return '';
		// Break path into segments to avoid lines across gaps where the
		// analemma exits and re-enters the image bounds.
		// Compute median spacing to set a gap threshold.
		const dists: number[] = [];
		for (let i = 1; i < sortedPoints.length; i++) {
			const dx = sortedPoints[i].pixel_x - sortedPoints[i - 1].pixel_x;
			const dy = sortedPoints[i].pixel_y - sortedPoints[i - 1].pixel_y;
			dists.push(Math.sqrt(dx * dx + dy * dy));
		}
		dists.sort((a, b) => a - b);
		const median = dists.length > 0 ? dists[Math.floor(dists.length / 2)] : 0;
		const gapThreshold = Math.max(median * 4, analemmaData.image_width * 0.05);

		const parts: string[] = [];
		let seg = `M ${sortedPoints[0].pixel_x},${sortedPoints[0].pixel_y}`;
		for (let i = 1; i < sortedPoints.length; i++) {
			const dx = sortedPoints[i].pixel_x - sortedPoints[i - 1].pixel_x;
			const dy = sortedPoints[i].pixel_y - sortedPoints[i - 1].pixel_y;
			const dist = Math.sqrt(dx * dx + dy * dy);
			if (dist > gapThreshold) {
				parts.push(seg);
				seg = `M ${sortedPoints[i].pixel_x},${sortedPoints[i].pixel_y}`;
			} else {
				seg += ` L ${sortedPoints[i].pixel_x},${sortedPoints[i].pixel_y}`;
			}
		}
		parts.push(seg);
		return parts.join(' ');
	});

	let dotRadius = $derived(Math.max(2, Math.min(5, analemmaData.image_width / 600)));

	// Labels every ~30 days
	let labeledPoints = $derived(() => {
		if (sortedPoints.length === 0) return [];
		const labels: Array<{
			pixel_x: number;
			pixel_y: number;
			dateLabel: string;
		}> = [];
		const months = [
			'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
			'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
		];
		let lastLabel = -Infinity;
		for (const p of sortedPoints) {
			const d = new Date(p.date);
			const dayOfYear = Math.floor(
				(d.getTime() - new Date(d.getFullYear(), 0, 0).getTime()) / 86400000
			);
			if (dayOfYear - lastLabel >= 28) {
				labels.push({
					pixel_x: p.pixel_x,
					pixel_y: p.pixel_y,
					dateLabel: `${months[d.getMonth()]} ${d.getDate()}`
				});
				lastLabel = dayOfYear;
			}
		}
		return labels;
	});

	// Hover tooltip
	let hoveredPoint = $state<{
		x: number;
		y: number;
		date: string;
		altitude: number;
		azimuth: number;
	} | null>(null);
	let containerEl: HTMLDivElement | undefined = $state();

	function onSvgMouseMove(e: MouseEvent) {
		if (!containerEl) return;
		const svg = containerEl.querySelector('svg');
		if (!svg) return;
		const rect = svg.getBoundingClientRect();
		const scaleX = analemmaData.image_width / rect.width;
		const scaleY = analemmaData.image_height / rect.height;
		const mx = (e.clientX - rect.left) * scaleX;
		const my = (e.clientY - rect.top) * scaleY;

		let closest: (typeof sortedPoints)[0] | null = null;
		let minDist = Infinity;
		const threshold = analemmaData.image_width * 0.02;
		for (const p of sortedPoints) {
			const dx = p.pixel_x - mx;
			const dy = p.pixel_y - my;
			const dist = Math.sqrt(dx * dx + dy * dy);
			if (dist < minDist && dist < threshold) {
				minDist = dist;
				closest = p;
			}
		}

		if (closest) {
			const d = new Date(closest.date);
			hoveredPoint = {
				x: e.clientX - rect.left,
				y: e.clientY - rect.top,
				date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
				altitude: closest.altitude,
				azimuth: closest.azimuth
			};
		} else {
			hoveredPoint = null;
		}
	}

	function onSvgMouseLeave() {
		hoveredPoint = null;
	}

	function replay() {
		showOverlay = false;
		animKey++;
		// Tick to reset DOM, then show again
		requestAnimationFrame(() => {
			showOverlay = true;
		});
	}

	// SVG draw transition (pure JS, not Svelte transition directive since we need path animation)
	let pathEl: SVGPathElement | undefined = $state();

	$effect(() => {
		if (showOverlay && pathEl && curvePath) {
			const _ = animKey; // depend on animKey for replay
			const length = pathEl.getTotalLength();
			pathEl.style.strokeDasharray = `${length}`;
			pathEl.style.strokeDashoffset = `${length}`;
			pathEl.getBoundingClientRect(); // force reflow

			const duration = 3000;
			const start = performance.now();
			function animate(now: number) {
				const elapsed = now - start;
				const t = Math.min(elapsed / duration, 1);
				const eased = cubicInOut(t);
				if (pathEl) {
					pathEl.style.strokeDashoffset = `${length * (1 - eased)}`;
				}
				if (t < 1) requestAnimationFrame(animate);
			}
			requestAnimationFrame(animate);
		}
	});

	// Auto-show overlay on mount
	$effect(() => {
		if (analemmaData && !showOverlay) {
			showOverlay = true;
		}
	});

	let isSaving = $state(false);

	async function saveImage() {
		if (!containerEl) return;
		isSaving = true;
		try {
			const img = containerEl.querySelector('img') as HTMLImageElement;
			const svg = containerEl.querySelector('svg');
			if (!img || !svg) return;

			const w = analemmaData.image_width;
			const h = analemmaData.image_height;

			const canvas = document.createElement('canvas');
			canvas.width = w;
			canvas.height = h;
			const ctx = canvas.getContext('2d')!;

			// Draw the background image
			ctx.drawImage(img, 0, 0, w, h);

			// Serialize the SVG and draw it onto canvas
			const svgClone = svg.cloneNode(true) as SVGSVGElement;
			// Remove animations and set final opacity on all animated elements
			svgClone.querySelectorAll('animate').forEach((anim) => {
				const parent = anim.parentElement;
				if (parent) {
					const toVal = anim.getAttribute('to');
					if (toVal && anim.getAttribute('attributeName') === 'opacity') {
						parent.setAttribute('opacity', toVal);
					}
					anim.remove();
				}
			});
			// Remove dash animation from path
			const pathClone = svgClone.querySelector('path');
			if (pathClone) {
				pathClone.style.strokeDasharray = '';
				pathClone.style.strokeDashoffset = '';
			}

			const svgData = new XMLSerializer().serializeToString(svgClone);
			const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
			const svgUrl = URL.createObjectURL(svgBlob);

			const svgImg = new Image();
			await new Promise<void>((resolve, reject) => {
				svgImg.onload = () => resolve();
				svgImg.onerror = () => reject(new Error('SVG render failed'));
				svgImg.src = svgUrl;
			});
			ctx.drawImage(svgImg, 0, 0, w, h);
			URL.revokeObjectURL(svgUrl);

			canvas.toBlob((blob) => {
				if (!blob) return;
				const url = URL.createObjectURL(blob);
				// On mobile, open in new tab for long-press save
				// On desktop, trigger download
				const a = document.createElement('a');
				a.href = url;
				a.download = 'analemma_overlay.png';
				a.click();
				// Also open in new tab as fallback for mobile
				if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
					window.open(url, '_blank');
				} else {
					setTimeout(() => URL.revokeObjectURL(url), 5000);
				}
			}, 'image/png');
		} finally {
			isSaving = false;
		}
	}
</script>

<div class="relative" bind:this={containerEl}>
	<img src={previewUrl} alt="Sky photo" class="w-full rounded-lg" />

	{#if showOverlay}
		{#key animKey}
			<svg
				viewBox="0 0 {analemmaData.image_width} {analemmaData.image_height}"
				class="absolute inset-0 w-full h-full rounded-lg"
				onmousemove={onSvgMouseMove}
				onmouseleave={onSvgMouseLeave}
				role="img"
				aria-label="Analemma curve overlay"
			>
				<!-- Connecting curve -->
				<path
					bind:this={pathEl}
					d={curvePath}
					stroke="#fbbf24"
					stroke-width={Math.max(1, analemmaData.image_width / 1200)}
					fill="none"
					opacity="0.8"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>

				<!-- Sun position dots -->
				{#each sortedPoints as point, i}
					<circle
						cx={point.pixel_x}
						cy={point.pixel_y}
						r={dotRadius}
						fill="#fbbf24"
						opacity="0"
					>
						<animate
							attributeName="opacity"
							from="0"
							to="0.7"
							dur="0.15s"
							begin="{3 + i * 0.015}s"
							fill="freeze"
						/>
					</circle>
				{/each}

				<!-- Anchor point -->
				<circle
					cx={analemmaData.anchor_point.pixel_x}
					cy={analemmaData.anchor_point.pixel_y}
					r={dotRadius * 2}
					fill="#ef4444"
					stroke="white"
					stroke-width={Math.max(1, analemmaData.image_width / 2000)}
					opacity="0"
				>
					<animate
						attributeName="opacity"
						from="0"
						to="1"
						dur="0.3s"
						begin="3s"
						fill="freeze"
					/>
				</circle>

				<!-- Date labels -->
				{#each labeledPoints() as lp}
					<text
						x={lp.pixel_x + dotRadius * 3}
						y={lp.pixel_y + dotRadius}
						fill="white"
						font-size={Math.max(10, analemmaData.image_width / 250)}
						font-weight="500"
						style="text-shadow: 1px 1px 3px rgba(0,0,0,0.9), -1px -1px 3px rgba(0,0,0,0.9);"
						opacity="0"
					>
						{lp.dateLabel}
						<animate
							attributeName="opacity"
							from="0"
							to="0.85"
							dur="0.3s"
							begin="4.5s"
							fill="freeze"
						/>
					</text>
				{/each}
			</svg>
		{/key}
	{/if}

	<!-- Hover tooltip -->
	{#if hoveredPoint}
		<div
			class="absolute pointer-events-none bg-slate-900/90 text-slate-100 text-xs px-2 py-1 rounded shadow-lg border border-slate-600"
			style="left: {hoveredPoint.x + 12}px; top: {hoveredPoint.y - 8}px;"
		>
			{hoveredPoint.date} | Alt: {hoveredPoint.altitude.toFixed(1)}&#176; | Az: {hoveredPoint.azimuth.toFixed(1)}&#176;
		</div>
	{/if}

	<!-- Replay + Save buttons -->
	{#if showOverlay}
		<div class="absolute top-3 right-3 flex gap-2">
			<button
				onclick={saveImage}
				disabled={isSaving}
				class="bg-slate-800/80 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs px-2.5 py-1.5 rounded-md backdrop-blur-sm cursor-pointer transition-colors flex items-center gap-1"
			>
				<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
				</svg>
				{isSaving ? 'Saving...' : 'Save'}
			</button>
			<button
				onclick={replay}
				class="bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-md backdrop-blur-sm cursor-pointer transition-colors flex items-center gap-1"
			>
				<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
				Replay
			</button>
		</div>
	{/if}
</div>
