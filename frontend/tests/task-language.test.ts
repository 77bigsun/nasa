import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest'
import {mount,flushPromises,enableAutoUnmount} from '@vue/test-utils'
import {readFileSync} from 'node:fs'
import MethodPage from '../src/pages/Method.vue'
import DataPage from '../src/pages/Data.vue'
import ResearchPage from '../src/pages/Research.vue'
import LunarWeightExplanation from '../src/components/LunarWeightExplanation.vue'
import {api} from '../src/api'
import {i18n,setContentTranslations} from '../src/i18n'
import {expandTaskNames,readableTaskContent,readableTaskHtml,taskName} from '../src/taskNames'
import products from '../../data/catalog/datasets.json'
import research from '../../data/catalog/research.json'
import pairings from '../../data/observed/task-pairings.json'
import translations from '../../data/locales/zh-TW.json'
import catalog from '../../data/catalog/lunar-handoff.json'
import rankings from '../../data/lunar/handoff/rankings.json'
import type {LunarTask,LunarFeatureResult} from '../src/lunarHandoffTypes'
vi.mock('../src/api',()=>({api:{method:vi.fn(),coverage:vi.fn(),sources:vi.fn(),datasets:vi.fn(),observations:vi.fn(),research:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
enableAutoUnmount(afterEach)
const global={plugins:[i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,RouterLink:{template:'<a><slot/></a>'}}}
const method=(locale:string)=>['mars-handoff','lunar-weights','lunar-modis'].map(name=>readFileSync(`../data/content/${name}.${locale}.md`,'utf8')).join('\n')+readFileSync(locale==='en'?'../docs/METHOD.md':'../data/content/method.zh-TW.md','utf8')
beforeEach(()=>{
 vi.clearAllMocks();i18n.global.locale.value='en';setContentTranslations(translations)
 vi.mocked(api.method).mockResolvedValue({markdown:method('en'),markdown_zh:method('zh-TW'),settings:{}})
 vi.mocked(api.coverage).mockResolvedValue({features:pairings,targets:{},mode:'observed'})
 vi.mocked(api.sources).mockResolvedValue([{id:'test-source',name:'Source for M1 and R1',portal:'NASA',official:true,url:'https://example.org/M1',status:'imported',used_by:[pairings[0]!.feature_id],notes:'M1-M6 and R1~R6'}])
 vi.mocked(api.datasets).mockResolvedValue(products)
 vi.mocked(api.observations).mockResolvedValue(null)
 vi.mocked(api.research).mockResolvedValue(research)
})
describe('Full task names and documented lunar weights',()=>{
 it('expands individual IDs and ranges while preserving routing IDs and source URLs',()=>{
  for(const locale of ['en','zh-TW']){
   const text=expandTaskNames('M1–M6 / R1~~R6',locale)
   for(const id of ['M1','M2','M3','M4','M5','M6','R1','R2','R3','R4','R5','R6']){
    expect(text).toContain(taskName(id,locale));expect(taskName(id,locale)).not.toMatch(/\?{2,}/)
   }
   expect(text).not.toMatch(/\b[MR][1-6]\b/)
   const data={task_id:'M2',url:'https://example.org/M2',notes:'M2 uses NASA M2T1NXAER'}
   const rendered=readableTaskContent(data,locale)
   expect(rendered.task_id).toBe('M2');expect(rendered.url).toBe(data.url);expect(rendered.notes).toContain('M2T1NXAER')
   const element=document.createElement('div');element.innerHTML=readableTaskHtml('<a href="/moon/M2">M2</a>',locale)
   expect(element.textContent).toBe(taskName('M2',locale));expect(element.querySelector('a')?.getAttribute('href')).toBe('/moon/M2')
  }
 })
 it.each(['en','zh-TW'])('shows full task names throughout all three explanatory pages in %s',async(locale)=>{
  i18n.global.locale.value=locale as 'en'|'zh-TW'
  for(const page of [MethodPage,DataPage,ResearchPage]){
   const wrapper=mount(page,{global});await flushPromises()
   expect(wrapper.text()).not.toMatch(/\b[MR][1-6]\b/)
   expect(wrapper.text()).not.toMatch(/\?{2,}/)
   if(page===DataPage){
    expect(wrapper.find('.task-data-matrix').text()).toContain(taskName('M1',locale))
    await wrapper.find('.task-data-matrix select').setValue('mars')
    expect(wrapper.find('.task-data-matrix').text()).toContain(taskName('R6',locale))
    expect(wrapper.find('.task-data-matrix').text()).not.toMatch(/\b[MR][1-6]\b/)
    expect(wrapper.find('.data-section a[href="https://example.org/M1"]').exists()).toBe(true)
   }
   if(page===MethodPage){
    const chapter=readFileSync(`../data/content/lunar-weights.${locale}.md`,'utf8').split('\n')[0]!.slice(2)
    expect(wrapper.findAll('h2').map(heading=>heading.text())).toContain(chapter)
    expect(wrapper.find('.katex-error').exists()).toBe(false)
    expect(wrapper.findAll('.katex-display').length).toBeGreaterThan(8)
    expect(wrapper.text()).toContain('26.25%')
   }
   wrapper.unmount()
  }
 })
 it('distinguishes purpose weights from effective weights and checks darkness independently of total score',async()=>{
  const features=rankings.rankings.M3.new_candidates[0]!.features as LunarFeatureResult[]
  const wrapper=mount(LunarWeightExplanation,{props:{taskId:'M3',task:catalog.tasks.M3 as LunarTask,features,expanded:true},global})
  expect(wrapper.text()).toContain('not official NASA weights')
  expect(wrapper.text()).toContain('26.25%')
  expect(wrapper.find('[data-testid="darkness-threshold"]').text()).toContain('meets the')
  const changed=features.map(f=>f.feature==='longest_darkness_h'?{...f,value:119}:f)
  await wrapper.setProps({features:changed})
  expect(wrapper.find('[data-testid="darkness-threshold"]').text()).toContain('below the 120 h')
  await wrapper.setProps({features:changed.map(f=>f.feature==='longest_darkness_h'?{...f,value:null,s:null,c:0}:f)})
  expect(wrapper.find('[data-testid="darkness-threshold"]').text()).toContain('no usable duration')
  await wrapper.setProps({taskId:'M6',task:catalog.tasks.M6 as LunarTask,features:undefined})
  const rows=wrapper.findAll('tbody tr')
  expect(rows.map(row=>row.findAll('td')[0]!.text())).toEqual(['25%','25%','50%'])
  expect(rows.map(row=>row.findAll('td')[2]!.text())).toEqual(['33.33%','33.33%','33.33%'])
  expect(wrapper.text()).not.toMatch(/\bM6\b/)
 })
})
