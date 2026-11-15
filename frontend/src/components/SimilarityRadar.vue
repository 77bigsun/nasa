<script setup lang="ts">
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import {useI18n} from 'vue-i18n'
import Chart from './Chart.vue'
import {observedRadarFeatures} from '../similarityRadar'
import type {RadarFeature} from '../similarityRadar'
import type {EChartsOption} from 'echarts'
const props=defineProps<{features:RadarFeature[]}>()
const {t}=useI18n();const replay=ref(0);const active=ref('');const reduced=ref(typeof window!=='undefined'&&!!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);let media:MediaQueryList|undefined
const host=ref<HTMLElement>();const plotWidth=ref(typeof window==='undefined'?650:Math.min(650,window.innerWidth-100));let observer:ResizeObserver|undefined
const narrow=computed(()=>plotWidth.value<420)
const observed=computed(()=>observedRadarFeatures(props.features))
const missing=computed(()=>props.features.filter(f=>!observed.value.some(x=>x.id===f.id)))
const selected=computed(()=>props.features.find(f=>f.id===active.value))
const option=computed<EChartsOption>(()=>({
 backgroundColor:'transparent',animation:!reduced.value,animationDuration:1000,animationDurationUpdate:350,animationEasing:'cubicOut',
 tooltip:{trigger:'item',confine:true,renderMode:'richText',backgroundColor:'#10212c',borderColor:'#527563',textStyle:{color:'#e7f1eb',fontSize:12},formatter:()=>observed.value.map(f=>f.name+': '+f.s.toFixed(3)).join('\n')},
 radar:{center:['50%','52%'],radius:narrow.value?'42%':'53%',shape:observed.value.length<3?'circle':'polygon',splitNumber:4,
  indicator:observed.value.map(f=>({name:f.name,max:1,min:0,color:f.id===active.value?'#f1d58e':'#bfd2da'})),
  axisName:{fontSize:narrow.value?10:11,width:narrow.value?64:90,overflow:'break',lineHeight:16},axisNameGap:12,
  axisLine:{lineStyle:{color:'#3b5261'}},splitLine:{lineStyle:{color:'#304652'}},splitArea:{areaStyle:{color:['#13212b','#10202a']}}},
 series:[{type:'radar',name:t('similarityRadarTitle'),symbol:'circle',symbolSize:7,lineStyle:{width:2,color:'#9be6c1'},itemStyle:{color:'#b5f4d4',borderColor:'#18352a',borderWidth:1},areaStyle:{color:'#85dfbe',opacity:observed.value.length<3?0:.2},emphasis:{lineStyle:{width:3},areaStyle:{opacity:.35}},data:[{name:t('lunarFeatureSimilarity'),value:observed.value.map(f=>f.s)}]}]
}))
function updateMotion(event:MediaQueryListEvent){reduced.value=event.matches}
onMounted(()=>{
 media=window.matchMedia?.('(prefers-reduced-motion: reduce)');if(media){reduced.value=media.matches;media.addEventListener?.('change',updateMotion)}
 if(host.value?.clientWidth)plotWidth.value=host.value.clientWidth
 if(typeof ResizeObserver!=='undefined'&&host.value){observer=new ResizeObserver(entries=>{if(entries[0]?.contentRect.width)plotWidth.value=entries[0].contentRect.width});observer.observe(host.value)}
})
onBeforeUnmount(()=>{media?.removeEventListener?.('change',updateMotion);observer?.disconnect()})
</script>
<template><section ref="host" class="similarity-radar" data-testid="similarity-radar"><div class="radar-heading"><h3>{{t('similarityRadarTitle')}}</h3><button v-if="observed.length&&!reduced" class="text-button" @click="replay++" :aria-label="t('similarityRadarReplay')">↻ {{t('similarityRadarReplay')}}</button></div>
 <p class="small muted">{{t('similarityRadarMeaning')}}</p><div v-if="observed.length" class="radar-plot"><Chart :key="replay" :option="option" :label="t('similarityRadarTitle')"/></div><p v-else class="notice">{{t('similarityRadarMissing')}}</p>
 <p v-if="observed.length===2" class="small muted">{{t('similarityRadarTwoAxes')}}</p><p v-if="missing.length" class="small warning">{{t('similarityRadarOmitted')}}: {{missing.map(f=>f.name).join(' · ')}}</p>
 <div class="radar-values" :aria-label="t('features')"><button v-for="feature in features" :key="feature.id" class="radar-feature" :class="{active:active===feature.id}" :aria-pressed="active===feature.id" @mouseenter="active=feature.id" @focus="active=feature.id" @click="active=feature.id"><span class="radar-feature-name">{{feature.name}}</span><span class="radar-meter" aria-hidden="true"><i :style="{width:(feature.s===null?0:feature.s*100)+'%'}"></i></span><b class="mono">{{feature.s===null?t('lunarMissing'):feature.s.toFixed(3)}}</b></button></div>
 <p v-if="selected" class="radar-selection small" aria-live="polite">{{selected.name}} · {{selected.s===null?t('lunarMissing'):selected.s.toFixed(3)+' / 1.000'}}</p>
</section></template>
<style scoped>
.similarity-radar{margin:28px 0;padding:24px 18px;border:1px solid #355248;border-radius:10px;background:radial-gradient(ellipse at top,#1b3b3129,transparent 65%)}.radar-heading{display:flex;align-items:center;justify-content:space-between;gap:16px}.radar-heading h3{margin:0}.radar-heading button{font-size:11px}.radar-plot :deep(.chart){height:350px;width:100%}.radar-values{display:grid;gap:7px}.radar-feature{display:grid;grid-template-columns:minmax(0,1fr) 70px 58px;align-items:center;gap:12px;border:1px solid transparent;background:transparent;padding:9px 10px;text-align:left;border-radius:5px;font-size:12px}.radar-feature.active{border-color:#577c6a;background:#a1edc009}.radar-feature b{font-size:12px;color:#ade8c8;font-weight:400}.radar-meter{height:3px;background:#2d424b}.radar-meter i{display:block;height:100%;background:#9ee2be;transition:width .45s ease}.radar-selection{margin:16px 0 0;color:#eddaaa}.radar-feature-name{overflow-wrap:anywhere}@media(max-width:500px){.similarity-radar{padding:20px 10px}.radar-plot :deep(.chart){height:310px}.radar-feature{grid-template-columns:minmax(0,1fr) 36px 52px;gap:8px}}@media(prefers-reduced-motion:reduce){.radar-meter i{transition:none}}
</style>
