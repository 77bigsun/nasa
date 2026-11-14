<script setup lang="ts">
import {ref,onMounted,computed} from 'vue'
import {useI18n} from 'vue-i18n'
import Shell from '../components/Shell.vue'
import {api,errorMessage} from '../api'
import type {DataSource} from '../types'
const {t}=useI18n();const sources=ref<DataSource[]>([]);const error=ref('');const filter=ref('all')
const filtered=computed(()=>sources.value.filter(s=>filter.value==='all'||(filter.value==='official')===s.official))
async function load(){error.value='';try{sources.value=await api.sources()}catch(e){error.value=errorMessage(e)}}onMounted(load)
</script>
<template><Shell><div class="page-head"><span class="eyebrow">THE EVIDENCE LIBRARY</span><h1>{{t('data')}}</h1><p>{{t('dataIntro')}}</p></div><section class="section data-section"><div class="filter-row"><button v-for="key in ['all','official','supplement']" :key="key" :class="{active:filter===key}" @click="filter=key">{{t(key)}} <span>{{key==='all'?sources.length:sources.filter(s=>(key==='official')===s.official).length}}</span></button></div><div v-if="error" class="error-panel">{{error}} <button @click="load">{{t('retry')}}</button></div><div class="source-grid"><article v-for="source in filtered" :key="source.id" class="source-card"><span class="badge" :class="source.official?'official':'supplement'">{{source.official?'✓':'＋'}} {{t(source.official?'official':'supplement')}}</span><h3>{{source.name}}</h3><a v-if="source.url" :href="source.url" target="_blank" rel="noopener">{{t('source')}} ↗</a><span v-else class="warning">TODO · {{t('todo')}}</span><h4>{{t('usedBy')}}</h4><div v-if="source.used_by.length" class="feature-tags"><span v-for="id in source.used_by" :key="id">{{id}}</span></div><p v-else class="small muted">{{t('notUsed')}}</p><p class="small muted">{{source.notes}}</p></article></div></section></Shell></template>
