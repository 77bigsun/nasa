<script setup lang="ts">
import {ref,computed,watch,onMounted,onBeforeUnmount} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import Shell from '../components/Shell.vue'
import PlanetTargetMap from '../components/PlanetTargetMap.vue'
import EarthMap from '../components/EarthMap.vue'
import LunarCandidateCard from '../components/LunarCandidateCard.vue'
import LunarEvidenceDrawer from '../components/LunarEvidenceDrawer.vue'
import LunarSiteDialog from '../components/LunarSiteDialog.vue'
import {api,errorMessage} from '../api'
import {localizeData} from '../i18n'
import {lunarCandidateName} from '../lunarFormat'
import type {LunarHandoffCatalog,LunarTaskComparison,LunarTaskId,LunarReference,LunarEarthCandidate} from '../lunarHandoffTypes'
import type {Candidate,Site} from '../types'
const {t,locale}=useI18n();const route=useRoute();const router=useRouter()
const raw=ref<LunarHandoffCatalog>();const comparisonRaw=ref<LunarTaskComparison>();const loading=ref(true);const busy=ref(false);const error=ref('');const selectedCandidate=ref<LunarEarthCandidate>()
const informationSiteId=ref('')
const informationSite=computed(()=>catalog.value?.moon_sites.find(s=>s.id===informationSiteId.value))
const ids:LunarTaskId[]=['M2','M3','M4','M6']
const taskId=computed(()=>ids.includes(route.params.task as LunarTaskId)?route.params.task as LunarTaskId:null)
const catalog=computed(()=>raw.value?localizeData(raw.value,locale.value):undefined)
const task=computed(()=>taskId.value?catalog.value?.tasks[taskId.value]:undefined)
const selectedSite=computed(()=>catalog.value?.moon_sites.find(s=>route.query.site===s.id||route.query.site===s.legacy_id)||(!route.query.site?catalog.value?.moon_sites.find(s=>taskId.value&&s.suitable_tasks.primary.includes(taskId.value)):undefined))
const comparison=computed(()=>comparisonRaw.value?localizeData(comparisonRaw.value,locale.value):undefined)
const prioritySites=computed(()=>catalog.value?.moon_sites.filter(s=>status(s)==='primary')||[])
const secondarySites=computed(()=>catalog.value?.moon_sites.filter(s=>status(s)==='secondary')||[])
const unassessedSites=computed(()=>catalog.value?.moon_sites.filter(s=>status(s)==='unassessed')||[])
const mapSites=computed<Site[]>(()=>catalog.value?.moon_sites.map(s=>({id:s.id,mission:'moon',name:s.name,name_en:s.name,lat:s.map_lat,lon:s.map_lon,coords_status:'approx',source:s.dem_source,description:s.coordinate_note,description_en:s.coordinate_note}))||[])
const mapCandidates=computed<Candidate[]>(()=>comparison.value?[...comparison.value.most_similar,...comparison.value.least_similar].map(c=>({id:c.id,name:lunarCandidateName(c,locale.value),name_en:c.name_en,lat:c.lat,lon:c.lon,known_analog:false,is_placeholder:false,overall:c.score/100,tasks:{}})):[])
const mapSettings={gibs_url:'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg',fallback_url:'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',max_zoom:8}
let version=0;let controller:AbortController|undefined
function status(site:LunarReference){return taskId.value&&site.suitable_tasks.primary.includes(taskId.value)?'primary':taskId.value&&site.suitable_tasks.secondary.includes(taskId.value)?'secondary':'unassessed'}
function chooseSite(id:string){selectedCandidate.value=undefined;void router.replace({query:{site:id}})}
function openSite(id:string){chooseSite(id);informationSiteId.value=id}
function openMapCandidate(id:string){selectedCandidate.value=[...comparison.value!.most_similar,...comparison.value!.least_similar].find(c=>c.id===id)}
async function loadCatalog(){
 loading.value=true;error.value=''
 try{
  raw.value=await api.lunarHandoff()
  const sharedTasks=typeof route.query.tasks==='string'?route.query.tasks.split(','):[]
  const sharedTask=sharedTasks.find(id=>ids.includes(id as LunarTaskId))
  if(!taskId.value&&sharedTask)await router.replace({name:'lunar-task',params:{task:sharedTask},query:route.query.site?{site:route.query.site}:{}})
 }catch(e){error.value=errorMessage(e)}finally{loading.value=false}
}
async function loadComparison(){
 const current=++version;controller?.abort();selectedCandidate.value=undefined;comparisonRaw.value=undefined;busy.value=false
 if(!raw.value||!taskId.value)return
 if(!selectedSite.value){error.value=t('lunarUnknownSite');return}
 error.value='';busy.value=true;controller=new AbortController()
 try{
  const result=await api.lunarTask(taskId.value,selectedSite.value.id,controller.signal)
  if(current===version){
   if(result.task_id!==taskId.value||result.selected_site.id!==selectedSite.value?.id||result.version!==raw.value.version)throw new Error(t('lunarResponseMismatch'))
   comparisonRaw.value=result
  }
 }catch(e){if(current===version&&!controller.signal.aborted)error.value=errorMessage(e)}finally{if(current===version)busy.value=false}
}
watch(()=>[raw.value?.version,taskId.value,selectedSite.value?.id],loadComparison)
onMounted(loadCatalog)
onBeforeUnmount(()=>{version++;controller?.abort()})
</script>
<template><Shell>
 <div v-if="loading" class="loading-state" role="status"><span class="spinner"></span>{{t('loading')}}</div>
 <div v-if="error" class="error-panel" role="alert">{{error}} <button class="button" @click="raw?loadComparison():loadCatalog()">{{t('retry')}}</button></div>
 <template v-if="catalog&&!loading">
  <div class="mission-head lunar-mission-head"><router-link to="/" class="breadcrumb">← {{t('home')}}</router-link><div class="mission-title-row"><div><span class="eyebrow">MOON / MISSION EXPLORER</span><h1>{{task?task.name:t('lunarMissionHeading')}}</h1><p>{{task?t('lunarDetailIntro'):t('lunarMissionIntro')}}</p></div><div class="mini-planet moon" aria-hidden="true"></div></div></div>
  <nav v-if="taskId" class="lunar-task-tabs" :aria-label="t('lunarChooseTask')"><router-link :to="{name:'lunar-tasks'}">← {{t('lunarAllTasks')}}</router-link><router-link v-for="id in ids" :key="id" :class="{active:taskId===id}" :to="{name:'lunar-task',params:{task:id}}"><span>{{catalog.tasks[id].name}}</span></router-link></nav>
  <section v-if="!taskId" class="section" data-testid="lunar-task-picker"><div class="section-heading"><div><span class="eyebrow">01 / {{t('lunarChooseTask')}}</span><h2>{{t('lunarFourTasks')}}</h2></div><span class="eyebrow">04 / {{t('lunarTaskCount')}}</span></div>
   <div class="lunar-task-grid"><router-link v-for="id in ids" :key="id" class="task-card lunar-task-entry" :to="{name:'lunar-task',params:{task:id}}" :data-task-id="id"><h3>{{catalog.tasks[id].name}}</h3><p>{{t('lunarPurpose'+id)}}</p><div class="lunar-task-facts"><span>{{catalog.tasks[id].features.length}} {{t('features')}}</span><span>{{t('weight')}} {{(catalog.tasks[id].weight*100).toFixed(1)}}%</span></div><span class="source-link">{{t('lunarOpenTask')}} ↗</span></router-link></div>
   <p class="small muted lunar-intro-note">{{t('lunarRetiredNote')}}</p>
  </section>
  <template v-else-if="task&&selectedSite">
   <section class="section lunar-sites-section" data-testid="lunar-sites-section"><div class="section-heading"><div><span class="eyebrow">01 / MOON</span><h2>{{t('lunarWhereOnMoon')}}</h2></div><span class="eyebrow">10 / {{t('sitesUnit')}}</span></div>
    <p class="lunar-task-purpose">{{t('lunarPurpose'+taskId)}}</p>
    <div class="lunar-site-counts"><span>{{t('lunarPrimary')}} <b>{{prioritySites.length}}</b></span><span>{{t('lunarSecondary')}} <b>{{secondarySites.length}}</b></span><span>{{t('lunarUnassessed')}} <b>{{unassessedSites.length}}</b></span></div>
    <div class="lunar-site-grid"><button v-for="site in [...prioritySites,...secondarySites]" :key="site.id" class="lunar-site-card" :class="{selected:selectedSite.id===site.id}" :aria-pressed="selectedSite.id===site.id" :data-site-id="site.id" @click="openSite(site.id)"><span class="badge" :class="status(site)">{{t(status(site)==='primary'?'lunarPrimary':'lunarSecondary')}}</span><h3>{{site.name}}</h3><p>{{site.suitable_tasks.note}}</p><span class="small muted">{{t('lunarTerrain')}}: {{t('lunarTerrain_'+site.terrain.class)}} · {{t('relief')}} {{site.terrain.relief_16km_m}} m</span></button></div>
    <details class="lunar-unassessed"><summary>{{t('lunarOtherSites',{count:unassessedSites.length})}}</summary><p class="small muted">{{t('lunarUnassessedMeaning')}}</p><div class="lunar-site-grid"><button v-for="site in unassessedSites" :key="site.id" class="lunar-site-card" :class="{selected:selectedSite.id===site.id}" :aria-pressed="selectedSite.id===site.id" :data-site-id="site.id" @click="openSite(site.id)"><span class="badge">{{t('lunarUnassessed')}}</span><h3>{{site.name}}</h3><p>{{site.suitable_tasks.note}}</p></button></div></details>
    <div class="lunar-reference-panel panel"><div class="lunar-reference-top"><div><span class="eyebrow">{{t('lunarReferenceForEarth')}}</span><h3>{{selectedSite.name}}</h3></div><label>{{t('lunarChooseReference')}}<select :value="selectedSite.id" @change="chooseSite(($event.target as HTMLSelectElement).value)"><option v-for="site in catalog.moon_sites" :key="site.id" :value="site.id">{{site.name}}</option></select></label></div>
     <button class="button" @click="informationSiteId=selectedSite.id">{{t('lunarSiteInformation')}} ↗</button><p v-if="status(selectedSite)==='unassessed'" class="notice">{{t('lunarSelectedUnassessed')}}</p><p>{{selectedSite.suitable_tasks.note}}</p><p class="small mono muted">{{selectedSite.lat}}°, {{selectedSite.lon===null?t('lunarLongitudeMissing'):selectedSite.lon+'°'}} · {{selectedSite.dem_source}}</p><p class="small muted">{{selectedSite.coordinate_note}}</p><p class="small muted">{{t('lunarSupport')}}: 30 m / 16 km · {{t('lunarTerrain')}}: {{t('lunarTerrain_'+selectedSite.terrain.class)}}</p><a class="source-link" :href="selectedSite.assessment_source.url" target="_blank" rel="noopener">{{t('lunarAssessmentSource')}} ↗</a>
     <details><summary>{{t('lunarLunarTerrainDetails')}}</summary><div class="table-scroll"><table><thead><tr><th>{{t('lunarSlopeBin')}}</th><th>{{t('lunarAreaShare')}}</th></tr></thead><tbody><tr v-for="(fraction,index) in selectedSite.terrain.slope_fraction" :key="index"><th>{{selectedSite.terrain.slope_fraction_bins_deg[index]}}°</th><td>{{(fraction*100).toFixed(1)}}%</td></tr></tbody></table></div></details>
    </div>
    <details class="lunar-location-map"><summary>{{t('lunarShowMoonMap')}}</summary><PlanetTargetMap :sites="mapSites" :selected-id="selectedSite.id" mission="moon" :imported-ids="catalog.moon_sites.map(s=>s.id)" @select="openSite"/></details>
   </section>
   <section class="section lunar-earth-section" data-testid="lunar-earth-section" :aria-busy="busy"><div class="section-heading"><div><span class="eyebrow">02 / EARTH</span><h2>{{t('lunarEarthContrast')}}</h2></div><span class="eyebrow">03 + 03 / {{t('sitesUnit')}}</span></div><p class="small muted">{{t('comparisonTarget')}}: {{selectedSite.name}}</p>
    <div v-if="busy" class="loading-state" role="status"><span class="spinner"></span>{{t('calculating')}}</div>
    <template v-if="comparison"><p v-if="comparison.provenance.temperature_source==='MODIS_LST_2023'&&['M3','M6'].includes(taskId!)" class="notice" data-testid="modis-method-notice">{{t('lunarModisMethodNotice')}}</p><p class="small muted">{{comparison.ranking_scope}}</p>
     <div class="lunar-contrast-grid"><section class="lunar-contrast-group" data-testid="most-similar"><div class="lunar-group-title"><span class="lunar-group-dot"></span><h3>{{t('lunarMostSimilar')}}</h3><span class="eyebrow">TOP 03</span></div><p class="small muted">{{t('lunarNewCandidateMeaning')}}</p><LunarCandidateCard v-for="candidate in comparison.most_similar" :key="candidate.id" :candidate="candidate" :task="task" @select="selectedCandidate=$event"/></section>
     <section class="lunar-contrast-group least" data-testid="least-similar"><div class="lunar-group-title"><span class="lunar-group-dot"></span><h3>{{t('lunarLeastSimilar')}}</h3><span class="eyebrow">BOTTOM 03</span></div><p class="small muted">{{t('lunarLeastMeaning')}}</p><LunarCandidateCard v-for="candidate in comparison.least_similar" :key="candidate.id" :candidate="candidate" :task="task" least @select="selectedCandidate=$event"/></section></div>
     <p class="small muted">{{t('lunarTieNote')}}</p><div class="lunar-earth-map"><EarthMap :candidates="mapCandidates" :settings="mapSettings" :similar-cutoff=".6" :different-cutoff=".3" :score-scale="100" @select="openMapCandidate"/></div>
     <details class="lunar-validation"><summary>{{t('lunarValidationTitle')}}</summary><p class="small muted">{{t('lunarValidationMeaning')}}</p><div class="lunar-validation-grid"><LunarCandidateCard v-for="candidate in comparison.known_analogs_validation" :key="candidate.id" :candidate="candidate" :task="task" @select="selectedCandidate=$event"/></div></details>
     <details class="lunar-validation"><summary>{{t('lunarMoreCandidates')}}</summary><div class="lunar-validation-grid"><LunarCandidateCard v-for="candidate in comparison.other_new_candidates" :key="candidate.id" :candidate="candidate" :task="task" @select="selectedCandidate=$event"/></div></details>
    </template>
   </section>
   <section class="section lunar-method-section"><div class="section-heading"><div><span class="eyebrow">METHOD / MOON</span><h2>{{t('lunarHowScored')}}</h2></div><router-link to="/method">{{t('method')}} ↗</router-link></div><p class="mono lunar-score-formula">100 × Σ(w × c × s) / Σ(w × c)</p><p>{{t('lunarScoreMeaning')}}</p><p class="small muted">{{t('lunarMissingRule')}}</p><p class="small muted">{{t('lunarFitnessMeaning')}}</p><div class="table-scroll"><table><thead><tr><th>{{t('features')}}</th><th>{{t('lunarFeatureWeight')}}</th><th>{{t('lunarDataFitness')}}</th><th>{{t('lunarFormula')}}</th></tr></thead><tbody><tr v-for="feature in task.features" :key="feature.id"><th>{{feature.name}}</th><td>{{feature.w.toFixed(2)}}</td><td>{{feature.c.toFixed(1)}}</td><td class="mono small">{{feature.formula}}</td></tr></tbody></table></div></section>
  </template>
  <section class="section lunar-source-section"><div class="section-heading"><div><span class="eyebrow">DATA / PROVENANCE</span><h2>{{t('lunarSourceHeading')}}</h2></div><span class="badge">{{t('lunarPreliminary')}}</span></div><div class="lunar-data-counts"><div><strong>19,599</strong><span>{{t('lunarGlobalCells')}}</span></div><div><strong>4,881</strong><span>{{t('lunarExcludedIce')}}</span></div><div><strong>10</strong><span>{{t('lunarLunarReferences')}}</span></div></div><div class="inline-links"><a v-for="doc in catalog.documents" :key="doc.url" :href="doc.url" target="_blank" rel="noopener">{{doc.title}} ↗</a><a href="/api/measurements/lunar-temperature" download>{{t('lunarDownloadTemperature')}} ↓</a><a href="/api/measurements/lunar-grid" download>{{t('lunarDownloadGrid')}} ↓</a><a href="/api/measurements/lunar-handoff" target="_blank" rel="noopener">{{t('lunarDownloadRankings')}} ↗</a></div>
   <details><summary>{{t('lunarSourcesAndLimits')}}</summary><ul><li v-for="note in catalog.limitations" :key="note">{{note}}</li></ul><div class="inline-links"><a v-for="source in catalog.sources" :key="source.url" :href="source.url" target="_blank" rel="noopener">{{source.title}} ↗</a></div><p class="small muted">{{t('lunarArchiveNote')}}</p><p class="small muted">{{t('lunarAiDisclosure')}}</p></details>
  </section>
  <LunarSiteDialog v-if="informationSite" :site="informationSite" @close="informationSiteId=''"/>
  <LunarEvidenceDrawer v-if="selectedCandidate&&task&&selectedSite" :candidate="selectedCandidate" :task="task" :site="selectedSite" :sources="[...catalog.documents,...catalog.sources]" @close="selectedCandidate=undefined"/>
 </template>
</Shell></template>
<style scoped>
.lunar-mission-head{margin-bottom:28px}.lunar-task-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.lunar-task-entry{display:block;padding:28px;text-decoration:none;color:inherit;transition:border-color .15s}.lunar-task-entry:hover,.lunar-task-entry:focus-visible{border-color:var(--green)}.lunar-task-entry h3{font-size:24px;margin:18px 0 12px}.lunar-task-entry p{color:var(--muted);line-height:1.8}.lunar-task-facts{display:flex;justify-content:space-between;gap:14px;font-size:12px;margin:26px 0 20px;color:var(--muted)}.lunar-intro-note{margin-top:24px}.lunar-task-tabs{margin:0 5.5%;display:flex;flex-wrap:wrap;gap:8px;padding:0 0 30px;border-bottom:1px solid var(--line)}.lunar-task-tabs a{padding:10px 12px;border:1px solid var(--line);font-size:12px;text-decoration:none}.lunar-task-tabs .active{border-color:var(--green);color:var(--green)}.lunar-task-tabs span{margin-left:6px}.lunar-site-counts{display:flex;flex-wrap:wrap;gap:24px;margin:26px 0;font-size:13px;color:var(--muted)}.lunar-site-counts b{color:#e8edf1;margin-left:7px}.lunar-site-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.lunar-site-card{padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:4px;text-align:left;min-width:0}.lunar-site-card.selected{border-color:var(--green);box-shadow:inset 3px 0 var(--green)}.lunar-site-card h3{font-size:18px;margin:12px 0}.lunar-site-card p{font-size:13px;line-height:1.8;color:var(--muted)}.badge.primary{color:var(--green)}.badge.secondary{color:var(--blue)}.lunar-unassessed,.lunar-location-map,.lunar-validation{border-top:1px solid var(--line);padding:20px 0;margin-top:22px}.lunar-unassessed .lunar-site-grid{margin-top:18px}.lunar-reference-panel{margin-top:26px}.lunar-reference-top{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}.lunar-reference-top h3{margin:12px 0}.lunar-reference-top label{display:grid;gap:8px;font-size:12px;min-width:0}.lunar-reference-top select{max-width:100%;padding:9px}.lunar-reference-panel>p{margin:12px 0}.lunar-reference-panel>details{margin-top:18px}.lunar-contrast-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px;margin-top:32px}.lunar-contrast-group{display:flex;flex-direction:column;gap:16px;min-width:0}.lunar-group-title{display:flex;gap:10px;align-items:center}.lunar-group-title h3{font-size:19px;margin:0;flex:1}.lunar-group-dot{width:7px;height:7px;background:#91ddba;border-radius:50%}.least .lunar-group-dot{background:#d99673}.lunar-contrast-group>p{min-height:40px;margin:0 0 8px;line-height:1.8}.lunar-earth-map{margin:28px 0}.lunar-validation-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:20px}.lunar-score-formula{font-size:21px;padding:22px;border:1px solid var(--line);overflow-wrap:anywhere}.lunar-method-section p{line-height:1.9}.lunar-data-counts{display:flex;gap:60px;flex-wrap:wrap;margin:26px 0 32px}.lunar-data-counts div{display:grid;gap:8px}.lunar-data-counts strong{font:26px 'Space Mono',monospace;color:var(--blue)}.lunar-data-counts span{font-size:12px;color:var(--muted)}.lunar-source-section details{margin-top:26px}.lunar-source-section li{margin:12px 0;line-height:1.8;font-size:13px;color:var(--muted)}
@media(max-width:700px){.lunar-task-grid,.lunar-site-grid,.lunar-contrast-grid,.lunar-validation-grid{grid-template-columns:1fr}.lunar-task-entry{padding:22px}.lunar-task-tabs span{display:none}.lunar-reference-top{flex-direction:column}.lunar-reference-top label{width:100%}.lunar-data-counts{gap:28px}.lunar-score-formula{font-size:15px}.lunar-contrast-grid{gap:42px}.lunar-group-title .eyebrow{font-size:10px}}
</style>
