import {describe,it,expect,vi,beforeEach,afterEach} from 'vitest'
import {mount,flushPromises} from '@vue/test-utils'
import {createPinia,setActivePinia} from 'pinia'
import {createMemoryHistory,createRouter} from 'vue-router'
import {i18n} from './i18n'
import {useMission} from './store'
import MissionPage from './pages/Mission.vue'
import type {Bundle,ScoreResponse,OptimizeResponse} from './types'
import {api} from './api'
vi.mock('./api',()=>({api:{bundle:vi.fn(),score:vi.fn(),optimize:vi.fn(),sensitivity:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
const task=(id:string,order:number)=>({id,name:`Test ${id}`,name_en:`Test ${id}`,mission:'moon' as const,verify:'Verify the test',nasa_basis:'NASA',nasa_url:'https://www.nasa.gov/',order,manual_adjust:null,tech_gap:null,features:[],notes:[],weights:{roc:.5,rank_sum:.5}})
const bundle={mission:{id:'moon',name:'Moon mission',name_en:'Moon mission',goal:'Goal',goal_en:'Goal',summary:'Summary',summary_en:'Summary',nasa_sources:[{title:'NASA',url:'https://www.nasa.gov/'}]},tasks:[task('M1',2),task('M2',1)],sites:[{id:'moon-scr',mission:'moon',name:'Shackleton',name_en:'Shackleton',lat:null,lon:null,source:'Team',description:'Demo',description_en:'Demo',coords_status:'todo'}],limits:[],constraints:[],settings:{tau:.7,similar_cutoff:.7,different_cutoff:.4,weight_scheme:'roc',sensitivity:{n_samples:500,seed:42,alpha:1},map:{gibs_url:'',fallback_url:'',max_zoom:8}},categorical_tables:{}} as Bundle
const result={mission:'moon',site_id:'moon-scr',weights:{M1:.25,M2:.75},candidates:[{id:'demo-01',name:'Demo-01',name_en:'Demo-01',lat:36,lon:-116,known_analog:false,is_placeholder:true,overall:.8,tasks:{}}],task_rankings:[],limits:[],robustness:{status:'insufficient',spearman:null},uses_placeholder:true,warnings:[],tau:.7} as unknown as ScoreResponse
const optimal={minimum_sites:1,selected:['demo-01'],covered_tasks:['M1'],total_tasks:2,uncoverable:['M2'],coverage:[{task_id:'M1',covered_by:[{candidate_id:'demo-01',score:.8}]},{task_id:'M2',covered_by:[]}],marginal_curve:[],objective:.8,uses_placeholder:true} as OptimizeResponse
beforeEach(()=>{i18n.global.locale.value='en';setActivePinia(createPinia());vi.mocked(api.bundle).mockResolvedValue(bundle);vi.mocked(api.score).mockResolvedValue(result);vi.mocked(api.optimize).mockResolvedValue(optimal);window.scrollTo=vi.fn()})
afterEach(()=>{vi.useRealTimers();vi.clearAllMocks()})
describe('URL selection contract',()=>{
 it('restores shared settings, validates unknown values and preserves custom weights',()=>{
  const state=useMission();state.initialize(bundle,{tasks:'M2,invalid,M2',site:'bad',tau:'bad',weights:'custom',custom:'{"M2":4}',step:'3',exclude:'true'})
  expect(state.taskIds).toEqual(['M2']);expect(state.siteId).toBe('moon-scr');expect(state.tau).toBe(.7)
  expect(state.request().custom_weights).toEqual({M2:4});expect(state.step).toBe(3);expect(state.excludeKnown).toBe(true)
  expect(state.query().tasks).toBe('M2')
 })
})
describe('Mission wizard',()=>{
 it('selects tests, advances to one target and renders flagged results',async()=>{
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:MissionPage}]})
  await router.push('/moon');await router.isReady()
  const wrapper=mount(MissionPage,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,EarthMap:true,DetailsDrawer:true}}})
  await flushPromises()
  expect(wrapper.text()).toContain('Test M1')
  const checks=wrapper.findAll('input[type="checkbox"]');expect(checks).toHaveLength(2)
  await checks[0]!.setValue(false)
  const next=wrapper.findAll('button').find(b=>b.text().includes('Continue'))!;await next.trigger('click');await flushPromises()
  expect(wrapper.find('input[type="radio"]').exists()).toBe(true)
  await wrapper.findAll('button').find(b=>b.text().includes('Calculate similarity'))!.trigger('click')
  await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(api.score).toHaveBeenCalled();expect(wrapper.text().toLowerCase()).toContain('placeholder')
  expect(wrapper.text()).toContain('Demo-01');expect(wrapper.text()).toContain('Uncoverable')
  expect(router.currentRoute.value.query.tasks).toBe('M2')
  wrapper.unmount()
 })
 it('blocks progression with no selected tests',async()=>{
  const state=useMission();state.initialize(bundle,{tasks:''});expect(state.taskIds).toEqual([])
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:MissionPage}]})
  await router.push('/moon?tasks=');await router.isReady()
  const wrapper=mount(MissionPage,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'}}}})
  await flushPromises();expect(wrapper.findAll('button').find(b=>b.text().includes('Continue'))!.attributes('disabled')).toBeDefined();expect(wrapper.text()).toContain('Select at least one test.')
  wrapper.unmount()
 })
})
