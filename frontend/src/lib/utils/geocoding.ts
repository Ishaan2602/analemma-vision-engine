const TOKEN = import.meta.env.VITE_LOCATIONIQ_TOKEN;

export interface GeocodingResult {
	displayName: string;
	latitude: number;
	longitude: number;
}

const cache = new Map<string, GeocodingResult[]>();

export async function autocomplete(query: string): Promise<GeocodingResult[]> {
	if (query.length < 3) return [];

	const cacheKey = query.toLowerCase().trim();
	if (cache.has(cacheKey)) return cache.get(cacheKey)!;

	const url = `https://api.locationiq.com/v1/autocomplete?key=${encodeURIComponent(TOKEN)}&q=${encodeURIComponent(query)}&tag=place:city,place:town&limit=5&dedupe=1`;

	try {
		const res = await fetch(url);
		if (!res.ok) return [];
		const data = await res.json();
		const results: GeocodingResult[] = data.map(
			(item: { display_name: string; lat: string; lon: string }) => ({
				displayName: item.display_name,
				latitude: parseFloat(item.lat),
				longitude: parseFloat(item.lon)
			})
		);
		cache.set(cacheKey, results);
		return results;
	} catch {
		return [];
	}
}
