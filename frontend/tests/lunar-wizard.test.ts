import {beforeEach,describe,expect,it,vi} from 'vitest'
import {flushPromises,mount} from '@vue/test-utils'
import {createPinia} from 'pinia'
import {createMemoryHistory,createRouter} from 'vue-router'
import Mission from '../src/pages/Mission.vue'
import DetailsDrawer from '../src/components/DetailsDrawer.vue'
import {api} from '../src/api'
import {i18n} from '../src/i18n'
import type {Bundle,MeasurementCoverage,OptimizeResponse,ScoreResponse} from '../src/types'
import method from '../../data/catalog/lunar-method.json'
vi.mock('../src/api',()=>({api:{bundle:vi.fn(),coverage:vi.fn(),score:vi.fn(),optimize:vi.fn(),sensitivity:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
const features=method.features.map(f=>({id:f.id,name:f.name,name_en:f.name,type:'profile',compare_mode:'absolute',unit:f.unit,weight:1,threshold:null,planet_threshold:null,out_of_earth_range:false,earth_proxy:false,planet_data:[],earth_data:[],notes:[f.note],stat:'mean'}))
const tasks=method.tasks.map((t,i)=>({id:t.id,mission:'moon',name:t.name,name_en:t.name,verify:t.name,nasa_basis:'Team PDF',nasa_url:'/docs/lunar-method-2026-11-14.pdf',tech_gap:null,order:i+1,manual_adjust:null,notes:[],features:features.filter(f=>t.features.includes(f.id)),weights:{roc:t.weight,rank_sum:.25}}))
const sites=[{id:'moon-scr',name:'Connecting Ridge',lat:-89.4,lon:222.9},{id:'moon-mouton',name:'Mons Mouton',lat:-85.416,lon:31.85}].map(s=>({...s,name_en:s.name,mission:'moon',source:'Published point',description:'Study window',description_en:'Study window',coords_status:'approx'}))
const bundle={mission:{id:'moon',name:'Moon mission',name_en:'Moon mission',goal:'Goal',goal_en:'Goal',summary:'Summary',summary_en:'Summary',nasa_sources:[]},tasks,sites,limits:[],constraints:[],settings:{scoring_profile:'lunar_pdf',tau:.7,weight_scheme:'roc',similar_cutoff:.7,different_cutoff:.4,sensitivity:{n_samples:500,seed:42,alpha:1},map:{gibs_url:'',fallback_url:'',max_zoom:8}},categorical_tables:{}} as Bundle
const coverage={mode:'reported',targets:{'moon-scr':{usable:features.map(f=>f.id),context:[]},'moon-mouton':{usable:features.filter(f=>!['slope_histogram','relief'].includes(f.id)).map(f=>f.id),context:[]}},features:features.map(f=>({mission:'moon',task_id:method.features.find(d=>d.id===f.id)!.task,feature_id:f.id,name:f.name,planet_sources:[],earth_sources:[],planet_products:[],earth_products:[],status:'paired',ready_sites:['slope_histogram','relief'].includes(f.id)?['moon-scr']:sites.map(s=>s.id),observed_sites:sites.map(s=>s.id),reason:'PDF data'}))} as MeasurementCoverage
const candidate={id:'HAWAII_MAUNAKEA',name:'Mauna Kea',name_en:'Mauna Kea',lat:19.82,lon:-155.47,known_analog:true,is_placeholder:false,overall:null,partial_score:.3577,tasks:Object.fromEntries(tasks.map(t=>[t.id,{score:t.id==='M4'?.947:null,partial_score:.4,complete:t.id==='M4',available_features:t.features.length,total_features:t.features.length,not_reproducible:[],different:[],similar:[],features:[]}]))}
const score={profile:'lunar_pdf',mission:'moon',site_id:'moon-scr',weights:{M2:.183,M3:.429,M4:.28,M6:.108},candidates:[candidate],task_rankings:[],limits:[],robustness:{status:'pdf_anchor_sensitivity_available',spearman:null},uses_placeholder:false,warnings:[],tau:.7,evidence_mode:'reported',data_status:'partial'} as ScoreResponse
const plan={minimum_sites:1,selected:[candidate.id],covered_tasks:['M4'],total_tasks:4,uncoverable:['M2'],partial_tasks:['M3','M6'],insufficient_data:[],task_diagnostics:[],feature_network:{minimum_sites:1,selected:[candidate.id],total_features:10,comparable_features:10,covered_features:2,coverage:[],marginal_curve:[]},coverage:[],marginal_curve:[],objective:.28,uses_placeholder:false} as OptimizeResponse
beforeEach(()=>{vi.clearAllMocks();i18n.global.locale.value='en';window.scrollTo=vi.fn();vi.mocked(api.bundle).mockResolvedValue(bundle);vi.mocked(api.coverage).mockResolvedValue(coverage);vi.mocked(api.score).mockImplementation(async r=>({...score,site_id:r.site_id}));vi.mocked(api.optimize).mockResolvedValue(plan)})
async function open(path='/moon'){
 const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:Mission}]});await router.push(path);await router.isReady()
 const wrapper=mount(Mission,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'},EarthMap:true,Chart:true,DetailsDrawer:true}}})
 await flushPromises();return {wrapper,router}
}
describe('Original mission design with PDF scoring',()=>{
 it('keeps all three wizard steps, ranking rows and the drawer while requesting PDF scores',async()=>{
  const {wrapper}=await open()
  expect(wrapper.findAll('.wizard-nav button')).toHaveLength(3)
  expect(wrapper.findAll('.task-card')).toHaveLength(4)
  expect(wrapper.find('.lunar-study').exists()).toBe(false)
  await wrapper.findAll('button').find(b=>b.text().includes('Continue'))!.trigger('click');await flushPromises()
  expect(wrapper.findAll('.site-card')).toHaveLength(2)
  await wrapper.findAll('button').find(b=>b.text().includes('Calculate similarity'))!.trigger('click')
  await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(vi.mocked(api.score).mock.calls.at(-1)![0]).toMatchObject({profile:'lunar_pdf',site_id:'moon-scr',task_ids:['M2','M3','M4','M6']})
  expect(wrapper.find('.ranking-row').text()).toContain('Mauna Kea')
  expect(wrapper.text()).toContain('data-fitness aggregation')
  await wrapper.find('.ranking-row').trigger('click')
  expect(wrapper.findComponent(DetailsDrawer).props('lunarProfile')).toBe(true)
  await wrapper.find('select').setValue('custom');await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(vi.mocked(api.score).mock.calls.at(-1)![0].custom_weights).toEqual({M2:1,M3:1,M4:1,M6:1})
  wrapper.unmount()
 })
 it('keeps a shared target selection and its partial-data path instead of redirecting to Connecting Ridge',async()=>{
  const {wrapper,router}=await open('/moon?site=moon-mouton&tasks=M4,M6&step=3')
  await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(router.currentRoute.value.query.site).toBe('moon-mouton')
  expect(router.currentRoute.value.query.step).toBe('3')
  expect(vi.mocked(api.score).mock.calls.at(-1)![0]).toMatchObject({profile:'lunar_pdf',site_id:'moon-mouton',task_ids:['M4','M6']})
  expect(wrapper.find('[data-testid="result-target-name"]').text()).toContain('Mons Mouton')
  wrapper.unmount()
 })
})
