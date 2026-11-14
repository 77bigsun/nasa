import type {Bundle,MeasurementCoverage} from './types'

export function targetEvidence(coverage:MeasurementCoverage|undefined,siteId:string,featureIds?:string[]){
 const target=coverage?.targets[siteId]
 const requested=featureIds?new Set(featureIds):undefined
 const relevant=(id:string)=>!requested||requested.has(id)
 const ready=new Set(coverage?.features.filter(f=>f.ready_sites.includes(siteId)).map(f=>f.feature_id)||[])
 const comparableIds=(target?.usable||[]).filter(id=>ready.has(id)&&relevant(id))
 const contextIds=[...new Set([...(target?.usable||[]),...(target?.context||[])])].filter(id=>!comparableIds.includes(id)&&relevant(id))
 return {imported:!!target,comparableIds,contextIds}
}

export function preferredTarget(bundle:Bundle,taskIds:string[],coverage:MeasurementCoverage){
 const featureIds=bundle.tasks.filter(t=>taskIds.includes(t.id)).flatMap(t=>t.features.map(f=>f.id))
 return [...bundle.sites].sort((a,b)=>{
  const x=targetEvidence(coverage,a.id,featureIds),y=targetEvidence(coverage,b.id,featureIds)
  return y.comparableIds.length-x.comparableIds.length||y.contextIds.length-x.contextIds.length||Number(y.imported)-Number(x.imported)
 })[0]
}
