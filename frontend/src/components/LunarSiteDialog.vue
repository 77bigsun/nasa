<script setup lang="ts">
import {ref,onMounted,onBeforeUnmount,computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {localizeData} from '../i18n'
import images from '../moonSiteImages.json'
import type {LunarReference} from '../lunarHandoffTypes'
const props=defineProps<{site:LunarReference}>()
const emit=defineEmits<{close:[]}>()
const {t,locale}=useI18n();const dialog=ref<HTMLDialogElement>();let previous:HTMLElement|null=null
const image=computed(()=>images[props.site.id as keyof typeof images])
function close(){dialog.value?.close();emit('close')}
onMounted(()=>{previous=document.activeElement as HTMLElement;dialog.value?.showModal()})
onBeforeUnmount(()=>{dialog.value?.close();previous?.focus()})
</script>
<template><dialog ref="dialog" class="detail-drawer lunar-site-dialog" aria-labelledby="lunar-site-title" @cancel.prevent="close" @click="e=>{if(e.target===dialog)close()}"><div class="drawer-inner">
 <div class="drawer-heading"><div><span class="eyebrow">MOON / {{t('lunarSiteInformation')}}</span><h2 id="lunar-site-title">{{site.name}}</h2></div><button class="icon-button" :aria-label="t('close')" @click="close">×</button></div>
 <figure v-if="image"><img :src="image.url" :alt="site.name+' — '+localizeData(image.caption,locale)" loading="lazy"/><figcaption><p>{{localizeData(image.caption,locale)}}</p><p class="small muted">{{image.credit}}</p><a :href="image.source_url" target="_blank" rel="noopener">{{t('source')}} ↗</a></figcaption></figure>
 <p>{{site.suitable_tasks.note}}</p><p class="mono">{{site.lat}}°, {{site.lon===null?t('lunarLongitudeMissing'):site.lon+'°'}}</p><p class="small muted">{{site.coordinate_note}}</p>
 <dl class="feature-values"><div><dt>{{t('lunarTerrain')}}</dt><dd>{{t('lunarTerrain_'+site.terrain.class)}}</dd></div><div><dt>{{t('relief')}}</dt><dd>{{site.terrain.relief_16km_m}} m / 16 km</dd></div><div><dt>{{t('source')}}</dt><dd>{{site.dem_source}}</dd></div></dl>
 <a :href="site.assessment_source.url" target="_blank" rel="noopener">{{t('lunarAssessmentSource')}} ↗</a>
</div></dialog></template>
<style scoped>
.lunar-site-dialog{width:min(860px,96vw)}figure{margin:24px 0}img{display:block;width:100%;max-height:65vh;object-fit:contain;background:#03080c}figcaption{font-size:13px;line-height:1.7}.feature-values{margin:24px 0}
</style>
