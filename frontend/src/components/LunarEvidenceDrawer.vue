<script setup lang="ts">
import {ref,watch,nextTick,onBeforeUnmount} from 'vue'
import {useI18n} from 'vue-i18n'
import {localizeData} from '../i18n'
import {lunarCandidateName} from '../lunarFormat'
import type {LunarEarthCandidate,LunarTask,LunarReference} from '../lunarHandoffTypes'
import type {Link} from '../types'
const props=defineProps<{candidate:LunarEarthCandidate;task:LunarTask;site:LunarReference;sources:Link[]}>()
const emit=defineEmits<{close:[]}>()
const {t,locale}=useI18n();const dialog=ref<HTMLDialogElement>();let previous:HTMLElement|null=null
const text=(value:string)=>localizeData(value,locale.value)
const definition=(id:string)=>props.task.features.find(f=>f.id===id)!
const format=(value:number|number[]|null,unit='')=>value===null?t('lunarMissing'):Array.isArray(value)?value.map(v=>(v*100).toFixed(1)+'%').join(' / '):unit==='fraction'?(value*100).toFixed(2)+'%':value.toLocaleString(locale.value==='en'?'en-US':'zh-TW',{maximumFractionDigits:3})+(unit?' '+(unit==='C'?'°C':unit==='deg'?'°':unit==='index'?'':unit):'')
function close(){dialog.value?.close();emit('close');previous?.focus()}
watch(()=>props.candidate.id,async()=>{if(!dialog.value?.open){previous=document.activeElement as HTMLElement;await nextTick();dialog.value?.showModal()}},{immediate:true})
onBeforeUnmount(()=>{dialog.value?.close();previous?.focus()})
</script>
<template><dialog ref="dialog" class="detail-drawer" aria-labelledby="lunar-evidence-title" @cancel.prevent="close" @click="e=>{if(e.target===dialog)close()}"><div class="drawer-inner">
 <div class="drawer-heading"><div><span class="eyebrow">EARTH / {{task.name}}</span><h2 id="lunar-evidence-title">{{lunarCandidateName(candidate,locale)}}</h2><span class="mono">{{candidate.score.toFixed(1)}} / 100 · {{candidate.lat}}°, {{candidate.lon}}°</span></div><button class="icon-button" :aria-label="t('close')" @click="close">×</button></div>
 <p class="notice">{{t('lunarScoreMeaning')}}</p><p>{{t('comparisonTarget')}}: <strong>{{site.name}}</strong></p>
 <p v-if="candidate.temperature_source==='MODIS_LST_2023'" class="notice" data-testid="temperature-source">{{t('lunarModisMonths',{months:candidate.temperature_months})}} · {{t('lunarModisMethodNotice')}}</p>
 <p v-for="note in candidate.notes" :key="note" class="notice">{{text(note)}}</p>
 <article v-for="feature in candidate.features" :key="feature.feature" class="feature-detail">
  <div class="feature-heading"><h3>{{definition(feature.feature).name}}</h3><span class="badge" :class="feature.classification||'missing'">{{t(feature.classification==='partial'?'lunarPartial':feature.classification==='similar'?'similar':feature.classification==='different'?'different':'lunarMissing')}}</span></div>
  <dl class="feature-values"><div><dt>{{t('lunarEarthInput')}}</dt><dd>{{format(feature.value,definition(feature.feature).unit)}}</dd></div><div v-if="task.depends_on_moon_site"><dt>{{t('lunarSelectedReference')}}</dt><dd>{{format(feature.moon_value,definition(feature.feature).unit)}}</dd></div><div><dt>{{t('lunarFeatureSimilarity')}}</dt><dd>{{feature.s===null?t('lunarMissing'):feature.s.toFixed(3)}}</dd></div><div><dt>{{t('lunarFeatureWeight')}}</dt><dd>{{feature.w.toFixed(2)}}</dd></div><div><dt>{{t('lunarDataFitness')}}</dt><dd>{{feature.c.toFixed(1)}}</dd></div></dl>
  <p class="lunar-formula mono">{{definition(feature.feature).formula}}</p>
  <div v-if="Array.isArray(feature.value)" class="table-scroll"><table><thead><tr><th>{{t('lunarSlopeBin')}}</th><th>{{t('earth')}}</th><th>{{t('moon')}}</th></tr></thead><tbody><tr v-for="(value,index) in feature.value" :key="index"><th>{{site.terrain.slope_fraction_bins_deg[index]}}°</th><td>{{(value*100).toFixed(1)}}%</td><td>{{Array.isArray(feature.moon_value)?(feature.moon_value[index]!*100).toFixed(1)+'%':'—'}}</td></tr></tbody></table></div>
 </article>
 <section class="drawer-task"><h3>{{t('lunarCalculation')}}</h3><p class="mono">100 × Σ(w × c × s) / Σ(w × c)</p><p class="small muted">{{t('lunarMissingRule')}}</p><p class="small muted">{{t('lunarFitnessMeaning')}}</p><h3>{{t('source')}}</h3><a v-for="source in sources" :key="source.url" :href="source.url" target="_blank" rel="noopener" class="lunar-source">{{source.title}} ↗</a></section>
</div></dialog></template>
<style scoped>
.lunar-formula{font-size:12px;overflow-wrap:anywhere;line-height:1.8;padding:12px;background:#0b141c;border:1px solid var(--line)}.lunar-source{display:block;margin:12px 0;font-size:13px}.feature-values dd{overflow-wrap:anywhere}.feature-heading h3{font-size:17px}.drawer-task h3{margin-top:22px}
</style>
