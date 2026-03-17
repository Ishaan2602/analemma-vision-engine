# Project Specification: The Analemma Engine

## 1. Project Overview
**Goal:** Build a robust, versatile Python-based system to analyze, simulate, and visualize the **Analemma**—the figure-8 path the Sun traces in the sky when photographed at the same mean solar time over a year.

**Long-term Vision:** A suite of tools including 3D simulations, multi-planet comparisons, and real-time web rendering.
**Immediate Focus:** A Python utility to calculate and visualize the analemma from a specific observer's location (Latitude/Longitude), with a specific feature focus on "Image Anchoring" (extrapolating an analemma from a single timestamped photo).

## 2. Theoretical Framework & Math
The system must be grounded in the following astronomical principles.

### A. The Core Components
The analemma's shape is derived from two primary orbital effects:
1.  **Solar Declination ($\delta$):** The vertical component (North/South). Caused by Earth's axial tilt (Obliquity $\epsilon \approx 23.44^\circ$).
2.  **Equation of Time ($EoT$):** The horizontal component (East/West). The difference between *Apparent Solar Time* and *Mean Solar Time*. Caused by:
    * **Obliquity:** The tilt of the ecliptic relative to the equator.
    * **Eccentricity:** The variable speed of Earth in its elliptical orbit (Kepler's 2nd Law).

### B. Governing Equations
**1. Altitude Calculation (Spherical Law of Cosines)**
To map the sun's position to the observer's local sky (Horizon Coordinates):
$$
\sin(a) = \sin(\phi)\sin(\delta) + \cos(\phi)\cos(\delta)\cos(H)
$$
* $a$: Altitude
* $\phi$: Observer's Latitude
* $\delta$: Solar Declination
* $H$: Local Hour Angle (derived from $EoT$ and local time)

**2. Max Altitude (Meridian Transit)**
$$
a_{max} = 90^\circ - |\phi - \delta|
$$

**3. Solar Declination Approximation**
For the "Simple Mode" (educational approximation), use the sine wave model:
$$
\delta \approx 23.45^\circ \sin\left[\frac{360}{365}(284+N)\right]
$$
* $N$: Day of the year (1-365).
* **Note:** The constant $284$ is a phase shift to ensure $\delta=0$ at the Vernal Equinox ($N \approx 81$).

## 3. Technical Architecture (Python)
We will build this in **three modular layers** to ensure separation of concerns.

### Layer 1: The Physics Engine (`AnalemmaCalculator`)
* **Responsibility:** Pure numerical calculation. No awareness of location or plotting.
* **Input:** Date/Time.
* **Output:** Tuple `(Declination, Equation_of_Time)`.
* **Feature: Dual Precision Modes**
    * *Mode A (Approximate):* Uses standard sine-wave formulas (fast, good for understanding the "why").
    * *Mode B (High-Precision):* Wraps `astropy` or `jplephem` to get NASA-grade coordinates.

### Layer 2: The Sky Projector (`SkyMapper`)
* **Responsibility:** Coordinate transformation.
* **Input:** `(Declination, EoT)` from Layer 1 + `(Latitude, Longitude)` of observer.
* **Output:** Local Horizon Coordinates `(Altitude, Azimuth)`.
* **Logic:** Must handle the conversion of $EoT$ into Hour Angle $H$, accounting for the observer's longitude offset from their time zone meridian.

### Layer 3: The Visualizer (`AnalemmaPlotter`)
* **Responsibility:** Rendering.
* **Tools:** `matplotlib` (static/interactive) or `plotly` (web-ready).
* **Outputs:**
    * 2D Sky Chart (Azimuth vs. Altitude).
    * "Figure-8" standalone plot ($EoT$ vs. Declination).

## 4. Key Utility: "Image-to-Analemma" Anchoring
This is a priority feature to explore.
* **Concept:** Take a user-provided image of the sky with metadata (Timestamp + GPS).
* **Workflow:**
    1.  Calculate the **True Sun Position** (Alt/Az) for that specific timestamp.
    2.  Assume this calculated position aligns with the "Sun" pixel in the image (or center of frame if aiming at sun).
    3.  Generate the full year's analemma data points for that same time of day.
    4.  Overlay the theoretical curve onto the image relative to the anchor point.
* **Goal:** Create an "Augmented Reality" style static image showing where the sun *will be* the rest of the year.

## 5. Implementation Roadmap
1.  **Setup Environment:** Initialize Python with `numpy`, `matplotlib`, `astropy`, `pandas`.
2.  **Build Layer 1 (Dual Mode):** Implement the `AnalemmaCalculator` class with a switch for precision.
3.  **Validate Math:** distinct unit tests to compare the "Approximate" mode vs "Astropy" mode to see the divergence.
4.  **Build Layer 2 & 3:** Generate a standard "UIUC Noon Analemma" plot (Latitude $40^\circ$ N) to verify the figure-8 shape (checking for the South-culminating loop).
5.  **Prototype Image Anchor:** Create a script that accepts a dummy image and pixel coordinate, and overlays the calculated curve.