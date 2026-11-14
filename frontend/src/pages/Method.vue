<script setup lang="ts">
import {ref,onMounted} from 'vue'
import {useI18n} from 'vue-i18n'
import {marked} from 'marked'
import DOMPurify from 'dompurify'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import Shell from '../components/Shell.vue'
import {api,errorMessage} from '../api'
const {t}=useI18n();const html=ref('');const error=ref('')
async function load(){error.value='';try{const result=await api.method();const formulas:string[]=[];const md=result.markdown.replace(/\$\$([\s\S]*?)\$\$/g,(_,formula:string)=>{const index=formulas.push(katex.renderToString(formula,{displayMode:true,throwOnError:false}))-1;return `\n\nFORMULABLOCK${index}END\n\n`});let output=String(await marked(md));output=DOMPurify.sanitize(output);html.value=output.replace(/FORMULABLOCK(\d+)END/g,(_,i:string)=>formulas[Number(i)]!)}catch(e){error.value=errorMessage(e)}}
onMounted(load)
</script>
<template><Shell><div class="page-head"><span class="eyebrow">THE METHODOLOGY</span><h1>{{t('method')}}</h1><p>{{t('methodIntro')}}</p></div><div v-if="error" class="error-panel">{{error}} <button @click="load">{{t('retry')}}</button></div><article v-else class="prose" v-html="html"></article></Shell></template>
