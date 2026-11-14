<script setup lang="ts">
import {ref,onMounted} from 'vue'
import {useI18n} from 'vue-i18n'
import Shell from '../components/Shell.vue'
import Globe from '../components/Globe.vue'
import {api,errorMessage} from '../api'
import {localized} from '../i18n'
import type {Mission,Facts} from '../types'
const {t,locale}=useI18n();const missions=ref<Mission[]>([]);const facts=ref<Facts>();const error=ref('')
async function load(){error.value='';try{[missions.value,facts.value]=await Promise.all([api.missions(),api.facts()])}catch(e){error.value=errorMessage(e)}}
onMounted(load)
</script>
<template><Shell>
 <section class="hero"><div class="hero-copy"><div class="eyebrow"><span class="live-dot"></span>{{t('heroLabel')}}</div><h1>{{t('tagline')}}</h1><p>{{t('intro')}}</p><a href="#missions" class="button primary">{{t('chooseMission')}} <span>↘</span></a><div class="hero-meta"><span>01 / EARTH</span><span>02 / MOON</span><span>03 / MARS</span></div></div><Globe/><div class="hero-bottom"><span>35° 41′ N &nbsp; 139° 41′ E</span><span>{{t('scienceNote')}}</span><span>SCROLL TO EXPLORE ↓</span></div></section>
 <div v-if="error" class="error-panel" role="alert">{{t('error')}}: {{error}} <button @click="load">{{t('retry')}}</button></div>
 <section id="missions" class="section"><div class="section-heading"><div><span class="eyebrow">01 / MISSION SELECT</span><h2>{{t('chooseMission')}}</h2></div><p class="muted">{{t('missionIntro')}}</p></div><div class="mission-grid"><router-link v-for="(mission,index) in missions" :key="mission.id" :to="`/${mission.id}`" class="mission-tile" :class="mission.id"><div class="tile-top"><span class="eyebrow">{{String(index+1).padStart(2,'0')}} / {{mission.id.toUpperCase()}}</span><span class="arrow-circle">↗</span></div><div class="planet-illustration" aria-hidden="true"></div><div class="tile-copy"><span class="eyebrow">{{mission.id==='moon'?'LUNAR SOUTH POLE':'THE NEXT HORIZON'}}</span><h3>{{localized(mission,locale)}}</h3><p>{{locale==='en'?mission.goal_en:mission.goal}}</p><span class="tile-link">{{t('explore')}} <span>→</span></span></div></router-link></div></section>
 <section class="principles section"><div v-for="(key,index) in ['identify','characterize','limits','connect']" :key="key"><span class="mono">0{{index+1}}</span><h3>{{t(key)}}</h3></div></section>
 <section class="section facts-section"><div class="section-heading"><div><span class="eyebrow">02 / KNOW THE DIFFERENCE</span><h2>{{t('comparison')}}</h2></div><p class="muted">{{t('compareIntro')}}</p></div><div v-if="facts" class="table-scroll"><table><thead><tr><th></th><th><i class="planet-dot earth"></i>{{t('earth')}}</th><th><i class="planet-dot moon"></i>{{t('moon')}}</th><th><i class="planet-dot mars"></i>{{t('mars')}}</th></tr></thead><tbody><tr v-for="row in facts.rows" :key="row.name"><th>{{localized(row,locale)}}</th><td>{{row.earth}}</td><td>{{row.moon}}</td><td>{{row.mars}}</td></tr></tbody></table><p class="source-note">{{facts.notes}} <a :href="facts.source.url" target="_blank" rel="noopener">{{facts.source.title}} ↗</a></p></div></section>
</Shell></template>
