<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount,watch,nextTick} from 'vue'
import {useI18n} from 'vue-i18n'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type {Candidate,Settings} from '../types'
import {candidateMapPoints} from '../mapGeometry'
const props=defineProps<{candidates:Candidate[];settings:Settings['map'];similarCutoff:number;differentCutoff:number;scoreScale?:number;gridPoints?:Array<{lat:number;lon:number;score:number}>}>()
const emit=defineEmits<{select:[id:string]}>()
const {t}=useI18n();const host=ref<HTMLElement>();const fallback=ref(false);const offline=ref(false)
let map:L.Map|undefined;let points:L.LayerGroup;let screen:L.LayerGroup;let tiles:L.TileLayer|undefined;let observer:ResizeObserver|undefined
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
function drawGrid(){
 if(!map||!screen)return;screen.clearLayers()
 const positions=candidateMapPoints(props.candidates).map(p=>p.longitude)
 const center=positions.length?(Math.min(...positions)+Math.max(...positions))/2:0
 for(const p of props.gridPoints??[]){
  const x=Math.max(0,Math.min(1,p.score/100));const from=x<.5?[190,117,87]:[216,196,142];const to=x<.5?[216,196,142]:[133,223,190];const f=x<.5?x*2:(x-.5)*2
  const color='rgb('+from.map((v,i)=>Math.round(v+(to[i]!-v)*f)).join(',')+')'
  const longitude=p.lon+360*Math.round((center-p.lon)/360)
  L.circleMarker([p.lat,longitude],{radius:2.5,stroke:false,fillColor:color,fillOpacity:.65,interactive:false,pane:'marsGrid'}).addTo(screen)
 }
}
onMounted(async()=>{
 await nextTick();if(!host.value)return
 map=L.map(host.value,{scrollWheelZoom:false,minZoom:1,maxZoom:props.settings.max_zoom,preferCanvas:true}).setView([0,0],1)
 map.createPane('marsGrid').style.zIndex='350';screen=L.layerGroup().addTo(map)
 points=L.layerGroup().addTo(map)
 tiles=L.tileLayer(props.settings.gibs_url,{maxZoom:props.settings.max_zoom,attribution:'Imagery: NASA GIBS'}).addTo(map)
 tiles.once('tileerror',()=>{
  if(!map)return;fallback.value=true;tiles?.remove()
  tiles=L.tileLayer(props.settings.fallback_url,{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map)
  tiles.once('tileerror',()=>{offline.value=true})
 })
 observer=new ResizeObserver(()=>{map?.invalidateSize();if(host.value&&viewport!==host.value.clientWidth+':'+host.value.clientHeight)fitCandidates()});observer.observe(host.value)
 draw();drawGrid()
})
watch(()=>props.candidates,()=>{draw();drawGrid()})
watch(()=>props.gridPoints,drawGrid)
onBeforeUnmount(()=>{observer?.disconnect();map?.remove();map=undefined})
</script>
<template><div><div ref="host" class="earth-map" :aria-label="t('map')"></div><p v-if="offline||fallback" class="muted small">{{t(offline?'mapOffline':'mapFallback')}}</p></div></template>
