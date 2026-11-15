<script setup lang="ts">
import {ref,computed,useId,onMounted,onBeforeUnmount} from 'vue'
import EarthSiteImage from './EarthSiteImage.vue'
import {earthImageAt} from '../earthImages'
const props=defineProps<{lat:number;lon:number;name:string}>()
const anchor=ref<HTMLElement>();const pointer=ref(false);const focus=ref(false);const dismissed=ref(false);const position=ref({left:'0px',top:'0px',width:'320px'})
const tooltipId=useId();const open=computed(()=>(pointer.value||focus.value)&&!dismissed.value&&!!earthImageAt(props.lat,props.lon))
function place(){
 if(!anchor.value)return
 const rect=anchor.value.getBoundingClientRect();const width=Math.min(320,window.innerWidth-32);const height=width*.625+84;const gap=16
 let left=rect.right+gap;let top=rect.top
 if(left+width>window.innerWidth-gap)left=rect.left-width-gap
 if(left<gap){left=Math.max(gap,Math.min(rect.left,window.innerWidth-width-gap));top=rect.bottom+12;if(top+height>window.innerHeight-gap)top=rect.top-height-12}
 position.value={left:Math.max(gap,Math.min(left,window.innerWidth-width-gap))+'px',top:Math.max(gap,Math.min(top,window.innerHeight-height-gap))+'px',width:width+'px'}
}
function enter(event:PointerEvent){if(event.pointerType==='touch')return;dismissed.value=false;pointer.value=true;place()}
function leave(){pointer.value=false;if(!focus.value)dismissed.value=false}
function focused(){dismissed.value=false;focus.value=true;place()}
function blur(event:FocusEvent){if(!anchor.value?.contains(event.relatedTarget as Node|null))focus.value=false}
function dismiss(){dismissed.value=true}
function scrolled(){if(focus.value&&!dismissed.value)place();else dismiss()}
function keydown(event:KeyboardEvent){if(event.key==='Escape')dismiss()}
onMounted(()=>{window.addEventListener('scroll',scrolled,true);window.addEventListener('resize',dismiss);window.addEventListener('keydown',keydown)})
onBeforeUnmount(()=>{window.removeEventListener('scroll',scrolled,true);window.removeEventListener('resize',dismiss);window.removeEventListener('keydown',keydown)})
</script>
<template><div ref="anchor" class="earth-image-hover" @pointerenter="enter" @pointerleave="leave" @focusin="focused" @focusout="blur"><slot :preview-id="open?tooltipId:undefined"/><Teleport to="body"><Transition name="earth-preview"><div v-if="open" :id="tooltipId" class="earth-image-popover" :style="position" role="tooltip"><EarthSiteImage :lat="lat" :lon="lon" :name="name" compact/></div></Transition></Teleport></div></template>
<style scoped>
.earth-image-hover{min-width:0}.earth-image-popover{position:fixed;z-index:2500;pointer-events:none;border:1px solid #688c7d;border-radius:10px;overflow:hidden;background:#0b141c;box-shadow:0 16px 55px #0009}.earth-preview-enter-active{transition:opacity .3s ease,transform .3s cubic-bezier(.2,.7,.2,1)}.earth-preview-leave-active{transition:opacity .18s ease,transform .18s ease}.earth-preview-enter-from,.earth-preview-leave-to{opacity:0;transform:translateY(9px) scale(.98)}@media(prefers-reduced-motion:reduce){.earth-preview-enter-active,.earth-preview-leave-active{transition:none}}
</style>
