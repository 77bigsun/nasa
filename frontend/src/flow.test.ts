import {describe,it,expect,vi,beforeEach,afterEach} from 'vitest'
import {mount,flushPromises} from '@vue/test-utils'
import {createPinia,setActivePinia} from 'pinia'
import {createMemoryHistory,createRouter} from 'vue-router'
import {i18n} from './i18n'
import {useMission} from './store'
import MissionPage from './pages/Mission.vue'
import type {Bundle,ScoreResponse,OptimizeResponse} from './types'
import {api} from './api'
vi.mock('./api',()=>({api:{coverage:vi.fn().mockResolvedValue({features:[{feature_id:"M1-f",ready_sites:["moon-scr"]},{feature_id:"M2-f",ready_sites:["moon-scr"]}],targets:{"moon-scr":{usable:["M1-f","M2-f"],context:[]}},mode:"observed"}),bundle:vi.fn(),score:vi.fn(),optimize:vi.fn(),sensitivity:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
const task=(id:string,order:number)=>({id,name:`Test ${id}`,name_en:`Test ${id}`,mission:'moon' as const,verify:'Verify the test',nasa_basis:'NASA',nasa_url:'https://www.nasa.gov/',order,manual_adjust:null,tech_gap:null,features:[{id:id+'-f',name:'Observed feature',name_en:'Observed feature',type:'profile',compare_mode:'absolute',unit:'deg',weight:1,threshold:null,planet_threshold:null,out_of_earth_range:false,earth_proxy:false,planet_data:[],earth_data:[],notes:[],stat:'mean'}],notes:[],weights:{roc:.5,rank_sum:.5}})
const bundle={mission:{id:'moon',name:'Moon mission',name_en:'Moon mission',goal:'Goal',goal_en:'Goal',summary:'Summary',summary_en:'Summary',nasa_sources:[{title:'NASA',url:'https://www.nasa.gov/'}]},tasks:[task('M1',2),task('M2',1)],sites:[{id:'moon-scr',mission:'moon',name:'Shackleton',name_en:'Shackleton',lat:null,lon:null,source:'Team',description:'Demo',description_en:'Demo',coords_status:'todo'}],limits:[],constraints:[],settings:{tau:.7,similar_cutoff:.7,different_cutoff:.4,weight_scheme:'roc',sensitivity:{n_samples:500,seed:42,alpha:1},map:{gibs_url:'',fallback_url:'',max_zoom:8}},categorical_tables:{}} as Bundle
const result={mission:'moon',site_id:'moon-scr',weights:{M1:.25,M2:.75},candidates:[{id:'demo-01',name:'Demo-01',name_en:'Demo-01',lat:36,lon:-116,known_analog:false,is_placeholder:false,overall:null,partial_score:.8,tasks:{}}],task_rankings:[],limits:[],robustness:{status:'insufficient',spearman:null},uses_placeholder:false,warnings:[],tau:.7,data_status:"partial"} as unknown as ScoreResponse
const optimal={minimum_sites:1,selected:['demo-01'],covered_tasks:['M1'],total_tasks:2,uncoverable:['M2'],partial_tasks:[],insufficient_data:[],task_diagnostics:[],feature_network:{minimum_sites:1,selected:['demo-01'],total_features:2,comparable_features:1,covered_features:1,coverage:[],marginal_curve:[]},coverage:[{task_id:'M1',covered_by:[{candidate_id:'demo-01',score:.8}]},{task_id:'M2',covered_by:[]}],marginal_curve:[],objective:.8,uses_placeholder:false} as OptimizeResponse
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
  expect(api.score).toHaveBeenCalled();expect(wrapper.text()).toContain('Available evidence only');expect(wrapper.text()).toContain('Observed products')
  expect(wrapper.text()).toContain('Demo-01');expect(wrapper.text()).toContain('Below threshold (complete data)')
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


describe('Imported target selection',()=>{
 it('compares newly imported Mons Mouton data without redirecting to Shackleton',async()=>{
  const mouton={...bundle.sites[0]!,id:'moon-mouton',name:'Mons Mouton',name_en:'Mons Mouton',lat:-85.416,lon:31.8506}
  vi.mocked(api.bundle).mockResolvedValue({...bundle,sites:[...bundle.sites,mouton]})
  vi.mocked(api.coverage).mockResolvedValueOnce({mode:'observed',features:[{mission:'moon',task_id:'M1',feature_id:'M1-f',name:'Observed feature',planet_sources:[],earth_sources:[],planet_products:[],earth_products:[],status:'paired',ready_sites:['moon-mouton'],observed_sites:['moon-mouton'],reason:'Imported'}],targets:{'moon-scr':{usable:['M1-f'],context:[]},'moon-mouton':{usable:['M1-f'],context:[]}}})
  vi.mocked(api.score).mockResolvedValue({...result,site_id:'moon-mouton'})
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:MissionPage}]})
  await router.push('/moon?site=moon-mouton&tasks=M1&step=3');await router.isReady()
  const wrapper=mount(MissionPage,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,EarthMap:true,DetailsDrawer:true}}})
  await flushPromises();await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(router.currentRoute.value.query.site).toBe('moon-mouton')
  expect(router.currentRoute.value.query.step).toBe('3')
  expect(vi.mocked(api.score).mock.calls.at(-1)![0].site_id).toBe('moon-mouton')
  expect(wrapper.find('[data-testid="result-target-name"]').text()).toContain('Mons Mouton')
  expect(wrapper.find('[data-testid="unimported-target-warning"]').exists()).toBe(false)
  wrapper.unmount()
 })
 it('does not calculate a bookmarked target without measurements or borrow another location',async()=>{
  const pending={...bundle.sites[0]!,id:'moon-mouton',name:'Mons Mouton',name_en:'Mons Mouton'}
  vi.mocked(api.bundle).mockResolvedValue({...bundle,sites:[pending,...bundle.sites]})
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:MissionPage}]})
  await router.push('/moon?site=moon-mouton&tasks=M1,M2&step=3');await router.isReady()
  const wrapper=mount(MissionPage,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,EarthMap:true,DetailsDrawer:true}}})
  await flushPromises()
  expect(router.currentRoute.value.query.site).toBe('moon-mouton')
  expect(router.currentRoute.value.query.step).toBe('2')
  expect(wrapper.find('[data-testid="unimported-target-warning"]').text()).toContain('Mons Mouton')
  expect(wrapper.find('[data-site-id="moon-mouton"] input').attributes('disabled')).toBeDefined()
  expect(api.score).not.toHaveBeenCalled()
  await wrapper.find('[data-testid="unimported-target-warning"] button').trigger('click');await flushPromises()
  expect(wrapper.find('[data-testid="selected-target-summary"]').text()).toContain('Shackleton')
  await wrapper.findAll('button').find(b=>b.text().includes('Calculate similarity'))!.trigger('click')
  await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(vi.mocked(api.score).mock.calls.at(-1)![0].site_id).toBe('moon-scr')
  expect(wrapper.find('[data-testid="result-target-name"]').text()).toContain('Shackleton')
  wrapper.unmount()
 })
 it('replaces empty ranking bars with an explanation and evidence access for context-only data',async()=>{
  vi.mocked(api.coverage).mockResolvedValue({mode:'observed',features:[],targets:{'moon-scr':{usable:[],context:['M1-f']}}})
  vi.mocked(api.score).mockResolvedValue({...result,data_status:'unavailable',candidates:result.candidates.map(c=>({...c,overall:null,partial_score:null}))})
  vi.mocked(api.optimize).mockResolvedValue({...optimal,minimum_sites:0,selected:[],covered_tasks:[],total_tasks:1,uncoverable:[],partial_tasks:[],insufficient_data:['M1'],task_diagnostics:[],feature_network:{minimum_sites:0,selected:[],total_features:1,comparable_features:0,covered_features:0,coverage:[],marginal_curve:[]}})
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/:mission',component:MissionPage}]})
  await router.push('/moon?site=moon-scr&tasks=M1&step=3');await router.isReady()
  const wrapper=mount(MissionPage,{global:{plugins:[createPinia(),router,i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,EarthMap:true,DetailsDrawer:true}}})
  await flushPromises();await new Promise(resolve=>setTimeout(resolve,350));await flushPromises()
  expect(wrapper.find('[data-testid="no-comparable-results"]').text()).toContain('Shackleton')
  expect(wrapper.findAll('.ranking-row')).toHaveLength(0)
  expect(wrapper.find('[data-testid="no-comparable-results"]').text()).toContain('Inspect imported evidence')
  wrapper.unmount()
 })
})
