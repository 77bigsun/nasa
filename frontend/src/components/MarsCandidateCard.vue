<script setup lang="ts">
import {useI18n} from 'vue-i18n'
import EarthImageHover from './EarthImageHover.vue'
import type {MarsEarthCandidate} from '../marsHandoffTypes'
defineProps<{candidate:MarsEarthCandidate}>()
defineEmits<{select:[candidate:MarsEarthCandidate]}>()
const {t}=useI18n()
</script>
<template><EarthImageHover :lat="candidate.lat" :lon="candidate.lon" :name="candidate.name_en??(candidate.lat+'°, '+candidate.lon+'°')" v-slot="{previewId}"><button :aria-describedby="previewId" class="mars-earth-card panel" :data-candidate-id="candidate.id" @click="$emit('select',candidate)"><div class="card-heading"><span class="mono muted">{{String(candidate.rank).padStart(2,'0')}}</span><strong class="mono">{{candidate.score?.toFixed(1)}} <small>/ 100</small></strong></div><h4>{{candidate.lat}}°, {{candidate.lon}}°</h4><p class="small muted">{{candidate.name_en}}</p><div class="score-track"><i :style="{width:(candidate.score??0)+'%'}"></i></div><p class="small">{{t('marsWeakest')}}: {{t('marsFeature_'+candidate.weakest_feature)}}</p><span class="source-link">{{t('inspectImportedEvidence')}} ↗</span></button></EarthImageHover></template>
<style scoped>
.mars-earth-card{display:block;text-align:left;width:100%;cursor:pointer;margin:12px 0;background:var(--panel);color:inherit;border:1px solid var(--line);padding:20px}.mars-earth-card:hover{border-color:var(--accent)}.card-heading{display:flex;justify-content:space-between;gap:15px}.card-heading strong{font-size:25px}h4{font-size:18px;margin:14px 0 8px}.score-track{display:block;width:100%;margin:15px 0}.score-track i{display:block;height:4px;background:#85dfbe}.source-link{font-size:12px}
</style>
