<script setup lang="ts">
import {ref,onMounted,computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {marked} from 'marked'
import DOMPurify from 'dompurify'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import Shell from '../components/Shell.vue'
import {api,errorMessage} from '../api'
const {t,locale}=useI18n();const markdown=ref('');const chinese=ref('');const error=ref('')
const html=computed(()=>{
 const formulas:string[]=[]
 const md=(locale.value==='zh-TW'&&chinese.value?chinese.value:markdown.value).replace(/\$\$([\s\S]*?)\$\$/g,(_,formula:string)=>{const index=formulas.push(katex.renderToString(formula,{displayMode:true,throwOnError:false}))-1;return '\n\nFORMULABLOCK'+index+'END\n\n'})
 const output=DOMPurify.sanitize(String(marked(md,{async:false})))
 return output.replace(/FORMULABLOCK(\d+)END/g,(_,i:string)=>formulas[Number(i)]!)
})
async function load(){error.value='';try{const result=await api.method();markdown.value=result.markdown;chinese.value=result.markdown_zh||''}catch(e){error.value=errorMessage(e)}}
onMounted(load)
</script>
<template><Shell><div class="page-head"><span class="eyebrow">{{t('methodology')}}</span><h1>{{t('method')}}</h1><p>{{t('methodIntro')}}</p><router-link to="/research">{{t('researchLink')}} ↗</router-link></div><div v-if="error" class="error-panel">{{error}} <button @click="load">{{t('retry')}}</button></div><article v-else class="prose" v-html="html"></article></Shell></template>
