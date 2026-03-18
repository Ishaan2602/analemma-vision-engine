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
			entire year, the sun won't be in the same place. It drifts. Over twelve months those
			positions trace out a tall, narrow figure-eight called an
			<strong class="text-slate-100">analemma</strong>.
		</p>
		<p>
			This feels wrong at first. Intuitively the sun "should" be in the same spot at noon
			every day. But the Earth's orbit isn't circular, and its axis is tilted 23.44 degrees
			off vertical, and those two facts together are enough to produce the pattern.
		</p>
		<figure class="my-6">
			<img src="/basicdiagram.png" alt="Diagram showing how the sun traces a figure-eight analemma pattern over a year" class="rounded-lg w-full" />
		</figure>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Why does it happen?</h2>
		<p>
			The figure-eight comes from two independent effects layered on top of each other.
		</p>
		<p>
			<strong class="text-slate-100">Axial tilt</strong> is the more intuitive one. Because
			Earth's rotation axis is tilted relative to its orbital plane, the sun's declination
			(its angular height above or below the celestial equator) swings between +23.44 and
			-23.44 degrees over the course of a year. Higher in summer, lower in winter. That
			oscillation gives the analemma its vertical extent.
		</p>
		<p>
			<strong class="text-slate-100">Orbital eccentricity</strong> is subtler. Earth's orbit
			is slightly elliptical, so it moves faster near perihelion (early January) and slower
			near aphelion (early July). The practical effect is that the sun doesn't cross your local
			meridian at exactly noon every day. The deviation, called the Equation of Time, can be
			as large as 16 minutes. It shifts the sun east or west of where a perfectly regular clock
			would predict, which creates the horizontal width of the figure-eight and makes the two
			lobes asymmetric.
		</p>
		<p>
			Neither effect alone makes a figure-eight. Tilt alone would give you a vertical line;
			eccentricity alone, a horizontal oscillation. It's the combination that produces two
			loops of different sizes, with the top lobe typically smaller because perihelion and the
			winter solstice fall only about two weeks apart.
		</p>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Does it look the same everywhere?</h2>
		<p>
			The shape is identical from anywhere on Earth, since it's entirely determined by orbital
			mechanics. But its <em>orientation and position in the sky</em> change a lot depending
			on where you are and what time of day you're photographing.
		</p>
		<p>
			At the equator around noon, the analemma stands nearly vertical, centered high overhead.
			At mid-northern latitudes (say, 40 N) a noon analemma tilts toward the south. Photograph
			it at sunrise or sunset and the whole thing rotates sideways, sometimes dipping partly
			below the horizon. In the southern hemisphere the larger lobe ends up on top instead of
			the bottom.
		</p>
		<figure class="my-6">
			<img src="/not_all_analemma_same.png" alt="Comparison of how the analemma appears at different latitudes and times of day" class="rounded-lg w-full" />
		</figure>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">Other planets</h2>
		<p>
			Every planet with a tilted axis or an eccentric orbit has some version of an analemma.
			Mars makes a teardrop rather than a figure-eight because its orbit is far more
			eccentric than Earth's. A hypothetical planet with zero tilt would trace a horizontal
			line; one with a perfectly circular orbit but nonzero tilt would give you a symmetric
			figure-eight with equal-sized lobes.
		</p>
		<figure class="my-6">
			<img src="/diffplanets.png" alt="Analemma shapes on different planets" class="rounded-lg w-full" />
		</figure>
	</section>

	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">What this app does</h2>
		<p>
			Analemma Vision computes the sun's position for every day of the year at your chosen
			time and location, using high-precision JPL DE440 ephemeris data through Astropy. It
			then projects those positions onto your photograph with a tangent-plane camera model
			built from the photo's focal length and sensor dimensions, and the result is a precise
			analemma curve rendered directly on your sky.
		</p>
		<p>
			Upload any photo with the sun in it. The app will try to detect the sun automatically;
			if that doesn't work (overcast, lens flare, the sun is behind clouds), you can click
			to select its position manually.
		</p>
	</section>

	<footer class="border-t border-slate-700 pt-6 text-sm text-slate-500">
		<p>
			The math and engineering behind the projection are covered on the
			<a href="/methodology" class="text-amber-400 hover:text-amber-300">Methodology</a> page.
		</p>
	</footer>
</div>
