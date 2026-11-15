import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest'
import {flushPromises,mount} from '@vue/test-utils'
import {i18n} from './i18n'
import EarthMap from './components/EarthMap.vue'
import type {Candidate} from './types'
const state=vi.hoisted(()=>({fitBounds:vi.fn(),positions:[] as number[][],tooltips:[] as HTMLElement[],resize:null as (()=>void)|null}))
vi.mock('leaflet',()=>{
 const map={setView(){return this},createPane:()=>({style:{}}),fitBounds:state.fitBounds,invalidateSize(){},remove(){}}
 const group={addTo(){return this},clearLayers(){}}
 const tile={addTo(){return this},once(){return this},remove(){}}
 return {default:{
  map:()=>map,layerGroup:()=>group,tileLayer:()=>tile,
  circleMarker:(position:number[])=>{
   state.positions.push(position)
   return {bindTooltip(node:HTMLElement){state.tooltips.push(node);return this},on(){return this},addTo(){return this}}
  }
 }}
})
const candidates=[
 {id:'death-valley',lat:36.4,lon:-116.7},
 {id:'gobi',lat:43.2,lon:104.5},
 {id:'australia',lat:-24.6,lon:135.4}
].map((p,index)=>({...p,name:p.id,name_en:p.id,known_analog:false,is_placeholder:false,overall:null,partial_score:index? .8:null,tasks:{}})) as Candidate[]
beforeEach(()=>{
 i18n.global.locale.value='en';state.fitBounds.mockClear();state.positions.length=0;state.tooltips.length=0
 vi.stubGlobal('ResizeObserver',class{constructor(callback:()=>void){state.resize=callback}observe(){}disconnect(){}})
})
afterEach(()=>vi.unstubAllGlobals())
describe('Earth candidate map viewport',()=>{
 it('fits every candidate including those with no score and preserves user framing on score updates',async()=>{
  const wrapper=mount(EarthMap,{props:{candidates,settings:{gibs_url:'/tiles',fallback_url:'/fallback',max_zoom:8},similarCutoff:.7,differentCutoff:.4},global:{plugins:[i18n]}})
  await flushPromises()
  expect(state.fitBounds).toHaveBeenCalledTimes(1)
  const bounds=state.fitBounds.mock.calls[0]![0] as number[][]
  expect(bounds).toHaveLength(3)
  expect(bounds.map(p=>p[0])).toContain(-24.6)
  const longitudes=bounds.map(p=>p[1]!)
  expect(Math.max(...longitudes)-Math.min(...longitudes)).toBeCloseTo(138.8)
  expect(state.positions[0]![1]).toBeCloseTo(243.3)
  expect(state.tooltips[0]!.textContent).toContain('No comparable score')
  await wrapper.setProps({candidates:candidates.map(c=>({...c,partial_score:.2}))})
  expect(state.fitBounds).toHaveBeenCalledTimes(1)
  Object.defineProperty(wrapper.find('.earth-map').element,'clientWidth',{value:400,configurable:true})
  state.resize?.()
  expect(state.fitBounds).toHaveBeenCalledTimes(2)
  wrapper.unmount()
 })
})
