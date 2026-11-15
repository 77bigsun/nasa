<script setup lang="ts">
import {computed,ref,watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {earthImageAt} from '../earthImages'
const props=defineProps<{lat:number;lon:number;name:string;compact?:boolean}>()
const {t}=useI18n();const image=computed(()=>earthImageAt(props.lat,props.lon));const failed=ref(false);const loaded=ref(false)
watch(()=>image.value?.url,()=>{failed.value=false;loaded.value=false})
</script>
<template><figure v-if="image" class="earth-site-image" :class="{compact}" data-testid="earth-site-image">
 <div class="image-frame" :class="{loaded}"><img v-if="!failed" :src="image.url" :alt="t('earthImageAlt',{name})" decoding="async" @load="loaded=true" @error="failed=true"/><span v-if="failed" class="image-state">{{t('earthImageUnavailable')}}</span><span v-else-if="!loaded" class="image-state" aria-hidden="true"><span class="spinner"></span></span></div>
 <figcaption><span class="image-description">{{t('earthImageKind_'+image.kind)}}<template v-if="image.imagery_date"> · {{image.imagery_date}}</template></span><span class="image-credit">{{image.credit}}</span><template v-if="!compact"><p>{{t('earthImageScope',{lat:image.lat,lon:image.lon})}}</p><a :href="image.source_url" target="_blank" rel="noopener">{{t('source')}} ↗</a></template></figcaption>
</figure><p v-else-if="!compact" class="small muted">{{t('earthImageUnavailable')}}</p></template>
<style scoped>
.earth-site-image{margin:22px 0 28px;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:#0b141c}.image-frame{position:relative;aspect-ratio:16/10;background:radial-gradient(ellipse at center,#213342,#08121a);overflow:hidden}.image-frame img{display:block;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .45s ease}.image-frame.loaded img{opacity:1}.image-state{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#a8bac8;font-size:12px;pointer-events:none}figcaption{padding:14px 18px;font-size:11px;line-height:1.7;color:#bac9d3}.image-description,.image-credit{display:block}.image-description{color:#e6eee9}.image-credit{font-size:10px;color:#8da3b1;margin-top:4px}figcaption p{margin:10px 0}figcaption a{color:#a9e7c7}.compact{margin:0;border:0;border-radius:9px}.compact figcaption{padding:12px 14px}.compact .image-credit{font-size:9px}.compact .image-frame{aspect-ratio:16/10}@media(prefers-reduced-motion:reduce){.image-frame img{transition:none}}
</style>
