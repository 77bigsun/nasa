import {beforeEach,describe,expect,it} from 'vitest'
import {flushPromises,mount} from '@vue/test-utils'
import CoverageSummary from './components/CoverageSummary.vue'
import {i18n} from './i18n'
import zh from './messages/zh-TW.json'
import type {Candidate,Feature,OptimizeResponse,Task} from './types'

const feature=(id:string,name:string)=>({id,name,name_en:name,type:'profile',compare_mode:'absolute',unit:'deg',weight:1,out_of_earth_range:false,earth_proxy:false,threshold:null,planet_threshold:null,planet_data:[],earth_data:[],notes:[],stat:'mean'} as Feature)
const tasks=[
 {id:'M1',name:'Landing',name_en:'Landing',features:[feature('slope','Slope'),feature('rock','Rock fraction')]},
 {id:'M2',name:'Lighting',name_en:'Lighting',features:[feature('sun','Solar elevation')]}
] as Task[]
const candidates=[{id:'earth-a',name:'Observed Earth window',name_en:'Observed Earth window',lat:36,lon:-116,known_analog:false,is_placeholder:false,overall:null,partial_score:.8,tasks:{}}] as Candidate[]
const result:OptimizeResponse={
 minimum_sites:0,selected:[],covered_tasks:[],total_tasks:2,uncoverable:['M2'],partial_tasks:['M1'],insufficient_data:[],
 task_diagnostics:[
  {task_id:'M1',status:'partial',required_features:2,comparable_features:1,met_features:1,best_complete_score:null,best_partial_score:.95,missing_features:['rock'],incomparable_features:[],met_feature_ids:['slope']},
  {task_id:'M2',status:'below_threshold',required_features:1,comparable_features:1,met_features:0,best_complete_score:.1,best_partial_score:.1,missing_features:[],incomparable_features:[],met_feature_ids:[]}
 ],
 feature_network:{minimum_sites:1,selected:['earth-a'],total_features:3,comparable_features:2,covered_features:1,coverage:[
  {task_id:'M1',feature_id:'slope',name:'Slope',status:'met',best_score:.95,best_candidate_id:'earth-a',covered_by:[{candidate_id:'earth-a',score:.95}]},
  {task_id:'M1',feature_id:'rock',name:'Rock fraction',status:'missing_data',best_score:null,best_candidate_id:null,covered_by:[]},
  {task_id:'M2',feature_id:'sun',name:'Solar elevation',status:'below_threshold',best_score:.1,best_candidate_id:'earth-a',covered_by:[]}
 ],marginal_curve:[]},
 coverage:[],marginal_curve:[],objective:0,uses_placeholder:false
}
beforeEach(()=>{i18n.global.locale.value='en'})
describe('Coverage diagnosis',()=>{
 it('keeps usable Earth matches visible without promoting an incomplete test',async()=>{
  const wrapper=mount(CoverageSummary,{props:{result,candidates,tasks,tau:.7},global:{plugins:[i18n],stubs:{Chart:true}}})
  const partial=wrapper.find('[data-task-id="M1"]')
  expect(partial.attributes('data-status')).toBe('partial')
  expect(partial.text()).toContain('Some features meet threshold')
  expect(partial.text()).toContain('1 / 2')
  expect(partial.text()).not.toContain('Below threshold (complete data)')
  expect(wrapper.find('[data-task-id="M2"]').text()).toContain('Below threshold (complete data)')
  expect(wrapper.find('[data-testid="no-complete-task-network"]').exists()).toBe(true)
  const site=wrapper.find('[data-testid="feature-network-site"]')
  expect(site.text()).toContain('Observed Earth window')
  await site.trigger('click')
  expect(wrapper.emitted('select')).toEqual([['earth-a']])
  expect(wrapper.find('[data-feature-id="rock"]').text()).toContain('Paired measurement missing')
  expect(wrapper.find('[data-feature-id="sun"]').text()).toContain('Comparable data, below threshold')
  wrapper.unmount()
 })
 it('translates data gaps and measured threshold failures independently',async()=>{
  const wrapper=mount(CoverageSummary,{props:{result,candidates,tasks,tau:.7},global:{plugins:[i18n],stubs:{Chart:true}}})
  i18n.global.locale.value='zh-TW';await flushPromises()
  expect(wrapper.find('[data-task-id="M1"]').text()).toContain(zh.coverageStatus_partial)
  expect(wrapper.find('[data-task-id="M2"]').text()).toContain(zh.coverageStatus_below_threshold)
  expect(wrapper.find('[data-feature-id="rock"]').text()).toContain(zh.featureCoverage_missing_data)
  wrapper.unmount()
 })
})
