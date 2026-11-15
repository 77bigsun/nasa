<script setup lang="ts">
import {useI18n} from 'vue-i18n'
import EarthImageHover from './EarthImageHover.vue'
import {lunarCandidateName} from '../lunarFormat'
import type {LunarEarthCandidate,LunarTask} from '../lunarHandoffTypes'
defineProps<{candidate:LunarEarthCandidate;task:LunarTask;least?:boolean}>()
defineEmits<{select:[candidate:LunarEarthCandidate]}>()
const {t,locale}=useI18n()
</script>
<template><EarthImageHover :lat="candidate.lat" :lon="candidate.lon" :name="lunarCandidateName(candidate,locale)" v-slot="{previewId}"><button :aria-describedby="previewId" class="lunar-earth-card" :class="{least}" @click="$emit('select',candidate)" :data-candidate-id="candidate.id">
 <div class="lunar-card-top"><span class="mono muted">{{String(candidate.rank).padStart(2,'0')}}</span><strong class="lunar-score mono">{{candidate.score.toFixed(1)}}<small> / 100</small></strong></div>
 <h4>{{lunarCandidateName(candidate,locale)}}</h4><p class="mono muted small">{{candidate.lat.toFixed(2)}}°, {{candidate.lon.toFixed(2)}}°</p>
 <p v-if="candidate.temperature_source==='MODIS_LST_2023'" class="small muted" data-testid="temperature-months">{{t('lunarModisMonths',{months:candidate.temperature_months})}}</p>
 <div class="score-track"><i :style="{width:candidate.score+'%'}"></i></div>
 <p v-if="candidate.available_features<candidate.total_features" class="small warning">{{t('lunarAvailableFeatures',{available:candidate.available_features,total:candidate.total_features})}}</p>
 <div class="lunar-feature-preview"><p v-for="feature in candidate.features" :key="feature.feature"><span>{{task.features.find(f=>f.id===feature.feature)?.name}}</span><b :class="feature.classification||'muted'">{{feature.s===null?t('lunarMissing'):feature.s.toFixed(3)}}</b></p></div>
 <span class="source-link">{{t('lunarInspectEvidence')}} ↗</span>
</button></EarthImageHover></template>
<style scoped>
.lunar-earth-card{display:block;width:100%;text-align:left;padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:4px;transition:border-color .15s;min-width:0}.lunar-earth-card:hover,.lunar-earth-card:focus-visible{border-color:var(--green)}.lunar-card-top{display:flex;justify-content:space-between;align-items:center;gap:12px}.lunar-score{color:var(--green);font-size:25px}.lunar-score small{font-size:11px;color:var(--muted)}h4{font-size:17px;line-height:1.5;margin:14px 0 5px;overflow-wrap:anywhere}.score-track{display:block;width:100%;margin:20px 0;height:4px}.score-track i{display:block;height:100%;background:#91ddba}.least .lunar-score{color:#d99673}.least .score-track i{background:#d99673}.lunar-feature-preview{margin:14px 0 18px}.lunar-feature-preview p{display:flex;justify-content:space-between;gap:12px;margin:8px 0;font-size:12px}.lunar-feature-preview b{font-family:'Space Mono',monospace;font-weight:400}.similar{color:#91ddba}.different{color:#d99673}.partial{color:#d8c48e}.source-link{font-size:12px}
</style>
