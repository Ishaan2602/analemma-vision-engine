import exifr from 'exifr';

export interface ExifData {
	datetime?: string;
	latitude?: number;
	longitude?: number;
	focalLength?: number;
	focalLength35mm?: number;
	make?: string;
	model?: string;
	imageWidth?: number;
	imageHeight?: number;
}

export async function extractExif(file: File): Promise<ExifData> {
	try {
		const tags = await exifr.parse(file, {
			pick: [
				'DateTimeOriginal',
				'GPSLatitude',
				'GPSLongitude',
				'FocalLength',
				'FocalLengthIn35mmFormat',
				'Make',
				'Model',
				'ImageWidth',
				'ImageHeight',
				'ExifImageWidth',
				'ExifImageHeight'
			],
			gps: true
		});

		if (!tags) return {};

		let datetime: string | undefined;
		if (tags.DateTimeOriginal) {
			const d =
				tags.DateTimeOriginal instanceof Date
					? tags.DateTimeOriginal
					: new Date(tags.DateTimeOriginal);
			if (!isNaN(d.getTime())) {
				// Format as local ISO datetime for the datetime-local input
				const pad = (n: number) => String(n).padStart(2, '0');
				datetime = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
			}
		}

		return {
			datetime,
			latitude: tags.latitude ?? undefined,
			longitude: tags.longitude ?? undefined,
			focalLength: tags.FocalLength ?? undefined,
			focalLength35mm: tags.FocalLengthIn35mmFormat ?? undefined,
			make: tags.Make ?? undefined,
			model: tags.Model ?? undefined,
			imageWidth: tags.ExifImageWidth ?? tags.ImageWidth ?? undefined,
			imageHeight: tags.ExifImageHeight ?? tags.ImageHeight ?? undefined
		};
	} catch {
		return {};
	}
}
