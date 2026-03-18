export function isHeic(file: File): boolean {
	return (
		file.type === 'image/heic' ||
		file.type === 'image/heif' ||
		file.name.toLowerCase().endsWith('.heic') ||
		file.name.toLowerCase().endsWith('.heif')
	);
}

export async function convertHeicToJpeg(file: File): Promise<Blob> {
	const heic2any = (await import('heic2any')).default;
	const blob = await heic2any({ blob: file, toType: 'image/jpeg', quality: 0.85 });
	return Array.isArray(blob) ? blob[0] : blob;
}
