<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount} from 'vue'
import {useI18n} from 'vue-i18n'
import {localizeData} from '../i18n'
import EarthSiteImage from './EarthSiteImage.vue'
import SimilarityRadar from './SimilarityRadar.vue'
import type {MarsEarthCandidate,MarsTask,MarsSite} from '../marsHandoffTypes'
const props=defineProps<{candidate:MarsEarthCandidate;task:MarsTask;site:MarsSite}>()
const emit=defineEmits<{close:[]}>();const {t,locale}=useI18n();const dialog=ref<HTMLDialogElement>();const visible=ref(false);let previous:HTMLElement|null=null
const definition=(id:string)=>props.task.features.find(f=>f.id===id) as (MarsTask['features'][number]&{earth_data?:string;mars_data?:string;fill?:{reason:string}})|undefined
function format(value:unknown):string {if(value===null||value===undefined)return '—';if(typeof value==='number')return value.toLocaleString(locale.value,{maximumFractionDigits:3});if(typeof value==='string')return localizeData(value,locale.value);return JSON.stringify(localizeData(value,locale.value))}
function close(){dialog.value?.close();emit('close')}
onMounted(()=>{previous=document.activeElement as HTMLElement;dialog.value?.showModal();visible.value=true})
onBeforeUnmount(()=>{dialog.value?.close();previous?.focus()})
</script>
<template><dialog ref="dialog" class="detail-drawer" aria-labelledby="mars-evidence-title" @cancel.prevent="close" @click="e=>{if(e.target===dialog)close()}"><div class="drawer-inner">
 <div class="drawer-heading"><div><span class="eyebrow">EARTH / {{task.name}}</span><h2 id="mars-evidence-title">{{candidate.lat}}°, {{candidate.lon}}°</h2><p>{{candidate.name_en}}</p><span class="mono">{{candidate.score?.toFixed(1)}} / 100</span></div><button class="icon-button" :aria-label="t('close')" @click="close">×</button></div>
 <EarthSiteImage :lat="candidate.lat" :lon="candidate.lon" :name="candidate.name_en??(candidate.lat+'°, '+candidate.lon+'°')"/>
 <SimilarityRadar v-if="visible" :features="candidate.features.map(f=>({id:f.feature,name:t('marsFeature_'+f.feature),s:f.s}))"/>
 <p>{{t('comparisonTarget')}}: <strong>{{site.name}}</strong></p><p class="notice">{{t('marsScoreMeaning')}}</p><p class="small muted">{{t('marsPlaceNote')}}</p>
 <article v-for="feature in candidate.features" :key="feature.feature" class="feature-detail"><div class="feature-heading"><h3>{{t('marsFeature_'+feature.feature)}}</h3><span class="badge" :class="feature.classification??'missing'">{{t(feature.classification==='partial'?'lunarPartial':feature.classification??'lunarMissing')}}</span></div>
  <dl class="feature-values"><div><dt>{{t('lunarEarthInput')}}</dt><dd>{{format(feature.value)}} <small>{{feature.unit}}</small></dd></div><div><dt>{{t('marsInput')}}</dt><dd>{{format(feature.mars_value)}}</dd></div><div><dt>{{t('lunarFeatureSimilarity')}}</dt><dd>{{feature.s===null?'—':feature.s.toFixed(3)}}</dd></div></dl>
  <p class="mono small formula">{{definition(feature.feature)?.formula}}</p><p class="small muted">{{t('earth')}}: {{definition(feature.feature)?.earth_data}}</p><p class="small muted">{{t('mars')}}: {{definition(feature.feature)?.mars_data}}</p><p v-if="definition(feature.feature)?.fill" class="small muted">{{definition(feature.feature)?.fill?.reason}}</p>
 </article>
 <section class="drawer-task"><h3>{{t('lunarCalculation')}}</h3><p class="mono">100 × exp(Σ ln(max(s, 0.01)) / n)</p><p>{{t('marsRequired')}}</p><p class="small muted">{{t('marsConditional')}}</p><a v-if="candidate.worldview_url" :href="candidate.worldview_url" target="_blank" rel="noopener">NASA Worldview ↗</a><p><router-link to="/method">{{t('method')}} ↗</router-link></p></section>
</div></dialog></template>
<style scoped>.formula{overflow-wrap:anywhere;padding:12px;border:1px solid var(--line);line-height:1.8}.feature-values dd{overflow-wrap:anywhere}.feature-heading h3{font-size:17px}</style>
