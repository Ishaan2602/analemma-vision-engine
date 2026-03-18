const API_URL = import.meta.env.VITE_API_URL;

export interface AnchorPoint {
	pixel_x: number;
	pixel_y: number;
	date: string;
	altitude: number;
	azimuth: number;
}

export interface AnalemmaPoint {
	pixel_x: number;
	pixel_y: number;
	date: string;
	altitude: number;
	azimuth: number;
}

export interface AnalemmaMetadata {
	latitude: number;
	longitude: number;
	timezone: string;
	time_of_day: string;
}

export interface AnalyzeResponse {
	image_width: number;
	image_height: number;
	anchor_point: AnchorPoint;
	points: AnalemmaPoint[];
	metadata: AnalemmaMetadata;
}

export interface SampleImage {
	id: string;
	name: string;
	thumbnail: string;
	datetime: string;
	latitude: number;
	longitude: number;
	focal_length_mm: number;
	sensor_width_mm: number;
	sensor_height_mm: number;
	license: string;
	author: string;
}

export async function analyzeImage(formData: FormData): Promise<AnalyzeResponse> {
	const res = await fetch(`${API_URL}/api/analyze`, {
		method: 'POST',
		body: formData
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
		throw new Error(err.detail || 'Analysis failed');
	}
	return res.json();
}

export async function renderOverlay(formData: FormData): Promise<Blob> {
	const res = await fetch(`${API_URL}/api/render`, {
		method: 'POST',
		body: formData
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: 'Render failed' }));
		throw new Error(err.detail || 'Render failed');
	}
	return res.blob();
}

export async function fetchSamples(): Promise<SampleImage[]> {
	const res = await fetch(`${API_URL}/api/samples`);
	if (!res.ok) return [];
	return res.json();
}
