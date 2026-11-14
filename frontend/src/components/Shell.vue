<script setup lang="ts">
import {useI18n} from 'vue-i18n'
const {t,locale}=useI18n()
function switchLanguage(){locale.value=locale.value==='en'?'zh-TW':'en';localStorage.setItem('analog-locale',locale.value);document.documentElement.lang=locale.value==='en'?'en':'zh-Hant'}
</script>
<template>
 <div class="site-shell"><header class="topbar"><router-link to="/" class="brand" aria-label="Earth Analog Finder"><span class="brand-orbit">✦</span><span>EARTH ANALOG<span class="brand-small">FINDER / 地球類比探索</span></span></router-link><nav aria-label="Main"><router-link to="/">{{t('home')}}</router-link><router-link to="/method">{{t('method')}}</router-link><router-link to="/data">{{t('data')}}</router-link></nav><button class="language" @click="switchLanguage">{{locale==='en'?'繁中':'EN'}} <span>↗</span></button></header><main id="main"><slot /></main><footer><span>◌ EARTH ANALOG FINDER</span><small>{{t('footer')}}</small><div><a href="/api/catalog/docs" target="_blank" rel="noopener">Catalog API ↗</a><a href="/api/similarity/docs" target="_blank" rel="noopener">Similarity API ↗</a></div></footer></div>
</template>
