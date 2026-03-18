<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';

	let { children } = $props();

	const tabs = [
		{ href: '/', label: 'App' },
		{ href: '/about', label: 'About' },
		{ href: '/methodology', label: 'Methodology' }
	] as const;
</script>

<div class="min-h-screen flex flex-col">
	<header class="border-b border-slate-800 px-6 py-4">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<div>
				<h1 class="text-xl font-bold text-slate-50">
					<span class="text-amber-400">Analemma</span> Vision
				</h1>
				<p class="text-xs text-slate-400 mt-0.5">
					Visualize the sun's yearly path on any sky photo
				</p>
			</div>
			<div class="flex items-center gap-6">
				<nav class="hidden sm:flex items-center gap-1">
					{#each tabs as tab}
						<a
							href={tab.href}
							class="px-3 py-1.5 rounded-md text-sm transition-colors {page.url.pathname === tab.href ? 'bg-amber-500/20 text-amber-400 font-medium' : 'text-slate-400 hover:text-slate-200'}"
						>
							{tab.label}
						</a>
					{/each}
				</nav>
				<a
					href="https://github.com/Ishaan2602/analemma-vision-engine"
					target="_blank"
					rel="noopener noreferrer"
					class="text-slate-400 hover:text-slate-200 transition-colors"
					aria-label="GitHub repository"
				>
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
						<path
							d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
						/>
					</svg>
				</a>
			</div>
		</div>
		<!-- Mobile nav -->
		<nav class="sm:hidden flex items-center gap-1 mt-3 -mb-1">
			{#each tabs as tab}
				<a
					href={tab.href}
					class="px-3 py-1.5 rounded-md text-sm transition-colors {page.url.pathname === tab.href ? 'bg-amber-500/20 text-amber-400 font-medium' : 'text-slate-400 hover:text-slate-200'}"
				>
					{tab.label}
				</a>
			{/each}
		</nav>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="border-t border-slate-800 px-6 py-4 text-center text-xs text-slate-500">
		<p>Built with the Analemma Engine -- Astropy + JPL DE440 ephemeris</p>
	</footer>
</div>
