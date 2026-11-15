import axios from 'axios'
import type {Bundle,Mission,Facts,DataSource,ScoreRequest,ScoreResponse,OptimizeResponse,SensitivityResponse,SeriesResponse,DatasetProduct,ResearchSection,ObservedPilot,MeasurementCoverage} from './types'
import type {LunarHandoffCatalog,LunarTaskComparison,LunarTaskId} from './lunarHandoffTypes'
import type {MarsCatalog,MarsComparison,MarsNetwork,MarsGlobalGrid} from './marsHandoffTypes'
const catalog=axios.create({baseURL:'/api/catalog',timeout:15000})
const similarity=axios.create({baseURL:'/api/similarity',timeout:120000})
const measurements=axios.create({baseURL:'/api/measurements',timeout:15000})
const planning=axios.create({baseURL:'/api/planning',timeout:120000})
export const api={
 marsHandoff:()=>catalog.get<MarsCatalog>('/mars-handoff').then(r=>r.data),
 marsComparison:(site:string,tasks:string[],signal?:AbortSignal)=>similarity.get<MarsComparison>('/mars/compare',{params:{site_id:site,tasks:tasks.join(',')},signal}).then(r=>r.data),
 marsNetwork:(site:string,tasks:string[]=[],signal?:AbortSignal)=>planning.get<MarsNetwork>('/mars/network',{params:{site_id:site,tasks:tasks.join(',')},signal}).then(r=>r.data),
 marsGrid:(signal?:AbortSignal)=>measurements.get<MarsGlobalGrid>('/mars-grid',{signal}).then(r=>r.data),
 lunarHandoff:()=>catalog.get<LunarHandoffCatalog>('/lunar-handoff').then(r=>r.data),
 lunarTask:(task:LunarTaskId,site:string,signal?:AbortSignal)=>similarity.get<LunarTaskComparison>(`/lunar/tasks/${task}`,{params:{site_id:site},signal}).then(r=>r.data),
 missions:()=>catalog.get<Mission[]>('/missions').then(r=>r.data),
 bundle:(id:string)=>catalog.get<Bundle>(`/missions/${id}/bundle`,{params:id==='moon'?{profile:'lunar_pdf'}:undefined}).then(r=>r.data),
 facts:()=>catalog.get<Facts>('/earth-facts').then(r=>r.data),
 datasets:()=>catalog.get<DatasetProduct[]>('/datasets').then(r=>r.data),
 research:()=>catalog.get<ResearchSection[]>('/research').then(r=>r.data),
 coverage:(profile?:string)=>profile==='lunar_pdf'?similarity.get<MeasurementCoverage>('/lunar/coverage').then(r=>r.data):measurements.get<MeasurementCoverage>('/coverage').then(r=>r.data),
 observations:()=>measurements.get<ObservedPilot>('/observations').then(r=>r.data).catch(e=>{if(axios.isAxiosError(e)&&e.response?.status===404)return null;throw e}),
 sources:()=>catalog.get<DataSource[]>('/data-sources').then(r=>r.data),
 method:()=>catalog.get<{settings:Record<string,unknown>;markdown:string;markdown_zh?:string}>('/method').then(r=>r.data),
 score:(r:ScoreRequest,signal?:AbortSignal)=>similarity.post<ScoreResponse>('/score',r,{signal}).then(r=>r.data),
 optimize:(r:ScoreRequest,signal?:AbortSignal)=>planning.post<OptimizeResponse>('/optimize',r,{signal}).then(r=>r.data),
 sensitivity:(r:ScoreRequest,n_samples:number,seed:number,alpha:number)=>planning.post<SensitivityResponse>('/sensitivity',{...r,n_samples,seed,alpha}).then(r=>r.data),
 series:(candidate:string,feature:string,site:string,mission:string)=>similarity.get<SeriesResponse>(`/candidates/${candidate}/series/${feature}`,{params:{site_id:site,mission}}).then(r=>r.data)
}
export function errorMessage(error:unknown):string {
 if(axios.isAxiosError(error)){const d=error.response?.data?.detail;return typeof d==='string'?d: error.message}
 return error instanceof Error?error.message:String(error)
}
