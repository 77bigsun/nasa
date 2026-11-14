<script setup lang="ts">
import {useI18n} from 'vue-i18n'
const {t,locale}=useI18n()
function toggleLanguage(){locale.value=locale.value==='en'?'zh-TW':'en'}
</script>
<template>
 <div class="site-shell"><header class="topbar"><router-link to="/" class="brand" aria-label="Earth Analog Finder"><span class="brand-orbit">◎</span><span>EARTH ANALOG<span class="brand-small">FINDER / MISSION EXPLORER</span></span></router-link><nav :aria-label="t('explore')"><router-link to="/">{{t('home')}}</router-link><router-link to="/research">{{t('research')}}</router-link><router-link to="/method">{{t('method')}}</router-link><router-link to="/data">{{t('data')}}</router-link></nav><button class="language" :aria-label="t('languageSwitch')" @click="toggleLanguage">{{t('switchLanguageLabel')}}</button></header><main id="main"><slot /></main><footer><span>◎ EARTH ANALOG FINDER</span><small>{{t('footer')}}</small><div><a href="/api/catalog/docs" target="_blank" rel="noopener">Catalog API ↗</a><a href="/api/measurements/docs" target="_blank" rel="noopener">Measurements API ↗</a></div></footer></div>
</template>
