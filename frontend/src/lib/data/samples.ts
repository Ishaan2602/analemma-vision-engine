export interface SampleImageData {
	id: string;
	name: string;
	thumbnail: string;
	datetime: string;
	latitude: number;
	longitude: number;
	focalLength: number;
	sensorWidth: number;
	sensorHeight: number;
	sunX?: number;
	sunY?: number;
	license: string;
	author: string;
}

export const SAMPLE_IMAGES: SampleImageData[] = [
	{
		id: 'brofjorden',
		name: 'Brofjorden, Sweden',
		thumbnail: '/samples/brofjorden_thumb.jpg',
		datetime: '2016-09-05T19:38:15',
		latitude: 58.373236,
		longitude: 11.446522,
		focalLength: 17.4,
		sensorWidth: 13.2,
		sensorHeight: 8.8,
		sunX: 986,
		sunY: 308,
		license: 'CC BY-SA 4.0',
		author: 'W.carter'
	},
	{
		id: 'cold_canada',
		name: 'Quebec, Canada',
		thumbnail: '/samples/cold_canada_thumb.jpg',
		datetime: '2009-12-20T10:53:00',
		latitude: 46.809397,
		longitude: -71.2077,
		focalLength: 24,
		sensorWidth: 23.4,
		sensorHeight: 15.6,
		sunX: 702,
		sunY: 215,
		license: 'CC BY 2.0',
		author: 'Emmanuel Huybrechts'
	},
	{
		id: 'hongkong',
		name: 'Hong Kong',
		thumbnail: '/samples/hongkong_thumb.jpg',
		datetime: '2014-09-02T16:20:48',
		latitude: 22.3,
		longitude: 114.2,
		focalLength: 6.1,
		sensorWidth: 7.4,
		sensorHeight: 5.5,
		sunX: 436,
		sunY: 254,
		license: 'CC BY-SA 4.0',
		author: 'Kailanchoi'
	},
	{
		id: 'hunan',
		name: 'Hunan, China',
		thumbnail: '/samples/hunan_thumb.jpg',
		datetime: '2017-12-18T08:25:14',
		latitude: 27.042819,
		longitude: 110.598294,
		focalLength: 3.95,
		sensorWidth: 5.6,
		sensorHeight: 4.2,
		sunX: 473,
		sunY: 130,
		license: 'CC0 1.0',
		author: 'Huangdan2060'
	},
	{
		id: 'sharjah_sands',
		name: 'Sharjah, UAE',
		thumbnail: '/samples/sharjah_sands_thumb.jpg',
		datetime: '2022-05-27T18:40:00',
		latitude: 25.3,
		longitude: 55.5,
		focalLength: 18,
		sensorWidth: 23.6,
		sensorHeight: 15.6,
		sunX: 568,
		sunY: 386,
		license: 'CC BY 4.0',
		author: 'Aleksandr Serebrennikov'
	},
	{
		id: 'russia_meadow',
		name: 'Germany',
		thumbnail: '/samples/russia_meadow_thumb.jpg',
		datetime: '2020-12-29T19:35:00',
		latitude: 49.1713,
		longitude: 8.807494,
		focalLength: 35,
		sensorWidth: 35.9,
		sensorHeight: 24.0,
		sunX: 532,
		sunY: 304,
		license: 'CC BY-SA 4.0',
		author: 'Roman Eisele'
	}
];
