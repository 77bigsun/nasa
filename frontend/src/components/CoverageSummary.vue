<script setup lang="ts">
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import type {Candidate,OptimizeResponse,Task} from '../types'
import {localized} from '../i18n'
import Chart from './Chart.vue'
const props=defineProps<{result:OptimizeResponse;candidates:Candidate[];tasks:Task[];tau:number}>()
const emit=defineEmits<{select:[id:string]}>()
const {t,locale}=useI18n()
const candidates=computed(()=>Object.fromEntries(props.candidates.map(c=>[c.id,c])))
const features=computed(()=>Object.fromEntries(props.tasks.flatMap(task=>task.features.map(f=>[f.id,f] as const))))
const taskName=(id:string)=>{const task=props.tasks.find(task=>task.id===id);return task?localized(task,locale.value):id}
const featureName=(id:string)=>features.value[id]?localized(features.value[id]!,locale.value):id
const value=(n:number|null)=>n===null?'—':n.toFixed(3)
const featureOption=computed(()=>({
 textStyle:{color:'#a9b7c5'},grid:{left:55,right:30,top:25,bottom:55},tooltip:{trigger:'axis' as const},
 xAxis:{type:'category' as const,name:t('kSites'),nameLocation:'middle' as const,nameGap:30,data:props.result.feature_network.marginal_curve.map(p=>p.k)},
 yAxis:{type:'value' as const,min:0,max:1,axisLabel:{formatter:(x:number)=>(x*100).toFixed(0)+'%'},splitLine:{lineStyle:{color:'#24303b'}}},
 series:[{type:'line' as const,data:props.result.feature_network.marginal_curve.map(p=>p.weighted_coverage),color:'#91ddba',symbolSize:7}]
}))
</script>
<template>
 <div class="section-heading"><h2>{{t('coverageDiagnosis')}}</h2><span class="mono">τ = {{tau.toFixed(2)}}</span></div>
 <p class="notice">{{t('coverageDistinction')}}</p>
 <div class="coverage-status-counts">
  <div><strong>{{result.covered_tasks.length}}</strong><span>{{t('coverageStatus_covered')}}</span></div>
  <div><strong>{{result.partial_tasks.length}}</strong><span>{{t('coverageStatus_partial')}}</span></div>
  <div><strong>{{result.insufficient_data.length}}</strong><span>{{t('coverageDataPending')}}</span></div>
  <div><strong>{{result.uncoverable.length}}</strong><span>{{t('coverageStatus_below_threshold')}}</span></div>
 </div>
 <div class="table-scroll"><table data-testid="task-coverage-diagnostics"><thead><tr><th>{{t('step1')}}</th><th>{{t('comparableRequirements')}}</th><th>{{t('featuresMeetingThreshold')}}</th><th>{{t('bestEvidenceScore')}}</th><th>{{t('status')}}</th></tr></thead><tbody>
  <tr v-for="row in result.task_diagnostics" :key="row.task_id" :data-task-id="row.task_id" :data-status="row.status">
   <th>{{row.task_id}} · {{taskName(row.task_id)}}</th>
   <td>{{row.comparable_features}} / {{row.required_features}}</td>
   <td>{{row.met_features}} / {{row.required_features}}</td>
   <td class="mono">{{value(row.best_complete_score??row.best_partial_score)}}<small v-if="row.best_complete_score===null&&row.best_partial_score!==null" class="coordinate-caption">{{t('partialScore')}}</small></td>
   <td><span class="badge" :class="row.status==='covered'?'official':'supplement'">{{t('coverageStatus_'+row.status)}}</span><p class="small muted">{{t('coverageReason_'+row.status)}}</p>
    <details v-if="row.missing_features.length||row.incomparable_features.length"><summary>{{t('inspectDataGaps')}}</summary>
     <p v-if="row.missing_features.length" class="small">{{t('featureCoverage_missing_data')}}: {{row.missing_features.map(featureName).join(', ')}}</p>
     <p v-if="row.incomparable_features.length" class="small">{{t('featureCoverage_incomparable')}}: {{row.incomparable_features.map(featureName).join(', ')}}</p>
    </details>
   </td>
  </tr>
 </tbody></table></div>
 <h3>{{t('completeTaskNetwork')}}</h3>
 <p class="small muted">{{t('coverageRequiresComplete')}}</p>
 <p v-if="!result.selected.length" class="notice" data-testid="no-complete-task-network">{{t('noCompleteTaskNetwork')}}</p>
 <div v-else class="network-summary">
  <div><span class="big-number">{{result.minimum_sites}}</span><span>{{t('sitesUnit')}}</span></div>
  <div><span class="big-number">{{result.covered_tasks.length}}<small>/{{result.total_tasks}}</small></span><span>{{t('covers')}}</span></div>
  <div class="network-sites"><button v-for="id in result.selected" :key="id" class="button" @click="emit('select',id)">{{candidates[id]?.name||id}} ↗</button></div>
 </div>
 <section class="feature-network" data-testid="feature-network">
  <h3>{{t('availableFeatureNetwork')}}</h3><p class="small muted">{{t('availableFeatureNetworkIntro')}}</p>
  <div class="result-summary">
   <div><span>{{t('comparableRequirements')}}</span><strong>{{result.feature_network.comparable_features}} <small>/ {{result.feature_network.total_features}}</small></strong></div>
   <div><span>{{t('featuresMeetingThreshold')}}</span><strong>{{result.feature_network.covered_features}} <small>/ {{result.feature_network.total_features}}</small></strong></div>
   <div><span>{{t('sitesForAvailableFeatures')}}</span><strong>{{result.feature_network.minimum_sites}}</strong></div>
  </div>
  <div v-if="result.feature_network.selected.length" class="network-sites"><button v-for="id in result.feature_network.selected" :key="id" class="button" data-testid="feature-network-site" @click="emit('select',id)">{{candidates[id]?.name||id}} ↗</button></div>
  <p v-else class="notice">{{t(result.feature_network.comparable_features?'noFeatureMeetsThreshold':'noComparableFeaturePairs')}}</p>
  <details class="feature-coverage-details"><summary>{{t('inspectFeatureCoverage')}}</summary><div class="table-scroll"><table><thead><tr><th>{{t('features')}}</th><th>{{t('bestEvidenceScore')}}</th><th>{{t('candidate')}}</th><th>{{t('status')}}</th></tr></thead><tbody>
   <tr v-for="row in result.feature_network.coverage" :key="row.feature_id" :data-feature-id="row.feature_id">
    <th>{{row.task_id}} · {{featureName(row.feature_id)}}</th><td class="mono">{{value(row.best_score)}}</td>
    <td><button v-if="row.best_candidate_id" class="text-button" @click="emit('select',row.best_candidate_id)">{{candidates[row.best_candidate_id]?.name||row.best_candidate_id}} ↗</button><span v-else>—</span></td>
    <td><span class="badge" :class="row.status==='met'?'official':'supplement'">{{t('featureCoverage_'+row.status)}}</span></td>
   </tr>
  </tbody></table></div></details>
  <article v-if="result.feature_network.covered_features" class="panel"><h4>{{t('featureMarginal')}}</h4><p class="small muted">{{t('featureMarginalIntro')}}</p><Chart :option="featureOption" :label="t('featureMarginal')"/></article>
 </section>
</template>
