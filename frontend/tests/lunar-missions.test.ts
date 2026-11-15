import {beforeEach,afterEach,describe,it,expect,vi} from 'vitest'
import {mount,flushPromises,enableAutoUnmount} from '@vue/test-utils'
import {createRouter,createMemoryHistory} from 'vue-router'
import LunarMission from '../src/pages/LunarMission.vue'
import LunarEvidenceDrawer from '../src/components/LunarEvidenceDrawer.vue'
import LunarSiteDialog from '../src/components/LunarSiteDialog.vue'
import {api} from '../src/api'
import {i18n,setContentTranslations} from '../src/i18n'
import catalogData from '../../data/catalog/lunar-handoff.json'
import rankingData from '../../data/lunar/handoff/rankings.json'
import translations from '../../data/locales/lunar-handoff.zh-TW.json'
import sourceTranslations from '../../data/locales/lunar-handoff-source.zh-TW.json'
import type {LunarHandoffCatalog,LunarTaskComparison,LunarTaskId} from '../src/lunarHandoffTypes'
vi.mock('../src/api',()=>({api:{lunarHandoff:vi.fn(),lunarTask:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
const catalog=catalogData as LunarHandoffCatalog
enableAutoUnmount(afterEach)
function result(id:LunarTaskId,siteId:string):LunarTaskComparison{
 const site=catalog.moon_sites.find(s=>s.id===siteId)!
 const rankings=id==='M4'?rankingData.rankings.M4[siteId as keyof typeof rankingData.rankings.M4]:rankingData.rankings[id]
 return {version:catalog.version,task_id:id,task:catalog.tasks[id],selected_site:site,site_status:site.suitable_tasks.primary.includes(id)?'primary':site.suitable_tasks.secondary.includes(id)?'secondary':'unassessed',most_similar:rankings.new_candidates.slice(0,3),least_similar:rankings.least_similar,known_analogs_validation:rankings.known_analogs_validation,other_new_candidates:rankings.new_candidates.slice(3),ranking_scope:'Supplied eligible comparison pool',anchor_note:id==='M4'?'Independent lunar terrain reference':'Shared Earth-achievable anchors',provenance:catalog.provenance} as LunarTaskComparison
}
beforeEach(()=>{vi.clearAllMocks();i18n.global.locale.value='en';setContentTranslations({...sourceTranslations,...translations});vi.mocked(api.lunarHandoff).mockResolvedValue(catalog);vi.mocked(api.lunarTask).mockImplementation(async(id,site)=>result(id,site))})
async function open(path:string){
 const router=createRouter({history:createMemoryHistory(),routes:[{path:'/moon',name:'lunar-tasks',component:LunarMission},{path:'/moon/:task(M2|M3|M4|M6)',name:'lunar-task',component:LunarMission},{path:'/:pathMatch(.*)*',component:{template:'<div>Other page</div>'}}]})
 await router.push(path);await router.isReady()
 const wrapper=mount(LunarMission,{global:{plugins:[router,i18n],stubs:{EarthMap:true,PlanetTargetMap:true,Chart:true}}})
 await flushPromises();return {wrapper,router}
}
describe('Task-first lunar experience',()=>{
 it('hides task codes and removed notices, and opens a credited image for a lunar site',async()=>{
  const {wrapper}=await open('/moon/M4?site=ConnectingRidge')
  expect(wrapper.find('h1').text()).not.toContain('M4')
  expect(wrapper.find('.lunar-task-tabs').text()).not.toMatch(/M[2346]/)
  expect(wrapper.text()).not.toContain(i18n.global.t('lunarSuitabilityMeaning'))
  expect(wrapper.text()).not.toContain('Shared Earth-achievable anchors')
  await wrapper.find('[data-site-id="MalapertMassif"]').trigger('click');await flushPromises()
  const dialog=wrapper.findComponent(LunarSiteDialog)
  expect(dialog.props('site').id).toBe('MalapertMassif')
  expect(dialog.find('img').attributes('src')).toBe('/images/moon-sites/MalapertMassif.png')
  expect(dialog.text()).toContain('NASA/GSFC/Arizona State University')
  expect(dialog.find('figcaption a').attributes('href')).toContain('science.nasa.gov')
  await dialog.find('.icon-button').trigger('click');await flushPromises()
  expect(wrapper.findComponent(LunarSiteDialog).exists()).toBe(false)
 })
 it('starts with four mission cards and opens lunar suitability before Earth comparisons',async()=>{
  const {wrapper,router}=await open('/moon')
  expect(wrapper.findAll('[data-task-id]')).toHaveLength(4)
  expect(api.lunarTask).not.toHaveBeenCalled()
  await wrapper.find('[data-task-id="M3"]').trigger('click');await flushPromises()
  expect(router.currentRoute.value.path).toBe('/moon/M3')
  expect(api.lunarTask).toHaveBeenLastCalledWith('M3','Haworth',expect.any(AbortSignal))
  const html=wrapper.html();expect(html.indexOf('lunar-sites-section')).toBeLessThan(html.indexOf('lunar-earth-section'))
  expect(wrapper.find('[data-testid="most-similar"]').findAll('.lunar-earth-card')).toHaveLength(3)
  expect(wrapper.find('[data-testid="least-similar"]').findAll('.lunar-earth-card')).toHaveLength(3)
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain('76.6')
  expect(wrapper.find('[data-testid="modis-method-notice"]').text()).toContain('monthly land-surface temperatures')
  expect(wrapper.find('[data-testid="most-similar"] [data-testid="temperature-months"]').text()).toContain('12/12')
  expect(wrapper.find('[data-testid="least-similar"]').text()).toContain('0.0')
  wrapper.unmount()
 })
 it('changes the M4 reference and shows actual feature evidence without borrowing another site',async()=>{
  const {wrapper,router}=await open('/moon/M4?site=ConnectingRidge')
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain('89.8')
  await wrapper.find('select').setValue('MalapertMassif');await flushPromises()
  expect(router.currentRoute.value.query.site).toBe('MalapertMassif')
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain('90.2')
  await wrapper.find('[data-testid="most-similar"] .lunar-earth-card').trigger('click');await flushPromises()
  const drawer=wrapper.findComponent(LunarEvidenceDrawer)
  expect(drawer.props('site').id).toBe('MalapertMassif')
  expect(drawer.text()).toContain('3,186')
  expect(drawer.text()).toContain('0.70')
  await drawer.find('.icon-button').trigger('click');expect(wrapper.findComponent(LunarEvidenceDrawer).exists()).toBe(false)
  wrapper.unmount()
 })
 it('preserves old shared site IDs, distinguishes insufficient evidence and switches both UI and data language',async()=>{
  const {wrapper,router}=await open('/moon?tasks=M3,M6&site=moon-scr')
  expect(router.currentRoute.value.path).toBe('/moon/M3')
  expect(api.lunarTask).toHaveBeenLastCalledWith('M3','ConnectingRidge',expect.any(AbortSignal))
  expect(wrapper.text()).toContain('its suitability for the selected mission is not established')
  const originalScore=wrapper.find('[data-testid="most-similar"]').text()
  await wrapper.find('button.language').trigger('click');await flushPromises()
  expect(document.documentElement.lang).toBe('zh-Hant')
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain(i18n.global.t('lunarMostSimilar'))
  expect(wrapper.find('[data-testid="most-similar"]').text()).not.toBe(originalScore)
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain(translations['Longest continuous darkness'])
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain('76.6')
  wrapper.unmount()
 })
 it('rejects an unknown site and prevents stale request results after changing a lunar reference',async()=>{
  const unknown=await open('/moon/M4?site=unknown')
  expect(api.lunarTask).not.toHaveBeenCalled();expect(unknown.wrapper.find('[role="alert"]').exists()).toBe(true);unknown.wrapper.unmount()
  const pending=new Map<string,(value:LunarTaskComparison)=>void>()
  vi.mocked(api.lunarTask).mockImplementation((id,site)=>new Promise(resolve=>pending.set(site,resolve)))
  const {wrapper}=await open('/moon/M4?site=ConnectingRidge')
  await wrapper.find('select').setValue('MalapertMassif');await flushPromises()
  pending.get('MalapertMassif')!(result('M4','MalapertMassif'));await flushPromises()
  pending.get('ConnectingRidge')!(result('M4','ConnectingRidge'));await flushPromises()
  expect(wrapper.find('[data-testid="most-similar"]').text()).toContain('90.2')
  expect(wrapper.find('[data-testid="most-similar"]').text()).not.toContain('89.8')
  wrapper.unmount()
 })
 it('shows the MODIS M6 winner with LST definitions and actual month coverage in both languages',async()=>{
  const {wrapper}=await open('/moon/M6?site=Haworth')
  const first=wrapper.find('[data-testid="most-similar"] .lunar-earth-card')
  expect(first.text()).toContain('Lake Hazen')
  expect(first.text()).toContain('59.3')
  await first.trigger('click');await flushPromises()
  const drawer=wrapper.findComponent(LunarEvidenceDrawer)
  expect(drawer.text()).toContain('Mean monthly day/night LST (2023)')
  expect(drawer.find('[data-testid="temperature-source"]').text()).toContain('MODIS LST 2023')
  expect(drawer.text()).not.toContain('Annual mean 2 m air temperature')
  await drawer.find('.icon-button').trigger('click');await flushPromises()
  await wrapper.find('button.language').trigger('click');await flushPromises()
  await wrapper.find('[data-testid="most-similar"] .lunar-earth-card').trigger('click');await flushPromises()
  const translatedDrawer=wrapper.findComponent(LunarEvidenceDrawer)
  expect(translatedDrawer.text()).toContain(translations['Mean monthly day/night LST (2023)'])
  expect(translatedDrawer.text()).toContain(i18n.global.t('lunarModisMonths',{months:12}))
  wrapper.unmount()
 })
})
