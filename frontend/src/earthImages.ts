import manifest from './earthSiteImages.json'
export type EarthImage = typeof manifest.images[number]
export function earthImageAt(lat:number,lon:number):EarthImage|undefined {
 if(!Number.isFinite(lat)||!Number.isFinite(lon))return undefined
 const covers=(image:EarthImage)=>image.bbox[0]!<=lat&&lat<=image.bbox[2]!&&[-360,0,360].some(shift=>image.bbox[1]!<=lon+shift&&lon+shift<=image.bbox[3]!)
 const exact=(image:EarthImage)=>Math.abs(image.lat-lat)<.00001&&Math.abs((((image.lon-lon)+540)%360)-180)<.00001
 // Prefer original supplied imagery, then an exact centre, then a verified
 // enclosing footprint. Place labels are deliberately not used as keys.
 return manifest.images.filter(covers).sort((a,b)=>
  Number(exact(b))-Number(exact(a))||Number(a.origin!=='provided')-Number(b.origin!=='provided')||
  (a.bbox[2]!-a.bbox[0]!)*(a.bbox[3]!-a.bbox[1]!)-(b.bbox[2]!-b.bbox[0]!)*(b.bbox[3]!-b.bbox[1]!)
 )[0]
}
