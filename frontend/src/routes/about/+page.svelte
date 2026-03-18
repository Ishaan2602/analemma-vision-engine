<svelte:head>
	<title>About the Analemma -- Analemma Vision</title>
	<meta name="description" content="What is an analemma, why does it happen, and what makes it different at various locations on Earth." />
</svelte:head>

<div class="max-w-3xl mx-auto px-4 sm:px-6 py-10 text-slate-300 space-y-10">
	<header>
		<h1 class="text-3xl font-bold text-slate-50 mb-2">What is an Analemma?</h1>
		<p class="text-slate-400">The figure-eight the sun traces in the sky over a year</p>
	</header>

	<section class="space-y-4">
		<p>
			If you photograph the sun from the same spot, at the same time of day, every week for an
			entire year, the sun won't be in the same place. Instead, it traces a tall, narrow figure-eight
			shape called an <strong class="text-slate-100">analemma</strong>.
		</p>
		<p>
			It's one of those things that seems wrong at first -- intuitively, the sun "should" be in
			the same place at noon every day. But the Earth's orbit isn't circular, and its axis is
			tilted, and those two facts combine to produce this distinctive pattern.
		</p>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Why does it happen?</h2>
		<p>
			Two factors drive the analemma's shape:
		</p>
		<ul class="list-disc list-inside space-y-2 ml-2 text-slate-300">
			<li>
				<strong class="text-slate-100">Axial tilt (obliquity):</strong> Earth's axis is tilted about
				23.44 degrees relative to its orbital plane. This causes the sun's declination to oscillate
				between +23.44 and -23.44 degrees over a year -- high in summer, low in winter. This
				produces the vertical spread of the analemma.
			</li>
			<li>
				<strong class="text-slate-100">Orbital eccentricity:</strong> Earth's orbit is slightly
				elliptical. It moves faster near perihelion (early January) and slower near aphelion (early
				July). This means the sun isn't exactly where a "mean sun" clock predicts. The difference is
				called the Equation of Time, and it shifts the sun east or west of its mean position,
				creating the horizontal width and the asymmetry of the figure-eight.
			</li>
		</ul>
		<p>
			Neither effect alone produces a figure-eight. Axial tilt alone gives a vertical line. Eccentricity
			alone gives a horizontal oscillation. Together, they form the asymmetric loop -- the top lobe is
			typically smaller than the bottom because perihelion and solstice don't coincide.
		</p>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Does it look the same everywhere?</h2>
		<p>
			No. The analemma's shape is the same from anywhere on Earth (it's determined by orbital
			mechanics, not geography), but its <em>orientation and position in the sky</em> change
			dramatically with latitude and time of day.
		</p>
		<ul class="list-disc list-inside space-y-2 ml-2 text-slate-300">
			<li>
				At the <strong class="text-slate-100">equator at noon</strong>, the analemma stands nearly
				vertical, centered high overhead.
			</li>
			<li>
				At <strong class="text-slate-100">mid-northern latitudes</strong> (like 40 N), a noon
				analemma tilts south and appears in the southern sky.
			</li>
			<li>
				Photographed at <strong class="text-slate-100">sunrise or sunset</strong>, the analemma tilts
				strongly sideways and may partially dip below the horizon.
			</li>
			<li>
				In the <strong class="text-slate-100">southern hemisphere</strong>, the figure-eight is
				inverted -- the larger lobe is on top.
			</li>
		</ul>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Do other planets have analemmas?</h2>
		<p>
			Yes, but they look different. Mars has a teardrop shape because its orbital eccentricity is
			much larger and its axial tilt is similar to Earth's. A planet with zero axial tilt would
			trace a horizontal line. One with a circular orbit but nonzero tilt would trace a vertical
			figure-eight with equal lobes.
		</p>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">What Analemma Vision does</h2>
		<p>
			This tool computes the sun's position for every week of the year at a given time and
			location using high-precision JPL DE440 ephemeris data via Astropy. It then projects those
			positions onto your photograph using a tangent-plane camera model matched to the photo's
			focal length and sensor dimensions. The result is a precise analemma curve overlaid on your
			actual sky.
		</p>
		<p>
			You can upload any sky photo -- the app detects the sun's position in the image,
			determines the exact camera geometry, and renders the full-year path. If automatic sun
			detection fails, you can select the sun's position manually.
		</p>
	</section>

	<footer class="border-t border-slate-700 pt-6 text-sm text-slate-500">
		<p>
			For the mathematical details behind the projection and computation, see the
			<a href="/methodology" class="text-amber-400 hover:text-amber-300">Methodology</a> page.
		</p>
	</footer>
</div>
