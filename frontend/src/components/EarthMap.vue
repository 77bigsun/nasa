<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount,watch,nextTick} from 'vue'
import {useI18n} from 'vue-i18n'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type {Candidate,Settings} from '../types'
const props=defineProps<{candidates:Candidate[];settings:Settings['map'];similarCutoff:number;differentCutoff:number}>()
const emit=defineEmits<{select:[id:string]}>()
const {t}=useI18n();const host=ref<HTMLElement>();const fallback=ref(false);const offline=ref(false)
let map:L.Map|undefined;let points:L.LayerGroup;let tiles:L.TileLayer|undefined;let observer:ResizeObserver|undefined
function draw(){
 if(!map)return;points.clearLayers()
 for(const c of props.candidates){
  const color=c.overall>=props.similarCutoff?'#85dfbe':c.overall<props.differentCutoff?'#d99673':'#d8c48e'
  const text=document.createElement('span');text.textContent=`${c.name} · ${c.overall.toFixed(3)}`
  L.circleMarker([c.lat,c.lon],{radius:6,color,weight:1.5,fillColor:color,fillOpacity:.7}).bindTooltip(text).on('click',()=>emit('select',c.id)).addTo(points)
 }
}
onMounted(async()=>{
 await nextTick();if(!host.value)return
 map=L.map(host.value,{scrollWheelZoom:false,minZoom:1,maxZoom:props.settings.max_zoom}).setView([22,15],2)
 points=L.layerGroup().addTo(map)
 tiles=L.tileLayer(props.settings.gibs_url,{maxZoom:props.settings.max_zoom,attribution:'Imagery: NASA GIBS'}).addTo(map)
 tiles.once('tileerror',()=>{
  if(!map)return;fallback.value=true;tiles?.remove()
  tiles=L.tileLayer(props.settings.fallback_url,{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map)
  tiles.once('tileerror',()=>{offline.value=true})
 })
 observer=new ResizeObserver(()=>map?.invalidateSize());observer.observe(host.value)
 draw()
})
watch(()=>props.candidates,draw)
onBeforeUnmount(()=>{observer?.disconnect();map?.remove();map=undefined})
</script>
<template><div><div ref="host" class="earth-map" :aria-label="t('map')"></div><p v-if="offline||fallback" class="muted small">{{t(offline?'mapOffline':'mapFallback')}}</p></div></template>
