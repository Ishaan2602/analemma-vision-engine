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
			The engine uses Astropy's <code class="text-amber-400">get_sun()</code> function,
			backed by JPL's DE440 development ephemeris, to query the sun's geocentric ICRS
			coordinates at each day of the year for a given clock time. It then transforms those
			into local horizon coordinates for the observer.
		</p>
		<p>
			The two quantities that matter most are <strong class="text-slate-100">solar
			declination</strong> (which oscillates roughly +/-23.44 degrees over the year due to
			axial tilt, setting the analemma's vertical extent) and the
			<strong class="text-slate-100">Equation of Time</strong>, the offset between mean
			and apparent solar time. The EoT can swing from about -16.4 to +14.3 minutes across
			the year, pushing the sun east or west of its expected position and creating the
			figure-eight's horizontal width.
		</p>
		<p>
			To compute the EoT, we take the difference between a mean solar longitude and the
			true right ascension from the ephemeris:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			L0 = (280.46646 + 0.9856474 * n) mod 360
		</div>
		<p class="text-sm text-slate-400">
			n is days since J2000.0. The EoT in minutes is (L0/15 - RA_sun) * 60,
			normalized to +/-720 minutes to handle the RA wraparound.
		</p>
	</section>

	<!-- 2. Horizon Coordinates -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">2. Horizon Coordinate Transform</h2>
		<p>
			Converting from declination and EoT to local altitude and azimuth is standard
			spherical trig. The hour angle tells you how far the sun is from the observer's
			meridian, measured westward:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			H = (t - 12) * 15 + EoT / 4 + (lon - tz * 15)
		</div>
		<p class="text-sm text-slate-400">
			t is observation time in decimal hours. EoT/4 converts minutes to degrees.
			The longitude term corrects for the observer's offset from the timezone's
			central meridian.
		</p>

		<p>From there, altitude and azimuth follow directly:</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			sin(alt) = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(H)
		</div>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto mt-2">
			az = atan2(cos(dec) * sin(H), cos(dec) * cos(H) * sin(lat) - sin(dec) * cos(lat))
		</div>
		<p class="text-sm text-slate-400">
			Azimuth is normalized to [0, 360) clockwise from North.
		</p>

		<p>
			Getting the timezone right matters more than you'd expect. The engine tries three
			approaches in order: an explicit UTC offset if the user provides one, then IANA
			auto-detection via <code class="text-amber-400">timezonefinder</code> (which handles
			DST correctly), and finally a round(longitude/15) fallback. The IANA path exists
			because the naive formula fails in places like Hawaii (UTC-10, but
			round(-157.8/15) gives -11) or China, which uses a single timezone across a 60-degree
			span of longitude.
		</p>
	</section>

	<!-- 3. Camera Model -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">3. Camera Model and Projection</h2>
		<p>
			We use a tangent-plane (pinhole) camera model to go from sky coordinates to pixel
			coordinates. The field of view comes from the focal length and physical sensor
			dimensions, both of which the app extracts from EXIF data when available:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			FOV_h = 2 * arctan(sensor_width / (2 * focal_length))<br />
			FOV_v = 2 * arctan(sensor_height / (2 * focal_length))
		</div>
		<p>
			Dividing the image's pixel dimensions by the FOV gives pixels-per-degree in each axis.
			The projection from sky separation to pixel offset then looks like this:
		</p>
		<div class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-200 overflow-x-auto">
			dx = d_az * cos(mean_alt) * px_per_deg_az<br />
			dy = -d_alt * px_per_deg_alt
		</div>
		<p>
			The cos(mean_alt) factor is doing real work here. At high altitudes, lines of constant
			azimuth converge (the same way longitude lines converge near the poles), so one degree
			of azimuth covers fewer linear degrees of sky. Without this correction the overlay
			stretches horizontally whenever the sun is high. The negative sign on dy just accounts
			for image coordinates having y increase downward.
		</p>
		<p>
			Everything is projected relative to the anchor point, which is the detected (or manually
			selected) sun position. Because we know both its pixel location and its sky coordinates,
			we can compute pixel offsets for every other point without ever needing to know where
			the camera was actually pointing in absolute terms.
		</p>
	</section>

	<!-- 4. Sun Detection -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">4. Sun Detection</h2>
		<p>
			Finding the sun in a photograph turns out to be trickier than "find the brightest
			pixel." Lens flare, specular reflections, and JPEG compression artifacts all produce
			isolated bright spots that aren't the sun. The detection pipeline handles this with
			progressive thresholding:
		</p>
		<ol class="list-decimal list-inside space-y-2 ml-2 text-slate-300">
			<li>
				First, apply EXIF orientation tags so the image matches what the user actually sees
				(rotation, mirroring).
			</li>
			<li>
				Convert to grayscale by taking max(R, G, B) per pixel. Luminance-weighted averages
				would undercount the sun, which saturates all three channels.
			</li>
			<li>
				Starting at 99.9% of the image's peak brightness, threshold the image and look for
				connected blobs of at least 20 pixels. If nothing qualifies, lower the threshold to
				99.5%, then 99.0%, and so on down to 96%. The minimum-size requirement filters out
				single-pixel glare artifacts that pass high thresholds but are too small to be the
				actual sun disc.
			</li>
			<li>
				Once a qualifying blob is found, <code class="text-amber-400">scipy.ndimage.label()</code>
				identifies connected components and the largest one is selected.
			</li>
			<li>
				The sun center is the brightness-weighted centroid of that blob, which gives
				sub-pixel accuracy.
			</li>
		</ol>
		<p>
			When none of that works (overcast sky, sun behind a cloud, unusual exposure), the app
			falls back to the manual picker.
		</p>
	</section>

	<!-- 5. Overlay Rendering -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">5. Overlay Rendering</h2>
		<p>
			The overlay is an SVG layer composited over the original photograph. All 365 analemma
			points get projected to pixel coordinates through the camera model, then rendered as
			connected line segments with dots at each sun position.
		</p>
		<p>
			One subtlety: the analemma sometimes exits the frame and re-enters at a distant point.
			A naive single polyline would draw a diagonal across the image connecting those
			re-entry points. The renderer detects these gaps (any jump larger than 4x the median
			point spacing) and breaks the path into separate segments.
		</p>
		<p>
			A date-based color gradient runs from January through December, so you can visually
			trace the sun's seasonal progression along the curve.
		</p>
	</section>

	<!-- 6. Limitations -->
	<section class="space-y-4">
		<h2 class="text-xl font-semibold text-slate-100">6. Limitations</h2>
		<p>
			The tangent-plane projection works well for normal and telephoto lenses but starts to
			break down with ultra-wide-angle glass or fisheye lenses, where barrel distortion
			becomes significant. We don't currently model lens distortion profiles.
		</p>
		<p>
			Atmospheric refraction isn't modeled either. Near the horizon, refraction lifts the
			apparent sun position by roughly half a degree, which can noticeably shift points
			at very low altitudes.
		</p>
		<p>
			The overlay scale depends on getting the sensor dimensions right. If you're shooting
			with a crop-sensor body but enter full-frame sensor values, or if the image has been
			cropped after capture, the projection won't match. The app tries to pull these from
			EXIF, but not all cameras write sensor dimensions into metadata.
		</p>
		<p>
			Sun detection works best with a clearly visible sun disc against sky. Overcast
			conditions, the sun partly behind clouds, or strong reflections off water/glass can
			all confuse the detector.
		</p>
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
