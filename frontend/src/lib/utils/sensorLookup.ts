export interface SensorSize {
	width: number;
	height: number;
	source: 'exif' | 'database' | 'manual';
}

interface CameraEntry {
	cropfactor: number;
	maker: string;
	model: string;
}

let sensorDb: Record<string, CameraEntry> | null = null;

/**
 * Tier 1: Compute sensor size from EXIF crop factor.
 * Requires both focalLength and focalLength35mm.
 */
export function sensorFromExif(
	focalLength: number,
	focalLength35mm: number,
	imageWidth?: number,
	imageHeight?: number
): SensorSize | null {
	if (!focalLength || !focalLength35mm || focalLength <= 0 || focalLength35mm <= 0) {
		return null;
	}
	const cropFactor = focalLength35mm / focalLength;
	if (cropFactor < 0.5 || cropFactor > 20) return null; // sanity check

	const diagonal = 43.27 / cropFactor;

	// Detect aspect ratio from image dimensions
	let ar = 3 / 2; // default 3:2
	if (imageWidth && imageHeight) {
		const ratio = Math.max(imageWidth, imageHeight) / Math.min(imageWidth, imageHeight);
		if (Math.abs(ratio - 4 / 3) < 0.1) ar = 4 / 3;
		else if (Math.abs(ratio - 16 / 9) < 0.1) ar = 16 / 9;
		else if (Math.abs(ratio - 1) < 0.1) ar = 1;
	}

	const width = diagonal * Math.cos(Math.atan(1 / ar));
	const height = diagonal * Math.sin(Math.atan(1 / ar));

	return {
		width: Math.round(width * 100) / 100,
		height: Math.round(height * 100) / 100,
		source: 'exif'
	};
}

/**
 * Tier 2: Look up sensor size from the Lensfun-derived camera database.
 */
export async function sensorFromDatabase(
	make: string,
	model: string,
	imageWidth?: number,
	imageHeight?: number
): Promise<SensorSize | null> {
	if (!make && !model) return null;

	if (!sensorDb) {
		try {
			const res = await fetch('/camera_sensors.json');
			if (!res.ok) return null;
			sensorDb = await res.json();
		} catch {
			return null;
		}
	}

	const key = `${make} ${model}`.toLowerCase().trim();
	const entry = sensorDb?.[key];
	if (!entry) {
		// Try partial match on model only
		const modelKey = model.toLowerCase().trim();
		const match = Object.entries(sensorDb || {}).find(
			([k]) => k.includes(modelKey) || modelKey.includes(k.split(' ').slice(1).join(' '))
		);
		if (!match) return null;
		const [, matched] = match;
		return computeFromCropfactor(matched.cropfactor, imageWidth, imageHeight);
	}

	return computeFromCropfactor(entry.cropfactor, imageWidth, imageHeight);
}

function computeFromCropfactor(
	cropfactor: number,
	imageWidth?: number,
	imageHeight?: number
): SensorSize {
	const diagonal = 43.27 / cropfactor;

	let ar = 3 / 2;
	if (imageWidth && imageHeight) {
		const ratio = Math.max(imageWidth, imageHeight) / Math.min(imageWidth, imageHeight);
		if (Math.abs(ratio - 4 / 3) < 0.1) ar = 4 / 3;
		else if (Math.abs(ratio - 16 / 9) < 0.1) ar = 16 / 9;
	}

	const width = diagonal * Math.cos(Math.atan(1 / ar));
	const height = diagonal * Math.sin(Math.atan(1 / ar));

	return {
		width: Math.round(width * 100) / 100,
		height: Math.round(height * 100) / 100,
		source: 'database'
	};
}

/**
 * Tier 3: Manual entry -- just wraps user-provided values.
 */
export function sensorFromManual(width: number, height: number): SensorSize {
	return { width, height, source: 'manual' };
}
