import axios from 'axios'
import type {Bundle,Mission,Facts,DataSource,ScoreRequest,ScoreResponse,OptimizeResponse,SensitivityResponse,SeriesResponse} from './types'
const catalog=axios.create({baseURL:'/api/catalog',timeout:15000})
const similarity=axios.create({baseURL:'/api/similarity',timeout:120000})
const planning=axios.create({baseURL:'/api/planning',timeout:120000})
export const api={
 missions:()=>catalog.get<Mission[]>('/missions').then(r=>r.data),
 bundle:(id:string)=>catalog.get<Bundle>(`/missions/${id}/bundle`).then(r=>r.data),
 facts:()=>catalog.get<Facts>('/earth-facts').then(r=>r.data),
 sources:()=>catalog.get<DataSource[]>('/data-sources').then(r=>r.data),
 method:()=>catalog.get<{settings:Record<string,unknown>;markdown:string}>('/method').then(r=>r.data),
 score:(r:ScoreRequest,signal?:AbortSignal)=>similarity.post<ScoreResponse>('/score',r,{signal}).then(r=>r.data),
 optimize:(r:ScoreRequest,signal?:AbortSignal)=>planning.post<OptimizeResponse>('/optimize',r,{signal}).then(r=>r.data),
 sensitivity:(r:ScoreRequest,n_samples:number,seed:number,alpha:number)=>planning.post<SensitivityResponse>('/sensitivity',{...r,n_samples,seed,alpha}).then(r=>r.data),
 series:(candidate:string,feature:string,site:string,mission:string)=>similarity.get<SeriesResponse>(`/candidates/${candidate}/series/${feature}`,{params:{site_id:site,mission}}).then(r=>r.data)
}
export function errorMessage(error:unknown):string {
 if(axios.isAxiosError(error)){const d=error.response?.data?.detail;return typeof d==='string'?d: error.message}
 return error instanceof Error?error.message:String(error)
}
