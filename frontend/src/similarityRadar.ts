export interface RadarFeature {id:string;name:string;s:number|null}
export function observedRadarFeatures(features:RadarFeature[]){
 return features.filter((f):f is RadarFeature&{s:number}=>f.s!==null&&Number.isFinite(f.s)&&f.s>=0&&f.s<=1)
}
