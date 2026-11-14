<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount,watch,nextTick} from 'vue'
import {useI18n} from 'vue-i18n'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type {Candidate,Settings} from '../types'
import {candidateMapPoints} from '../mapGeometry'
const props=defineProps<{candidates:Candidate[];settings:Settings['map'];similarCutoff:number;differentCutoff:number;scoreScale?:number}>()
const emit=defineEmits<{select:[id:string]}>()
const {t}=useI18n();const host=ref<HTMLElement>();const fallback=ref(false);const offline=ref(false)
let map:L.Map|undefined;let points:L.LayerGroup;let tiles:L.TileLayer|undefined;let observer:ResizeObserver|undefined
let geometry=''
let viewport=''
function fitCandidates(){
 if(!map||!host.value)return
 const projected=candidateMapPoints(props.candidates)
 if(projected.length)map.fitBounds(projected.map(p=>[p.candidate.lat,p.longitude] as [number,number]),{padding:[28,28],maxZoom:6})
 viewport=host.value.clientWidth+':'+host.value.clientHeight
}
function draw(){
 if(!map)return;points.clearLayers()
 const projected=candidateMapPoints(props.candidates)
 for(const {candidate:c,longitude} of projected){
  const value=c.overall??c.partial_score??null
  const color=value===null?'#8195a8':value>=props.similarCutoff?'#85dfbe':value<props.differentCutoff?'#d99673':'#d8c48e'
  const text=document.createElement('span');text.textContent=c.name+' - '+(value===null?t('noComparableScore'):(value*(props.scoreScale??1)).toFixed(props.scoreScale===100?1:3)+(c.overall===null?' - '+t('partialScore'):''))
  L.circleMarker([c.lat,longitude],{radius:6,color,weight:1.5,fillColor:color,fillOpacity:.7}).bindTooltip(text).on('click',()=>emit('select',c.id)).addTo(points)
 }
 const next=props.candidates.map(c=>[c.id,c.lat,c.lon].join(':')).sort().join('|')
 if(projected.length&&next!==geometry){fitCandidates();geometry=next}
}
onMounted(async()=>{
 await nextTick();if(!host.value)return
 map=L.map(host.value,{scrollWheelZoom:false,minZoom:1,maxZoom:props.settings.max_zoom}).setView([0,0],1)
 points=L.layerGroup().addTo(map)
 tiles=L.tileLayer(props.settings.gibs_url,{maxZoom:props.settings.max_zoom,attribution:'Imagery: NASA GIBS'}).addTo(map)
 tiles.once('tileerror',()=>{
  if(!map)return;fallback.value=true;tiles?.remove()
  tiles=L.tileLayer(props.settings.fallback_url,{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map)
  tiles.once('tileerror',()=>{offline.value=true})
 })
 observer=new ResizeObserver(()=>{map?.invalidateSize();if(host.value&&viewport!==host.value.clientWidth+':'+host.value.clientHeight)fitCandidates()});observer.observe(host.value)
 draw()
})
watch(()=>props.candidates,draw)
onBeforeUnmount(()=>{observer?.disconnect();map?.remove();map=undefined})
</script>
<template><div><div ref="host" class="earth-map" :aria-label="t('map')"></div><p v-if="offline||fallback" class="muted small">{{t(offline?'mapOffline':'mapFallback')}}</p></div></template>
