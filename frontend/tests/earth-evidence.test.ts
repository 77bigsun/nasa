import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest'
import {mount,flushPromises,enableAutoUnmount} from '@vue/test-utils'
import {readFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {resolve} from 'node:path'
import EarthImageHover from '../src/components/EarthImageHover.vue'
import EarthSiteImage from '../src/components/EarthSiteImage.vue'
import SimilarityRadar from '../src/components/SimilarityRadar.vue'
import {earthImageAt} from '../src/earthImages'
import {observedRadarFeatures} from '../src/similarityRadar'
import {i18n} from '../src/i18n'
import manifest from '../src/earthSiteImages.json'
import lunar from '../../data/lunar/handoff/rankings.json'
import mars from '../../data/mars/handoff/results.json'
enableAutoUnmount(afterEach)
beforeEach(()=>{i18n.global.locale.value='en'})
afterEach(()=>vi.unstubAllGlobals())
describe('Earth imagery and feature profiles',()=>{
 it('covers the current Moon and Mars candidates by coordinates and verifies local image bytes',()=>{
  const coordinates=new Set<string>()
  function walk(value:unknown){
   if(Array.isArray(value)){value.forEach(walk);return}
   if(!value||typeof value!=='object')return
   const item=value as Record<string,unknown>
   if('features' in item&&typeof item.lat==='number'&&typeof item.lon==='number'){
    coordinates.add(item.lat+','+item.lon)
    const image=earthImageAt(item.lat,item.lon)
    expect(image,`${item.lat},${item.lon}`).toBeDefined()
    expect(item.lat).toBeGreaterThanOrEqual(image!.bbox[0]!);expect(item.lat).toBeLessThanOrEqual(image!.bbox[2]!)
   }else Object.values(item).forEach(walk)
  }
  walk(lunar);walk(mars.task_rankings)
  expect(coordinates.size).toBe(manifest.coverage.candidate_locations)
  expect(manifest.coverage.unmatched_locations).toHaveLength(0)
  for(const image of manifest.images){
   const bytes=readFileSync(resolve('public',image.url.replace(/^\//,'')))
   expect(createHash('sha256').update(bytes).digest('hex')).toBe(image.sha256)
  }
  expect(earthImageAt(39.5,45.5)?.origin).toBe('provided')
  // Updated MODIS-era Yakutia must not inherit the older named point's image.
  expect(earthImageAt(70.5,112.5)?.lon).toBe(112.5)
  expect(earthImageAt(0,0)).toBeUndefined()
  expect(earthImageAt(Number.NaN,0)).toBeUndefined()
 })
 it('opens a viewport-bounded hover preview, supports keyboard focus/Escape, and avoids touch hover',async()=>{
  const wrapper=mount(EarthImageHover,{props:{lat:39.5,lon:45.5,name:'Armenia'},slots:{default:'<button>Candidate</button>'},attachTo:document.body,global:{plugins:[i18n]}})
  await wrapper.trigger('pointerenter',{pointerType:'mouse'});await flushPromises()
  const popup=document.querySelector('[role="tooltip"]') as HTMLElement
  expect(popup).not.toBeNull();expect(popup.querySelector('img')?.getAttribute('src')).toBe(earthImageAt(39.5,45.5)?.url)
  expect(parseFloat(popup.style.left)).toBeGreaterThanOrEqual(16)
  expect(parseFloat(popup.style.top)).toBeGreaterThanOrEqual(16)
  window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));await flushPromises()
  expect(document.querySelector('[role="tooltip"]')).toBeNull()
  await wrapper.trigger('pointerleave');await wrapper.trigger('pointerenter',{pointerType:'touch'});await flushPromises()
  expect(document.querySelector('[role="tooltip"]')).toBeNull()
  await wrapper.find('button').trigger('focusin');await flushPromises()
  expect(document.querySelector('[role="tooltip"]')).not.toBeNull()
  // Browser focus can scroll the card into view; that must not dismiss a
  // keyboard preview immediately after it opens.
  window.dispatchEvent(new Event('scroll'));await flushPromises()
  expect(document.querySelector('[role="tooltip"]')).not.toBeNull()
  wrapper.unmount();expect(document.querySelector('[role="tooltip"]')).toBeNull()
 })
 it('shows the credited source image, fades in on load, and handles load failure',async()=>{
  const wrapper=mount(EarthSiteImage,{props:{lat:39.5,lon:45.5,name:'Armenia'},global:{plugins:[i18n]}})
  expect(wrapper.text()).toContain('NASA GIBS')
  expect(wrapper.find('a').attributes('href')).toContain('gibs.earthdata.nasa.gov')
  await wrapper.find('img').trigger('load');expect(wrapper.find('.image-frame').classes()).toContain('loaded')
  await wrapper.find('img').trigger('error');expect(wrapper.find('img').exists()).toBe(false)
  expect(wrapper.text()).toContain('No verified image')
 })
 it('plots actual similarities, preserves zeros, omits missing data, and keeps two real axes',async()=>{
  const features=[{id:'a',name:'First',s:0},{id:'b',name:'Second',s:1},{id:'c',name:'Missing',s:null}]
  expect(observedRadarFeatures(features).map(f=>f.s)).toEqual([0,1])
  const wrapper=mount(SimilarityRadar,{props:{features},global:{plugins:[i18n],stubs:{Chart:{name:'Chart',props:['option','label'],template:'<div class="chart-stub"/>'}}}})
  const chart=wrapper.findComponent({name:'Chart'})
  const option=chart.props('option')
  expect(option.radar.indicator.map((i:{max:number})=>i.max)).toEqual([1,1])
  expect(option.series[0].data[0].value).toEqual([0,1])
  expect(option.radar.shape).toBe('circle')
  expect(wrapper.text()).toContain('two observed indicators')
  expect(wrapper.text()).toContain('Unobserved indicators')
  await wrapper.findAll('.radar-feature')[1]!.trigger('click')
  expect(wrapper.find('.radar-selection').text()).toBe('Second · 1.000 / 1.000')
  expect(wrapper.findAll('.radar-feature')[1]!.attributes('aria-pressed')).toBe('true')
  await wrapper.setProps({features:features.map(f=>({...f,s:null}))})
  expect(wrapper.find('.chart-stub').exists()).toBe(false)
 })
 it('disables chart motion for reduced-motion preference',async()=>{
  vi.stubGlobal('matchMedia',()=>({matches:true,addEventListener(){},removeEventListener(){}}))
  const wrapper=mount(SimilarityRadar,{props:{features:[{id:'a',name:'A',s:.7}]},global:{plugins:[i18n],stubs:{Chart:true}}})
  await flushPromises()
  expect(wrapper.findComponent({name:'Chart'}).props('option').animation).toBe(false)
  expect(wrapper.find('.radar-heading button').exists()).toBe(false)
 })
})
