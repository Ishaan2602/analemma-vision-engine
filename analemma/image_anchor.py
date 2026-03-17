"""
Image-to-Analemma Anchoring Utility

This module implements the priority feature: overlaying the theoretical analemma
onto a real photograph of the sky, anchored at a specific timestamp and GPS location.

Workflow:
1. Take a user-provided image with metadata (Timestamp + GPS)
2. Calculate the True Sun Position for that specific timestamp
3. Assume this position aligns with the Sun pixel in the image
4. Generate the full year's analemma for that same time of day
5. Overlay the theoretical curve onto the image
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict, List
from datetime import datetime
import matplotlib.pyplot as plt

from .calculator import AnalemmaCalculator
from .sky_mapper import SkyMapper


class ImageAnchorer:
    """
    Overlay analemma curves onto real sky photographs.
    
    This creates "Augmented Reality" style images showing where the sun
    will be throughout the year when photographed at the same time each day.
    
    Parameters
    ----------
    image_path : str
        Path to the sky photograph
    anchor_datetime : datetime
        Date and time when the photo was taken
    latitude : float
        GPS latitude where photo was taken
    longitude : float
        GPS longitude where photo was taken
    sun_pixel : tuple, optional
        (x, y) pixel coordinates of the sun in the image
        If None, will use center of image
    """
    
    def __init__(self,
                 image_path: str,
                 anchor_datetime: datetime,
                 latitude: float,
                 longitude: float,
                 sun_pixel: Optional[Tuple[int, int]] = None,
                 auto_detect_sun: bool = True,
                 timezone_offset: float = None,
                 mode: str = 'approximate'):
        """Initialize the image anchorer."""
        # Load image and apply EXIF orientation
        self.image = Image.open(image_path)
        
        # Apply EXIF orientation if present
        try:
            from PIL import ImageOps
            self.image = ImageOps.exif_transpose(self.image)
        except Exception:
            pass  # If EXIF orientation fails, use image as-is
        
        self.image_width, self.image_height = self.image.size
        
        # Store metadata
        self.anchor_datetime = anchor_datetime
        self.latitude = latitude
        self.longitude = longitude
        
        # Sun position in image - auto-detect if not provided
        if sun_pixel is None and auto_detect_sun:
            self.sun_pixel = self._detect_sun_position()
            print(f"Auto-detected sun at pixel: {self.sun_pixel}")
        elif sun_pixel is None:
            self.sun_pixel = (self.image_width // 2, self.image_height // 2)
        else:
            self.sun_pixel = sun_pixel
        
        # Initialize calculator and mapper
        self.calculator = AnalemmaCalculator(mode=mode, 
                                            year=anchor_datetime.year)
        self.sky_mapper = SkyMapper(latitude, longitude, 
                                   timezone_offset=timezone_offset,
                                   reference_datetime=anchor_datetime)
        
        # Calculate anchor point sky coordinates
        self.anchor_data = self._calculate_anchor_position()
        
        # Calibration parameters (pixels per degree)
        self.pixels_per_degree_az = None
        self.pixels_per_degree_alt = None
    
    def _detect_sun_position(self) -> Tuple[int, int]:
        """Detect the sun's position in the image.
        
        Uses progressive thresholding with connected-component analysis.
        Starts at a strict threshold and lowers it until a blob of
        meaningful size is found. For large saturated blobs, refines
        the center by finding the "whitest" region (highest minimum
        RGB channel) within the blob -- the sun disk is white while
        the surrounding glow tends to be colored.
        """
        import numpy as np
        try:
            from scipy import ndimage
            has_scipy = True
        except ImportError:
            has_scipy = False
        
        img_array = np.array(self.image)
        is_color = len(img_array.shape) == 3
        
        if is_color:
            gray = np.max(img_array, axis=2).astype(np.float64)
        else:
            gray = img_array.astype(np.float64)
        
        max_val = gray.max()
        min_blob_size = 20
        
        if has_scipy:
            # Progressive threshold: start strict, lower until a real blob appears
            thresholds = [0.999, 0.995, 0.99, 0.985, 0.98, 0.975, 0.97, 0.965, 0.96]
            blob_mask = None
            
            for thresh in thresholds:
                bright_mask = gray >= max_val * thresh
                labeled, num_features = ndimage.label(bright_mask)
                
                if num_features == 0:
                    continue
                
                sizes = ndimage.sum(bright_mask, labeled, range(num_features + 1))
                blob_sizes = sizes[1:]
                largest_size = blob_sizes.max()
                
                if largest_size >= min_blob_size:
                    largest_label = blob_sizes.argmax() + 1
                    blob_mask = labeled == largest_label
                    break
            
            if blob_mask is None:
                max_loc = np.unravel_index(gray.argmax(), gray.shape)
                return (int(max_loc[1]), int(max_loc[0]))
            
            blob_size = blob_mask.sum()
            
            # For large blobs, find the center of the brightest concentration
            # using a Gaussian-blurred luminance peak within the blob region.
            # Sigma scales with blob size: small blobs need tight focus,
            # large blobs need more smoothing to avoid local peaks.
            if blob_size > 100:
                from scipy.ndimage import gaussian_filter
                
                # Use sum of all channels for luminance (more info than max)
                if is_color:
                    lum = img_array.astype(np.float64).sum(axis=2)
                else:
                    lum = gray
                
                # Crop around the blob bounding box with margin
                cy, cx = np.where(blob_mask)
                margin = 20
                y_min = max(0, cy.min() - margin)
                y_max = min(img_array.shape[0], cy.max() + margin + 1)
                x_min = max(0, cx.min() - margin)
                x_max = min(img_array.shape[1], cx.max() + margin + 1)
                
                lum_crop = lum[y_min:y_max, x_min:x_max]
                
                # Adaptive sigma: ~12% of the blob's characteristic radius
                blob_radius = np.sqrt(blob_size / np.pi)
                sigma = max(1, min(blob_radius * 0.12, 5))
                
                blurred = gaussian_filter(lum_crop, sigma=sigma)
                peak = np.unravel_index(blurred.argmax(), blurred.shape)
                sun_x = int(peak[1] + x_min)
                sun_y = int(peak[0] + y_min)
            else:
                # Small blob or grayscale: weighted centroid
                cy, cx = np.where(blob_mask)
                weights = gray[cy, cx]
                sun_x = int(round(np.average(cx, weights=weights)))
                sun_y = int(round(np.average(cy, weights=weights)))
        else:
            bright_mask = gray >= max_val * 0.999
            if bright_mask.sum() > 10:
                y_coords, x_coords = np.where(bright_mask)
                weights = gray[y_coords, x_coords]
                sun_x = int(np.average(x_coords, weights=weights))
                sun_y = int(np.average(y_coords, weights=weights))
            else:
                max_loc = np.unravel_index(gray.argmax(), gray.shape)
                sun_y, sun_x = max_loc
        
        return (sun_x, sun_y)
        
    def _calculate_anchor_position(self) -> Dict:
        """Calculate the true sun position at anchor time."""
        calc_result = self.calculator.calculate(self.anchor_datetime)
        sky_result = self.sky_mapper.map_single_point(calc_result)
        return sky_result
    
    def calibrate_from_field_of_view(self, 
                                     horizontal_fov: float,
                                     vertical_fov: float):
        """
        Calibrate pixel-to-degree mapping from camera field of view.
        
        Parameters
        ----------
        horizontal_fov : float
            Horizontal field of view in degrees
        vertical_fov : float
            Vertical field of view in degrees
        """
        self.pixels_per_degree_az = self.image_width / horizontal_fov
        self.pixels_per_degree_alt = self.image_height / vertical_fov
    
    def calibrate_from_focal_length(self,
                                    focal_length_mm: float,
                                    sensor_width_mm: float = 36.0,
                                    sensor_height_mm: float = 24.0):
        """
        Calibrate from camera focal length and sensor size.
        
        Parameters
        ----------
        focal_length_mm : float
            Lens focal length in millimeters
        sensor_width_mm : float
            Sensor width in millimeters (default: 36mm for full frame)
        sensor_height_mm : float
            Sensor height in millimeters (default: 24mm for full frame)
        """
        # Calculate field of view
        h_fov = 2 * np.degrees(np.arctan(sensor_width_mm / (2 * focal_length_mm)))
        v_fov = 2 * np.degrees(np.arctan(sensor_height_mm / (2 * focal_length_mm)))
        
        self.calibrate_from_field_of_view(h_fov, v_fov)
    
    def sky_to_pixel(self, altitude: float, azimuth: float) -> Tuple[int, int]:
        """
        Convert sky coordinates (alt/az) to image pixel coordinates.
        
        Parameters
        ----------
        altitude : float
            Altitude in degrees
        azimuth : float
            Azimuth in degrees
        
        Returns
        -------
        tuple
            (x, y) pixel coordinates
        """
        if self.pixels_per_degree_az is None:
            raise ValueError("Must calibrate before converting coordinates. "
                           "Call calibrate_from_field_of_view() or "
                           "calibrate_from_focal_length()")
        
        # Calculate offset from anchor point
        anchor_alt = self.anchor_data['altitude']
        anchor_az = self.anchor_data['azimuth']
        
        delta_az = azimuth - anchor_az
        delta_alt = altitude - anchor_alt
        
        # Apply cos(altitude) correction for azimuth.
        # Lines of constant azimuth converge toward the zenith, just like
        # longitude lines converge at the poles. 1 degree of azimuth subtends
        # fewer pixels at higher altitudes. We use the mean altitude of the
        # anchor and target as a midpoint approximation.
        mean_alt_rad = np.radians((anchor_alt + altitude) / 2.0)
        
        # Convert to pixel offset (y is inverted - up is negative)
        delta_x = delta_az * np.cos(mean_alt_rad) * self.pixels_per_degree_az
        delta_y = -delta_alt * self.pixels_per_degree_alt
        
        # Apply to anchor pixel
        x = int(self.sun_pixel[0] + delta_x)
        y = int(self.sun_pixel[1] + delta_y)
        
        return (x, y)
    
    def generate_analemma_points(self, days: int = 365) -> List[Dict]:
        """
        Generate analemma points for the full year.
        
        Parameters
        ----------
        days : int
            Number of days to calculate
        
        Returns
        -------
        list
            List of dictionaries with sky coordinates and pixel positions
        """
        # Calculate for same time of day throughout the year
        year_data = self.calculator.calculate_year(
            hour=self.anchor_datetime.hour,
            minute=self.anchor_datetime.minute,
            days=days
        )
        
        # Map to horizon coordinates
        sky_data = self.sky_mapper.map_to_horizon(year_data)
        
        # Convert to pixel coordinates and filter out points below horizon
        all_points = []
        for point in sky_data:
            x, y = self.sky_to_pixel(point['altitude'], point['azimuth'])
            point['pixel_x'] = x
            point['pixel_y'] = y
            all_points.append(point)
        
        return all_points
    
    def overlay_analemma(self,
                        output_path: str,
                        dot_size: int = 10,
                        dot_color: Tuple[int, int, int] = (255, 255, 0),
                        line_color: Tuple[int, int, int] = (255, 200, 0),
                        line_width: int = 2,
                        show_dates: bool = True,
                        date_interval: int = 30) -> Image.Image:
        """
        Overlay the analemma curve onto the image.
        
        Parameters
        ----------
        output_path : str
            Path to save the output image
        dot_size : int
            Size of dots marking sun positions
        dot_color : tuple
            RGB color for dots
        line_color : tuple
            RGB color for connecting line
        line_width : int
            Width of connecting line
        show_dates : bool
            Whether to label specific dates
        date_interval : int
            Days between date labels
        
        Returns
        -------
        PIL.Image.Image
            The output image with overlay
        """
        # Generate analemma points
        analemma_points = self.generate_analemma_points()
        
        # Create a copy of the image to draw on
        output_image = self.image.copy()
        draw = ImageDraw.Draw(output_image)
        
        # Try to load a font (fall back to default if not available)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        def _in_bounds(x, y):
            return 0 <= x < self.image_width and 0 <= y < self.image_height
        
        # Draw connecting line segments between consecutive in-bounds points.
        # Break the line at gaps where points fall outside the image so we
        # don't get spurious lines connecting distant parts of the analemma.
        current_segment = []
        for p in analemma_points:
            px, py = p['pixel_x'], p['pixel_y']
            if _in_bounds(px, py):
                current_segment.append((px, py))
            else:
                # End current segment
                if len(current_segment) > 1:
                    draw.line(current_segment, fill=line_color, width=line_width)
                current_segment = []
        # Draw final segment
        if len(current_segment) > 1:
            draw.line(current_segment, fill=line_color, width=line_width)
        
        # Draw dots for each position
        points_in_image = 0
        for i, point in enumerate(analemma_points):
            x, y = point['pixel_x'], point['pixel_y']
            
            # Skip if outside image bounds
            if not _in_bounds(x, y):
                continue
            
            points_in_image += 1
            
            # Draw dot
            bbox = [x - dot_size//2, y - dot_size//2,
                   x + dot_size//2, y + dot_size//2]
            draw.ellipse(bbox, fill=dot_color, outline=(0, 0, 0))
            
            # Add date label
            if show_dates and i % date_interval == 0:
                date_str = point['date'].strftime('%b %d')
                draw.text((x + dot_size, y), date_str, 
                         fill=(255, 255, 255), font=font)
        
        # Highlight anchor point (current date)
        anchor_x, anchor_y = self.sun_pixel
        highlight_size = dot_size * 2
        bbox = [anchor_x - highlight_size//2, anchor_y - highlight_size//2,
               anchor_x + highlight_size//2, anchor_y + highlight_size//2]
        draw.ellipse(bbox, fill=(255, 0, 0), outline=(255, 255, 255), width=2)
        
        # Add text annotation
        anchor_str = self.anchor_datetime.strftime('%Y-%m-%d %H:%M')
        draw.text((anchor_x + highlight_size, anchor_y), 
                 f"Anchor: {anchor_str}",
                 fill=(255, 255, 255), font=font)
        
        # Add metadata text
        tz_info = ""
        if self.sky_mapper._iana_timezone_name:
            tz_info = f" | TZ: {self.sky_mapper._iana_timezone_name} (UTC{self.sky_mapper.timezone_offset:+.1f})"
        metadata_text = (f"Location: {self.latitude:.2f}\u00b0, {self.longitude:.2f}\u00b0{tz_info}\n"
                        f"Analemma for {self.anchor_datetime.strftime('%H:%M')} "
                        f"throughout {self.anchor_datetime.year}")
        draw.text((10, 10), metadata_text, fill=(255, 255, 255), font=font)
        
        # Save output
        output_image.save(output_path)
        
        # Return metadata
        total_points = len(analemma_points)
        points_outside = total_points - points_in_image
        
        return {
            'image': output_image,
            'points_drawn': points_in_image,
            'points_filtered': points_outside,
            'sun_pixel': self.sun_pixel,
            'sun_altitude': self.anchor_data['altitude'],
            'sun_azimuth': self.anchor_data['azimuth']
        }
    
    def create_composite_plot(self, output_path: str) -> plt.Figure:
        """
        Create a composite visualization showing image and sky chart.
        
        Parameters
        ----------
        output_path : str
            Path to save the output figure
        
        Returns
        -------
        matplotlib.figure.Figure
            The created figure
        """
        analemma_points = self.generate_analemma_points()
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Left: Original image with overlay
        overlay_img = self.overlay_analemma(output_path + '_temp.png')
        ax1.imshow(overlay_img)
        ax1.axis('off')
        ax1.set_title('Image with Analemma Overlay', fontsize=14, fontweight='bold')
        
        # Right: Sky chart
        altitudes = [p['altitude'] for p in analemma_points]
        azimuths = [p['azimuth'] for p in analemma_points]
        
        scatter = ax2.scatter(azimuths, altitudes,
                            c=range(len(analemma_points)),
                            cmap='twilight',
                            s=50, alpha=0.7,
                            edgecolors='black', linewidth=0.5)
        
        # Highlight anchor point
        ax2.scatter([self.anchor_data['azimuth']], 
                   [self.anchor_data['altitude']],
                   c='red', s=200, marker='*',
                   edgecolors='white', linewidth=2,
                   label='Anchor Date', zorder=10)
        
        ax2.set_xlabel('Azimuth (degrees)', fontsize=12)
        ax2.set_ylabel('Altitude (degrees)', fontsize=12)
        ax2.set_title('Sky Chart', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.colorbar(scatter, ax=ax2, label='Day of Year')
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the analemma for this location and time.
        
        Returns
        -------
        dict
            Dictionary with statistics including:
            - altitude_range: (min, max) altitude
            - azimuth_range: (min, max) azimuth
            - figure_size: angular size of figure-8
        """
        analemma_points = self.generate_analemma_points()
        
        altitudes = [p['altitude'] for p in analemma_points]
        azimuths = [p['azimuth'] for p in analemma_points]
        
        stats = {
            'altitude_range': (min(altitudes), max(altitudes)),
            'azimuth_range': (min(azimuths), max(azimuths)),
            'altitude_span': max(altitudes) - min(altitudes),
            'azimuth_span': max(azimuths) - min(azimuths),
            'anchor_altitude': self.anchor_data['altitude'],
            'anchor_azimuth': self.anchor_data['azimuth'],
            'anchor_date': self.anchor_datetime,
            'location': (self.latitude, self.longitude)
        }
        
        return stats
    
    def __repr__(self) -> str:
        return (f"ImageAnchorer(anchor={self.anchor_datetime}, "
                f"location=({self.latitude}°, {self.longitude}°))")
