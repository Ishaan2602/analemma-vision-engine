<svelte:head>
	<title>Methodology -- Analemma Vision</title>
	<meta name="description" content="Technical details: how Analemma Vision computes solar positions, projects them onto photographs, and detects the sun." />
</svelte:head>

<div class="max-w-3xl mx-auto px-4 sm:px-6 py-10 text-slate-300 space-y-10">
	<header>
		<h1 class="text-3xl font-bold text-slate-50 mb-2">Methodology</h1>
		<p class="text-slate-400">How the engine computes and renders an analemma overlay</p>
	</header>

	<!-- 1. Solar Position Computation -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">1. Solar Position Computation</h2>
		<p>
			The engine queries the sun's position using Astropy's <code class="text-amber-400">get_sun()</code>
			function backed by JPL's DE440 development ephemeris. For each week of the year at the
			observer's clock time, it retrieves the sun's right ascension and declination in the
			geocentric ICRS frame, then transforms to the observer's local horizon coordinates.
		</p>
		<p>
			Two quantities drive the analemma shape:
		</p>
		<ul class="list-disc list-inside space-y-2 ml-2 text-slate-300">
			<li>
				<strong class="text-slate-100">Solar declination</strong> -- oscillates between approx.
				+23.44 and -23.44 degrees over a year due to axial tilt. This sets the analemma's
				vertical extent.
			</li>
			<li>
				<strong class="text-slate-100">Equation of Time (EoT)</strong> -- the difference between
				mean solar time and apparent solar time, caused by orbital eccentricity and obliquity.
				Ranges from about -16.4 to +14.3 minutes. This shifts the sun east/west of its mean
				position and creates the horizontal width of the figure-eight.
			</li>
		</ul>
		<p>
			The EoT is computed from the difference between the mean sun's longitude-derived right
			ascension and the true right ascension returned by the ephemeris. The mean solar longitude is:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			L0 = (280.46646 + 0.9856474 * n) mod 360
		</div>
		<p class="text-sm text-slate-400">
			where n is days since J2000.0. The EoT in minutes is then
			(L0/15 - RA_sun) * 60, normalized to +/-720 minutes.
		</p>
	</section>

	<!-- 2. Horizon Coordinates -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">2. Horizon Coordinate Transform</h2>
		<p>
			Each sun position (declination + EoT) is converted to local altitude and azimuth
			using standard spherical trigonometry.
		</p>
		<p><strong class="text-slate-100">Hour angle:</strong></p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			H = (t - 12) * 15 + EoT / 4 + (lon - tz * 15)
		</div>
		<p class="text-sm text-slate-400">
			t is the observation time in decimal hours, EoT/4 converts minutes to degrees,
			and the longitude term corrects for the observer's offset from the timezone meridian.
		</p>

		<p><strong class="text-slate-100">Altitude:</strong></p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			sin(alt) = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(H)
		</div>

		<p><strong class="text-slate-100">Azimuth:</strong></p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			az = atan2(cos(dec) * sin(H), cos(dec) * cos(H) * sin(lat) - sin(dec) * cos(lat))
		</div>
		<p class="text-sm text-slate-400">
			Normalized to [0, 360) measured clockwise from North.
		</p>

		<p>
			Timezone detection uses a three-tier approach: explicit UTC offset if provided, then
			IANA auto-detection via <code class="text-amber-400">timezonefinder</code> (DST-aware),
			then a round(longitude/15) fallback. The IANA path is important for places like
			Hawaii (UTC-10, but round(-157.8/15) = -11) or China (UTC+8 across a wide longitude span).
		</p>
	</section>

	<!-- 3. Camera Model -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">3. Camera Model and Projection</h2>
		<p>
			The engine uses a tangent-plane (pinhole) camera model. From the focal length and
			sensor dimensions extracted from EXIF data, it computes the field of view:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			FOV_h = 2 * arctan(sensor_width / (2 * focal_length))<br />
			FOV_v = 2 * arctan(sensor_height / (2 * focal_length))
		</div>
		<p>
			This gives pixels-per-degree in both axes, which maps angular separations to pixel
			distances on the image.
		</p>

		<p><strong class="text-slate-100">Sky-to-pixel projection:</strong></p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			dx = d_az * cos(mean_alt) * px_per_deg_az<br />
			dy = -d_alt * px_per_deg_alt
		</div>
		<p class="text-sm text-slate-400">
			The cos(mean_alt) factor corrects for azimuthal foreshortening at high altitudes --
			without it, the overlay would be horizontally stretched when the sun is high in the sky.
			The negative sign on dy accounts for image coordinates having y increasing downward.
		</p>
		<p>
			All 365 sun positions are projected relative to the anchor point -- the detected sun,
			whose pixel position and sky coordinates are both known. This "differential projection"
			avoids needing to know the absolute camera pointing direction.
		</p>
	</section>

	<!-- 4. Sun Detection -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">4. Sun Detection</h2>
		<p>
			The CV pipeline finds the sun's pixel position in the uploaded photo through progressive
			thresholding with centroid refinement:
		</p>
		<ol class="list-decimal list-inside space-y-2 ml-2 text-slate-300">
			<li>
				Apply EXIF orientation correction (rotation, mirroring) so pixel coordinates match the
				displayed image.
			</li>
			<li>
				Convert to grayscale using max(R, G, B) per pixel rather than luminance weighting, since
				the sun saturates all channels equally.
			</li>
			<li>
				Starting at 99.9% of max brightness, progressively lower the threshold (99.5, 99.0, ...)
				until finding a connected blob with at least 20 pixels. This skips single-pixel glare
				artifacts from lens flare.
			</li>
			<li>
				Label connected components via <code class="text-amber-400">scipy.ndimage.label()</code>
				and select the largest blob.
			</li>
			<li>
				Compute the brightness-weighted centroid of the blob for sub-pixel accuracy.
			</li>
		</ol>
		<p>
			If auto-detection fails (no suitable blob at any threshold), the app prompts you to
			click on the sun's position manually using the image picker overlay.
		</p>
	</section>

	<!-- 5. Overlay Rendering -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">5. Overlay Rendering</h2>
		<p>
			The overlay is rendered as an SVG layer composited over the original photograph:
		</p>
		<ol class="list-decimal list-inside space-y-2 ml-2 text-slate-300">
			<li>Compute pixel positions for all 365 analemma points via the camera projection.</li>
			<li>Draw connecting line segments between consecutive in-bounds points, breaking
				the polyline at gaps where points leave the image frame. This prevents spurious
				lines cutting across the photo.</li>
			<li>Render dots at each visible sun position.</li>
			<li>Mark the anchor point (the photo's sun position) with a highlighted dot.</li>
		</ol>
		<p>
			The date-colored gradient runs from January (cool) through the year to December,
			letting you visually trace the sun's path through the seasons.
		</p>
	</section>

	<!-- 6. Limitations -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">6. Limitations</h2>
		<ul class="list-disc list-inside space-y-2 ml-2 text-slate-300">
			<li>
				<strong class="text-slate-100">Pinhole model:</strong> The tangent-plane projection is
				accurate for narrow to moderate fields of view but breaks down for ultra-wide-angle or
				fisheye lenses where barrel distortion becomes significant.
			</li>
			<li>
				<strong class="text-slate-100">Atmospheric refraction:</strong> Not modeled. Near the
				horizon, refraction lifts the apparent sun position by roughly 0.5 degrees, which can
				noticeably shift points at very low altitudes.
			</li>
			<li>
				<strong class="text-slate-100">Sensor crop factor:</strong> The engine uses the sensor
				dimensions you provide. If the photo was cropped or shot with a crop-sensor body but you
				enter full-frame dimensions, the overlay scale will be wrong.
			</li>
			<li>
				<strong class="text-slate-100">Sun detection:</strong> Works best with a clearly visible
				sun disc. Overcast skies, sun partially behind clouds, or reflections can confuse the
				detector. Use manual selection in these cases.
			</li>
		</ul>
	</section>

	<!-- 7. Stack -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">7. Technology Stack</h2>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
				<p class="text-sm font-medium text-slate-100 mb-1">Computation</p>
				<p class="text-sm text-slate-400">Astropy + JPL DE440, NumPy, SciPy</p>
			</div>
			<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
				<p class="text-sm font-medium text-slate-100 mb-1">Image Processing</p>
				<p class="text-sm text-slate-400">Pillow, EXIF transpose, brightness-weighted centroid</p>
			</div>
			<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
				<p class="text-sm font-medium text-slate-100 mb-1">Backend</p>
				<p class="text-sm text-slate-400">FastAPI, ThreadPoolExecutor, slowapi rate limiting</p>
			</div>
			<div class="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
				<p class="text-sm font-medium text-slate-100 mb-1">Frontend</p>
				<p class="text-sm text-slate-400">SvelteKit 5, Svelte 5 runes, TailwindCSS v4</p>
			</div>
		</div>
	</section>

	<footer class="border-t border-slate-700 pt-6 text-sm text-slate-500">
		<p>
			Source code and full technical documentation available on
			<a
				href="https://github.com/Ishaan2602/analemma-vision-engine"
				target="_blank"
				rel="noopener noreferrer"
				class="text-amber-400 hover:text-amber-300"
			>GitHub</a>.
		</p>
	</footer>
</div>
