import {createI18n} from 'vue-i18n'
import {ref,watch} from 'vue'
import en from './messages/en.json'
import zh from './messages/zh-TW.json'
export type Locale='en'|'zh-TW'
function preferredLocale():Locale {
 try {return localStorage.getItem('analog-locale')==='en'?'en':'zh-TW'} catch {return 'zh-TW'}
}
export const i18n=createI18n({legacy:false,locale:preferredLocale(),fallbackLocale:'en',messages:{en,'zh-TW':zh}})
watch(i18n.global.locale,value=>{
 try {localStorage.setItem('analog-locale',value)} catch { /* Private storage may be unavailable. */ }
 if(typeof document!=='undefined'){
  document.documentElement.lang=value==='en'?'en':'zh-Hant'
  document.title=i18n.global.t('pageTitle')
 }
},{immediate:true,flush:'sync'})
const contentTranslations=ref<Record<string,string>>({})
export function setContentTranslations(messages:Record<string,string>){contentTranslations.value=messages}
export async function loadContentTranslations(){
 try{
  const response=await fetch('/api/catalog/translations/zh-TW',{signal:AbortSignal.timeout(10000)})
  if(!response.ok)throw new Error('Translation catalog unavailable')
  setContentTranslations(await response.json())
 }catch{ /* English source text remains readable if the catalog is unavailable. */ }
}
export function localizeData<T>(value:T,locale:string):T {
 if(locale!=='zh-TW')return value
 function visit(item:unknown,key=''):unknown {
  if(typeof item==='string')return key.endsWith('_en')?item:contentTranslations.value[item]||item
  if(Array.isArray(item))return item.map(v=>visit(v,key))
  if(item&&typeof item==='object')return Object.fromEntries(Object.entries(item).map(([k,v])=>[k,visit(v,k)]))
  return item
 }
 return visit(value) as T
}
export function localized(item:{name:string;name_en?:string},locale:string){return locale==='en'?(item.name_en||item.name):localizeData(item.name,locale)}
