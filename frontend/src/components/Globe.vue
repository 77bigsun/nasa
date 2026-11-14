<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount} from 'vue'
const host=ref<HTMLElement>();const failed=ref(false)
let globe:InstanceType<(typeof import('globe.gl'))['default']> | undefined
let observer:ResizeObserver | undefined
let disposed=false
onMounted(async()=>{
 try{
  const {default:Globe}=await import('globe.gl')
  if(disposed||!host.value)return
  globe=new Globe(host.value,{animateIn:true}).width(host.value.clientWidth).height(host.value.clientHeight).backgroundColor('rgba(0,0,0,0)').globeImageUrl('/textures/blue-marble.jpg').showAtmosphere(true).atmosphereColor('#79bce5').atmosphereAltitude(.16)
  globe.pointOfView({lat:18,lng:110,altitude:2.35})
  globe.controls().autoRotate=!matchMedia('(prefers-reduced-motion: reduce)').matches
  globe.controls().autoRotateSpeed=.35;globe.controls().enableZoom=false
  observer=new ResizeObserver(()=>{if(host.value)globe?.width(host.value.clientWidth).height(host.value.clientHeight)})
  observer.observe(host.value)
 }catch{failed.value=true}
})
onBeforeUnmount(()=>{disposed=true;observer?.disconnect();globe?._destructor()})
</script>
<template><div class="globe-wrap"><div ref="host" class="globe-canvas" role="img" aria-label="NASA Blue Marble Earth globe"></div><div v-if="failed" class="globe-fallback" role="img" aria-label="NASA Blue Marble Earth"></div><span class="globe-label"><i></i> EARTH / 01<span>Imagery: NASA</span></span></div></template>
