import {defineStore} from 'pinia'
import type {Bundle,ScoreRequest} from './types'
export const useMission=defineStore('mission',{
 state:()=>({mission:'',taskIds:[] as string[],siteId:'',tau:.7,scheme:'roc' as 'roc'|'rank_sum'|'custom',custom:{} as Record<string,number>,excludeKnown:false,step:1}),
 actions:{
  initialize(bundle:Bundle,query:Record<string,unknown>){
   this.mission=bundle.mission.id
   const ids=bundle.tasks.map(t=>t.id)
   const raw=typeof query.tasks==='string'?query.tasks.split(','):ids
   this.taskIds=raw.filter((id,i)=>ids.includes(id)&&raw.indexOf(id)===i)
   this.siteId=bundle.sites.some(s=>s.id===query.site)?String(query.site):bundle.sites[0]!.id
   const tau=Number(query.tau)
   this.tau=Number.isFinite(tau)&&tau>0&&tau<=1?tau:bundle.settings.tau
   this.scheme=['roc','rank_sum','custom'].includes(String(query.weights))?query.weights as typeof this.scheme:bundle.settings.weight_scheme
   this.excludeKnown=query.exclude==='true'
   this.custom=Object.fromEntries(ids.map(id=>[id,1]))
   if(typeof query.custom==='string'){try{const custom=JSON.parse(query.custom);for(const id of ids)if(Number.isFinite(custom[id])&&custom[id]>=0)this.custom[id]=custom[id]}catch{}}
   this.step=query.step==='3'&&this.taskIds.length?3:query.step==='2'?2:1
  },
  toggle(id:string){this.taskIds=this.taskIds.includes(id)?this.taskIds.filter(v=>v!==id):[...this.taskIds,id]},
  request():ScoreRequest{return {mission:this.mission,site_id:this.siteId,task_ids:this.taskIds,weight_scheme:this.scheme,custom_weights:this.scheme==='custom'?Object.fromEntries(this.taskIds.map(id=>[id,this.custom[id]??1])):null,exclude_known:this.excludeKnown,tau:this.tau}},
  query(){return {tasks:this.taskIds.join(','),site:this.siteId,tau:String(this.tau),weights:this.scheme,exclude:String(this.excludeKnown),step:String(this.step),...(this.scheme==='custom'?{custom:JSON.stringify(this.custom)}:{})}}
 }
})
