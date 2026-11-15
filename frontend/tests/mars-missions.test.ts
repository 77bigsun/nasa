import {beforeEach,afterEach,describe,it,expect,vi} from 'vitest'
import {mount,flushPromises,enableAutoUnmount} from '@vue/test-utils'
import {createRouter,createMemoryHistory} from 'vue-router'
import MarsMission from '../src/pages/MarsMission.vue'
import MarsEvidenceDrawer from '../src/components/MarsEvidenceDrawer.vue'
import {api} from '../src/api'
import {i18n,setContentTranslations} from '../src/i18n'
import raw from '../../data/mars/handoff/results.json'
import translations from '../../data/locales/mars-handoff.zh-TW.json'
import type {MarsComparison,MarsCatalog,MarsNetwork} from '../src/marsHandoffTypes'
vi.mock('../src/api',()=>({api:{marsHandoff:vi.fn(),marsComparison:vi.fn(),marsNetwork:vi.fn(),marsGrid:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
enableAutoUnmount(afterEach)
const catalog={meta:raw.meta,tasks:raw.tasks,mars_sites:raw.mars_sites} as unknown as MarsCatalog
function response(siteId:string,tasks:string[]):MarsComparison{
 const site=raw.mars_sites.find(s=>s.id===siteId)!
 const rankings=raw.task_rankings as unknown as Record<string,Record<string,{new_candidates:Array<{features:Array<{feature:string}>}>}>>
 return {version:raw.meta.version,generated:raw.meta.generated,site,groups:tasks.map(id=>{
  const task=catalog.tasks[id]!;const ranking=rankings[id]?.[siteId]??null
  const features=ranking?task.features.filter(f=>ranking.new_candidates[0]!.features.some(s=>s.feature===f.id)):task.features
  return {task_id:id,task:{...task,features},status:site.test_status[id as keyof typeof site.test_status],ranking}
 }),profile:raw.profile_rankings[siteId as keyof typeof raw.profile_rankings],validation:raw.validation.summary} as unknown as MarsComparison
}
beforeEach(()=>{
 vi.clearAllMocks();i18n.global.locale.value='en';setContentTranslations(translations)
 vi.mocked(api.marsHandoff).mockResolvedValue(catalog)
 vi.mocked(api.marsComparison).mockImplementation(async(site,tasks)=>response(site,tasks))
 vi.mocked(api.marsNetwork).mockResolvedValue({version:raw.meta.version,scope:'mars-jezero',ratio:.9,n_requirements:3,k_star:1,sites:[],skipped:[],uncoverable:[],marginal_curve:[]} as unknown as MarsNetwork)
})
async function open(path:string){
 const router=createRouter({history:createMemoryHistory(),routes:[{path:'/mars',component:MarsMission},{path:'/:pathMatch(.*)*',component:{template:'<div>Other</div>'}}]})
 await router.push(path);await router.isReady()
 const wrapper=mount(MarsMission,{global:{plugins:[router,i18n],stubs:{EarthMap:true,PlanetTargetMap:true}}})
 await flushPromises();return {wrapper,router}
}
describe('Source-native Mars explorer',()=>{
 it('keeps the three-step workflow and uses the seven new study areas',async()=>{
  const {wrapper,router}=await open('/mars')
  expect(wrapper.findAll('[data-task-id]')).toHaveLength(6)
  expect(api.marsComparison).not.toHaveBeenCalled()
  await wrapper.find('.step-actions .primary').trigger('click');await flushPromises()
  expect(wrapper.findAll('[data-site-id]')).toHaveLength(7)
  await wrapper.find('[data-site-id="mars-gale"]').trigger('click');await flushPromises()
  expect(router.currentRoute.value.query.site).toBe('mars-gale')
  expect(wrapper.find('[data-site-id="mars-gale"]').text()).toContain('-5.4')
  await wrapper.find('.step-actions .primary').trigger('click');await flushPromises()
  expect(api.marsComparison).toHaveBeenLastCalledWith('mars-gale',['R1','R4','R6'],expect.any(AbortSignal))
  expect(wrapper.find('[data-testid="mars-most"]').findAll('.mars-earth-card')).toHaveLength(3)
  expect(wrapper.find('[data-testid="mars-least"]').findAll('.mars-earth-card')).toHaveLength(3)
 })
 it('shows exact source scores, evidence, conditional features and bilingual content',async()=>{
  const {wrapper}=await open('/mars?step=3&site=mars-jezero&tasks=R1,R4,R6')
  expect(wrapper.find('[data-testid="mars-most"]').text()).toContain('98.5')
  await wrapper.find('[data-testid="mars-most"] .mars-earth-card').trigger('click');await flushPromises()
  const drawer=wrapper.findComponent(MarsEvidenceDrawer)
  expect(drawer.text()).toContain('10.608')
  expect(drawer.text()).toContain('Earth ATI percentile (0-1)')
  expect(drawer.findAll('.feature-detail')).toHaveLength(6)
  await drawer.find('.icon-button').trigger('click');await flushPromises()
  await wrapper.find('button.language').trigger('click');await flushPromises()
  expect(wrapper.find('[data-testid="mars-task-comparison"]').text()).toContain(translations['Landing surface'])
  expect(wrapper.find('[data-testid="mars-network"]').text()).toContain(i18n.global.t('marsNetworkRule'))
 })
 it('distinguishes unscored R2 and inapplicable ice tests without zero or borrowed rankings',async()=>{
  const {wrapper,router}=await open('/mars?step=3&site=mars-jezero&tasks=R2,R3')
  expect(wrapper.find('[data-testid="mars-unscored"]').text()).toContain('image texture')
  expect(wrapper.find('[data-testid="mars-most"]').exists()).toBe(false)
  await router.replace({query:{step:'3',site:'mars-jezero',tasks:'R2,R3',test:'R3'}});await flushPromises()
  expect(wrapper.find('[data-testid="mars-unscored"]').text()).toContain('SWIM Ci')
  await router.replace({query:{step:'3',site:'mars-arcadia',tasks:'R3'}});await flushPromises()
  expect(wrapper.find('[data-testid="mars-most"]').exists()).toBe(true)
 })
 it('ignores stale replies and keeps URL state meaningful when a target is unknown',async()=>{
  const pending=new Map<string,(data:MarsComparison)=>void>()
  vi.mocked(api.marsComparison).mockImplementation(site=>new Promise(resolve=>pending.set(site,resolve)))
  const {wrapper,router}=await open('/mars?step=3&site=mars-jezero&tasks=R1')
  await router.replace({query:{step:'3',site:'mars-gale',tasks:'R1'}});await flushPromises()
  pending.get('mars-gale')!(response('mars-gale',['R1']));await flushPromises()
  pending.get('mars-jezero')!(response('mars-jezero',['R1']));await flushPromises()
  expect(wrapper.find('[data-testid="mars-most"]').text()).toContain('97.6')
  expect(wrapper.find('[data-testid="mars-most"]').text()).not.toContain('98.5')
  await router.replace({query:{step:'3',site:'mars-utopia',tasks:'R1'}});await flushPromises()
  expect(wrapper.find('[role="alert"]').text()).toContain('not in the current seven-site handoff')
  expect(wrapper.find('[data-testid="mars-most"]').exists()).toBe(false)
 })
})
