<script setup lang="ts">
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {localized} from '../i18n'
import {targetMapPoint} from '../mapGeometry'
import type {Site} from '../types'
const props=defineProps<{sites:Site[];selectedId:string;mission:string;importedIds:string[]}>()
const emit=defineEmits<{select:[id:string]}>()
const {t,locale}=useI18n()
const located=computed(()=>props.sites.filter(s=>s.lat!==null&&s.lon!==null))
const polar=computed(()=>props.mission==='moon'&&located.value.every(s=>s.lat!<=-75))
const points=computed(()=>located.value.map(site=>({site,...targetMapPoint(site.lat!,site.lon!,polar.value)})))
const select=(site:Site)=>{if(props.importedIds.includes(site.id))emit('select',site.id)}
</script>
<template><div class="planet-target-map">
 <h3>{{t(polar?'southPolarView':'targetCoordinateView')}}</h3>
 <svg viewBox="0 0 600 330" role="img" :aria-label="t(polar?'southPolarView':'targetCoordinateView')">
  <g v-if="polar" class="coordinate-grid">
   <circle cx="300" cy="164" r="130"/><circle cx="300" cy="164" :r="130*2/3"/><circle cx="300" cy="164" :r="130/3"/>
   <path d="M170 164H430M300 34V294"/>
   <text x="305" y="30">0°</text><text x="440" y="168">90° E</text><text x="270" y="314">180°</text><text x="113" y="168">90° W</text>
   <text x="307" y="126">85° S</text><text x="307" y="85">80° S</text><text x="307" y="43">75° S</text><text x="316" y="191">90° S</text>
  </g>
  <g v-else class="coordinate-grid">
   <rect x="38" y="38" width="524" height="224"/>
   <path d="M38 150H562M169 38V262M300 38V262M431 38V262"/>
   <text x="10" y="43">90°</text><text x="15" y="154">0°</text><text x="7" y="266">−90°</text>
   <text x="26" y="286">−180°</text><text x="288" y="286">0°</text><text x="546" y="286">180°</text>
  </g>
  <g v-for="(point,index) in points" :key="point.site.id" :transform="'translate('+point.x+','+point.y+')'"
     :data-target-id="point.site.id" role="button" :tabindex="importedIds.includes(point.site.id)?0:-1"
     :aria-label="localized(point.site,locale)" :aria-disabled="!importedIds.includes(point.site.id)"
     @click="select(point.site)" @keydown.enter.prevent="select(point.site)" @keydown.space.prevent="select(point.site)">
   <title>{{localized(point.site,locale)}} · {{point.site.lat?.toFixed(4)}}°, {{point.site.lon?.toFixed(4)}}°</title>
   <circle r="9" :fill="point.site.id===selectedId?'#91ddba':importedIds.includes(point.site.id)?'#91bfe1':'#526373'" stroke="#0c151e" stroke-width="2"/>
   <text text-anchor="middle" y="3.5" fill="#07111b" font-size="10">{{index+1}}</text>
  </g>
 </svg>
 <div class="target-map-legend"><button v-for="(site,index) in located" :key="site.id" :disabled="!importedIds.includes(site.id)" :class="{active:site.id===selectedId}" @click="select(site)">
  <span class="mono">{{index+1}}</span><span>{{localized(site,locale)}}<small>{{site.lat?.toFixed(4)}}°, {{site.lon?.toFixed(4)}}° · {{t(importedIds.includes(site.id)?'targetImported':'targetNotImported')}}</small></span>
 </button></div>
 <p class="small muted">{{t('coordinateDiagramOnly')}}</p>
 <p v-if="sites.length>located.length" class="small muted">{{t('unplacedTargetCount',{count:sites.length-located.length})}}</p>
</div></template>
<style scoped>
.planet-target-map{border:1px solid var(--line);padding:20px;margin:28px 0;border-radius:4px;background:#101921}
.planet-target-map h3{font-size:15px;margin-bottom:8px}.planet-target-map svg{display:block;width:100%;max-height:350px}
.coordinate-grid{fill:none;stroke:#354552;stroke-width:1}.coordinate-grid text{fill:#a9bac8;stroke:none;font:11px monospace}
.target-map-legend{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}.target-map-legend button{display:flex;gap:12px;align-items:center;text-align:left;border:1px solid #354552;background:transparent;padding:10px 14px;max-width:100%}
.target-map-legend .active{border-color:#91ddba}.target-map-legend small{display:block;color:#9aaebb;overflow-wrap:anywhere}.target-map-legend span{min-width:0}.planet-target-map p{margin:10px 0 0}.planet-target-map [role=button]:not([aria-disabled=true]){cursor:pointer}
</style>
