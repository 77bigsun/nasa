import {beforeEach,describe,expect,it} from 'vitest'
import {mount} from '@vue/test-utils'
import {createPinia,setActivePinia} from 'pinia'
import {candidateMapPoints,targetMapPoint} from './mapGeometry'
import {targetEvidence} from './targetEvidence'
import {useMission} from './store'
import PlanetTargetMap from './components/PlanetTargetMap.vue'
import {i18n} from './i18n'
import type {Bundle,MeasurementCoverage,Site} from './types'
const lunarSite={id:'moon-scr',mission:'moon',name:'Shackleton Connecting Ridge',name_en:'Shackleton Connecting Ridge',lat:-89.438758,lon:222.922517,coords_status:'approx',description:'Study window',description_en:'Study window',source:'LOLA'} as Site
const pending={...lunarSite,id:'moon-mouton',name:'Mons Mouton',name_en:'Mons Mouton',lat:null,lon:null}
const bundle={mission:{id:'moon'},sites:[pending,lunarSite],tasks:[{id:'M1',features:[{id:'slope'}]}],settings:{tau:.7,weight_scheme:'roc'}} as Bundle
const coverage:MeasurementCoverage={mode:'observed',targets:{'moon-scr':{usable:['slope'],context:['temperature']}},features:[{mission:'moon',task_id:'M1',feature_id:'slope',name:'Slope',planet_sources:[],earth_sources:[],planet_products:[],earth_products:[],status:'paired',ready_sites:['moon-scr'],observed_sites:['moon-scr'],reason:'Imported'}]}
beforeEach(()=>{i18n.global.locale.value='en';setActivePinia(createPinia())})
describe('Target data and geographic views',()=>{
 it('defaults to a measured target but preserves an explicit unmeasured request at the selection step',()=>{
  const state=useMission()
  state.initialize(bundle,{},coverage);expect(state.siteId).toBe('moon-scr')
  state.initialize(bundle,{site:'moon-mouton',step:'3'},coverage)
  expect(state.siteId).toBe('moon-mouton');expect(state.step).toBe(2)
  expect(targetEvidence(coverage,'moon-mouton').imported).toBe(false)
  expect(targetEvidence(coverage,'moon-mouton',['slope']).comparableIds).toEqual([])
  expect(targetEvidence(coverage,'moon-scr',['slope']).comparableIds).toEqual(['slope'])
 })
 it('keeps the lunar south-polar point and its full label away from clipped edges',async()=>{
  const point=targetMapPoint(lunarSite.lat!,lunarSite.lon!,true)
  expect(point.x).toBeGreaterThan(160);expect(point.x).toBeLessThan(440)
  expect(point.y).toBeGreaterThan(30);expect(point.y).toBeLessThan(295)
  const wrapper=mount(PlanetTargetMap,{props:{sites:[lunarSite,pending],selectedId:'moon-scr',mission:'moon',importedIds:['moon-scr']},global:{plugins:[i18n]}})
  expect(wrapper.find('.target-map-legend').text()).toContain(lunarSite.name)
  expect(wrapper.text()).toContain('Proposed targets awaiting verified coordinates: 1')
  expect(wrapper.findAll('[data-target-id]')).toHaveLength(1)
  await wrapper.find('.target-map-legend button').trigger('click')
  expect(wrapper.emitted('select')).toEqual([['moon-scr']])
  wrapper.unmount()
 })
 it('fits all Earth windows on the shorter Pacific longitude arc without changing source coordinates',()=>{
  const source=[{id:'death-valley',lat:36.4,lon:-116.7},{id:'gobi',lat:43.2,lon:104.5},{id:'australia',lat:-24.6,lon:135.4}]
  const points=candidateMapPoints(source)
  const longitudes=points.map(p=>p.longitude)
  expect(Math.max(...longitudes)-Math.min(...longitudes)).toBeCloseTo(138.8)
  expect(points[0]!.longitude).toBeCloseTo(243.3)
  expect(source[0]!.lon).toBe(-116.7)
  for(const site of [{lat:90,lon:180},{lat:-90,lon:-180}]){
   const p=targetMapPoint(site.lat,site.lon,false)
   expect(p.x).toBeGreaterThanOrEqual(38);expect(p.x).toBeLessThanOrEqual(562)
   expect(p.y).toBeGreaterThanOrEqual(38);expect(p.y).toBeLessThanOrEqual(262)
  }
 })
})
