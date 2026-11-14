/** Keep candidate points on one continuous longitude arc across the date line. */
export function candidateMapPoints<T extends {id:string;lat:number;lon:number}>(candidates:T[]){
 if(!candidates.length)return []
 const longitude=(lon:number)=>((lon%360)+360)%360
 const sorted=candidates.map(c=>longitude(c.lon)).sort((a,b)=>a-b)
 let gap=-1,start=sorted[0]!
 for(let i=0;i<sorted.length;i++){
  const next=i+1<sorted.length?sorted[i+1]!:sorted[0]!+360
  if(next-sorted[i]!>gap){gap=next-sorted[i]!;start=next%360}
 }
 return candidates.map(candidate=>{
  const lon=longitude(candidate.lon)
  return {candidate,longitude:lon<start?lon+360:lon}
 })
}

/** Padded overview coordinates; polar targets stay away from clipped SVG edges. */
export function targetMapPoint(lat:number,lon:number,polar:boolean){
 if(polar){
  const radius=(90+lat)/15*130,angle=lon*Math.PI/180
  return {x:300+radius*Math.sin(angle),y:164-radius*Math.cos(angle)}
 }
 const longitude=((lon+180)%360+360)%360-180
 return {x:38+(longitude+180)/360*524,y:38+(90-lat)/180*224}
}
