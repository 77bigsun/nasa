import {beforeEach,describe,it,expect,vi} from 'vitest'
import {mount,flushPromises} from '@vue/test-utils'
import DataPage from '../src/pages/Data.vue'
import ResearchPage from '../src/pages/Research.vue'
import {i18n,setContentTranslations} from '../src/i18n'
import {api} from '../src/api'
import translations from '../../data/locales/zh-TW.json'
import products from '../../data/catalog/datasets.json'
import research from '../../data/catalog/research.json'
import pilot from '../../data/observed/pilot.json'
import zh from '../src/messages/zh-TW.json'
vi.mock('../src/api',()=>({api:{coverage:vi.fn().mockResolvedValue({features:[],targets:{},mode:"observed"}),sources:vi.fn(),datasets:vi.fn(),observations:vi.fn(),research:vi.fn()},errorMessage:(e:unknown)=>String(e)}))
const global={plugins:[i18n],stubs:{Shell:{template:'<main><slot/></main>'},Chart:true,RouterLink:{template:'<a><slot/></a>'}}}
beforeEach(()=>{
 i18n.global.locale.value='en';setContentTranslations(translations)
 vi.mocked(api.sources).mockResolvedValue([])
 vi.mocked(api.datasets).mockResolvedValue(products)
 vi.mocked(api.observations).mockResolvedValue(pilot as never)
 vi.mocked(api.research).mockResolvedValue(research)
})
describe('Observed evidence and research',()=>{
 it('renders actual measurements and translates loaded data without reloading',async()=>{
  const wrapper=mount(DataPage,{global});await flushPromises()
  expect(wrapper.text()).toContain('8.77');expect(wrapper.findAll('#observed tbody tr')).toHaveLength(4)
  expect(wrapper.text()).toContain(pilot.scope)
  expect(wrapper.text()).toContain('SHA-256: '+pilot.downloads[0].sha256)
  i18n.global.locale.value='zh-TW';await flushPromises()
  expect(wrapper.text()).toContain(zh.observedPilot)
  expect(wrapper.text()).toContain(translations[pilot.scope as keyof typeof translations])
  expect(wrapper.text()).toContain('8.77')
  expect(api.observations).toHaveBeenCalledTimes(1);wrapper.unmount()
 })
 it('keeps planned capabilities explicit in both languages',async()=>{
  const wrapper=mount(ResearchPage,{global});await flushPromises()
  expect(wrapper.text()).toContain('That multi-target capability is not implemented.')
  i18n.global.locale.value='zh-TW';await flushPromises()
  expect(wrapper.text()).toContain(zh.status_planned)
  expect(wrapper.text()).toContain(translations[research[1].title as keyof typeof translations])
  expect(wrapper.findAll('article')).toHaveLength(10);wrapper.unmount()
 })
})
