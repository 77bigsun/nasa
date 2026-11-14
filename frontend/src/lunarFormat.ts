import {i18n,localizeData} from './i18n'
import type {LunarEarthCandidate} from './lunarHandoffTypes'
export function lunarCandidateName(candidate:Pick<LunarEarthCandidate,'name_en'|'lat'|'lon'>,locale:string){
 return /^(?:Grid cell\b|-?\d)/.test(candidate.name_en)?i18n.global.t('lunarGridCell',{lat:candidate.lat,lon:candidate.lon}):localizeData(candidate.name_en,locale)
}
