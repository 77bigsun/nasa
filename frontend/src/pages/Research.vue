<script setup lang="ts">
import {ref,computed,onMounted} from 'vue'
import {useI18n} from 'vue-i18n'
import Shell from '../components/Shell.vue'
import {api,errorMessage} from '../api'
import {localizeData} from '../i18n'
import type {ResearchSection} from '../types'
const {t,locale}=useI18n();const raw=ref<ResearchSection[]>([]);const error=ref('')
const sections=computed(()=>localizeData(raw.value,locale.value))
async function load(){error.value='';try{raw.value=await api.research()}catch(e){error.value=errorMessage(e)}}
onMounted(load)
</script>
<template><Shell><div class="page-head"><span class="eyebrow">{{t('research')}}</span><h1>{{t('research')}}</h1><p>{{t('researchIntro')}}</p><router-link to="/data#observed" class="button">{{t('pilotLink')}} ↗</router-link></div><section class="section research-grid"><div v-if="error" class="error-panel" role="alert">{{error}} <button @click="load">{{t('retry')}}</button></div><article v-for="(section,index) in sections" :key="section.id" class="panel research-card"><div class="research-card-heading"><span class="mono muted">{{String(index+1).padStart(2,'0')}}</span><span class="badge" :class="section.status==='implemented'?'official':'supplement'">{{t('status_'+section.status)}}</span></div><h2>{{section.title}}</h2><ul><li v-for="item in section.items" :key="item">{{item}}</li></ul><p class="source-note">{{t('sourceDocuments')}}: {{t('pdf_'+section.pdf)}} · {{t('pages')}} {{section.pages.join(', ')}}</p><a v-for="link in section.links" :key="link.url" :href="link.url" target="_blank" rel="noopener" class="source-link">{{link.title}} ↗</a></article></section></Shell></template>
