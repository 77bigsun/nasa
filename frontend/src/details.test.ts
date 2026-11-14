import {describe,it,expect,vi} from 'vitest'
import {mount,flushPromises} from '@vue/test-utils'
import {i18n} from './i18n'
import DetailsDrawer from './components/DetailsDrawer.vue'
import Shell from './components/Shell.vue'
import type {Candidate,Feature,Task} from './types'
import {api} from './api'
vi.mock('./api',()=>({api:{series:vi.fn().mockResolvedValue({phase:[0,.5],target:[1,2],candidate:[2,3],target_ecdf:{x:[1,2],y:[.5,1]},candidate_ecdf:{x:[2,3],y:[.5,1]},wasserstein:1,uses_placeholder:true})},errorMessage:(e:unknown)=>String(e)}))
const feature={id:'m2_sun_elevation',name:'太陽高度',name_en:'Sun elevation',type:'timeseries',compare_mode:'absolute',unit:'deg',weight:1,threshold:null,planet_threshold:null,out_of_earth_range:false,earth_proxy:false,planet_data:[{name:'LOLA',official:true,source_id:'lro',url:'https://science.nasa.gov/mission/lro/'}],earth_data:[{name:'Copernicus DEM',official:true,source_id:'copernicus',url:'https://dataspace.copernicus.eu/'}],notes:['示範注意事項'],stat:'mean'} as Feature
describe('Evidence drawer',()=>{
 it('opens a dialog, shows traceable evidence, loads series and closes',async()=>{
  i18n.global.locale.value='zh-TW'
  const task={id:'M2',name:'光照測試',name_en:'Lighting',features:[feature],nasa_basis:'NASA Lighting',nasa_url:'https://www.nasa.gov/'} as Task
  const candidate={id:'demo-01',name:'Demo-01',name_en:'Demo-01',lat:36,lon:-116,known_analog:false,is_placeholder:true,overall:.9,tasks:{M2:{score:.9,features:[{feature,target_value:5,candidate_value:4,score:.9,classification:'similar',warnings:[]}],similar:[feature.id],different:[],not_reproducible:[],available_features:1,total_features:1}}} as Candidate
  const wrapper=mount(DetailsDrawer,{props:{candidate,tasks:[task],limits:[{condition:'重力',planet:'1/6 g',reproducible:'否',handling:'無法重現'}],siteId:'moon-scr',mission:'moon'},attachTo:document.body,global:{plugins:[i18n],stubs:{Chart:true}}})
  await flushPromises()
  expect((wrapper.find('dialog').element as HTMLDialogElement).open).toBe(true)
  expect(wrapper.text()).toContain('placeholder');expect(wrapper.text()).toContain('相似之處')
  expect(wrapper.find('a[href="https://science.nasa.gov/mission/lro/"]').exists()).toBe(true)
  expect(wrapper.text()).toContain('Copernicus DEM');expect(wrapper.text()).toContain('1/6 g')
  expect(api.series).toHaveBeenCalledWith('demo-01',feature.id,'moon-scr','moon')
  expect(wrapper.text()).toContain('Wasserstein');expect(wrapper.text()).toContain('1.0000')
  await wrapper.find('button[aria-label="關閉"]').trigger('click');expect(wrapper.emitted('close')).toHaveLength(1)
  wrapper.unmount()
 })
})
describe('Language switching',()=>{
 it('switches navigation and persists the chosen locale',async()=>{
  i18n.global.locale.value='zh-TW';localStorage.removeItem('analog-locale')
  const wrapper=mount(Shell,{global:{plugins:[i18n],stubs:{RouterLink:{template:'<a><slot/></a>'}}}})
  expect(wrapper.text()).toContain('方法說明');await wrapper.find('.language').trigger('click')
  expect(wrapper.text()).toContain('Method');expect(localStorage.getItem('analog-locale')).toBe('en')
  await wrapper.find('.language').trigger('click');expect(wrapper.text()).toContain('方法說明')
  expect(localStorage.getItem('analog-locale')).toBe('zh-TW');wrapper.unmount()
 })
})
