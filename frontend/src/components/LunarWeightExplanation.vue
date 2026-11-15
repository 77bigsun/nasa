<script setup lang="ts">
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import type {LunarTask,LunarTaskId,LunarFeatureResult} from '../lunarHandoffTypes'
const props=defineProps<{taskId:LunarTaskId;task:LunarTask;features?:LunarFeatureResult[];expanded?:boolean}>()
const {t,locale}=useI18n()
const rows=computed(()=>props.task.features.map(feature=>{
 const measured=props.features?.find(f=>f.feature===feature.id)
 return {...feature,w:measured?.w??feature.w,c:measured?.c??feature.c,present:props.features===undefined||typeof measured?.s==='number'}
}))
const denominator=computed(()=>rows.value.reduce((sum,f)=>sum+(f.present?f.w*f.c:0),0))
const percent=(value:number)=>(value*100).toLocaleString(undefined,{maximumFractionDigits:2})+'%'
const hours=computed(()=>{const value=props.features?.find(f=>f.feature==='longest_darkness_h')?.value;return typeof value==='number'&&Number.isFinite(value)?value:null})
const hoursLabel=computed(()=>hours.value?.toLocaleString(locale.value,{maximumFractionDigits:1})??'')
const formula:Record<LunarTaskId,string>={M2:'100 × (0.30 s_noon + 0.70 s_low)',M3:'100 × (0.50 s_dark + 0.35 s_min + 0.15 s_range)',M4:'100 × (0.70 s_slope + 0.30 s_relief)',M6:'100 × (0.25 s_mean + 0.25 s_max + 0.50 s_ice)'}
</script>
<template><details class="lunar-weight-explanation" :open="expanded" data-testid="lunar-weight-explanation"><summary>{{t('lunarWeightOriginTitle')}}</summary>
 <p>{{t('lunarWeightOriginIntro')}}</p><p>{{t('lunarWeightReason_'+taskId)}}</p>
 <div class="table-scroll"><table><thead><tr><th>{{t('features')}}</th><th>{{t('lunarWeightDesign')}}</th><th>{{t('lunarDataFitness')}}</th><th>{{t('lunarWeightEffective')}}</th></tr></thead><tbody><tr v-for="feature in rows" :key="feature.id"><th>{{feature.name}}</th><td>{{percent(feature.w)}}</td><td>{{feature.c.toFixed(1)}}</td><td>{{feature.present&&denominator>0?percent(feature.w*feature.c/denominator):t('lunarMissing')}}</td></tr></tbody></table></div>
 <p class="small muted">{{t('lunarWeightEffectiveMeaning')}}</p><p class="mono weight-formula">{{formula[taskId]}}</p><p class="small muted">{{t('lunarWeightDesignOnly')}}</p>
 <p v-if="taskId==='M3'&&features" class="notice darkness-threshold" data-testid="darkness-threshold">{{hours===null?t('lunarDarknessUnknown'):t(hours>=120?'lunarDarknessMet':'lunarDarknessNotMet',{hours:hoursLabel})}}</p>
 <p>{{t('lunarWeightLimits_'+taskId)}}</p><router-link to="/method" class="source-link">{{t('lunarWeightFullMethod')}} ↗</router-link>
</details></template>
<style scoped>
.lunar-weight-explanation{margin:24px 0;padding:20px;border:1px solid var(--line);border-radius:6px;background:#11201c33}.lunar-weight-explanation summary{cursor:pointer;color:var(--green);font-size:16px}.lunar-weight-explanation p{margin:18px 0;line-height:1.9}.lunar-weight-explanation table{font-size:12px}.lunar-weight-explanation th{white-space:normal;min-width:100px}.weight-formula{padding:14px;border:1px solid var(--line);font-size:13px;overflow-wrap:anywhere}.darkness-threshold{margin-top:18px}
</style>
