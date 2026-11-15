<script setup lang="ts">
import {ref,computed,onMounted,onBeforeUnmount,watch} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import Shell from '../components/Shell.vue'
import EarthMap from '../components/EarthMap.vue'
import PlanetTargetMap from '../components/PlanetTargetMap.vue'
import MarsCandidateCard from '../components/MarsCandidateCard.vue'
import MarsEvidenceDrawer from '../components/MarsEvidenceDrawer.vue'
import {api,errorMessage} from '../api'
import {localizeData} from '../i18n'
import type {MarsCatalog,MarsComparison,MarsNetwork,MarsGlobalGrid,MarsEarthCandidate,MarsTask} from '../marsHandoffTypes'
import type {Candidate,Site} from '../types'
const {t,locale}=useI18n();const route=useRoute();const router=useRouter()
const raw=ref<MarsCatalog>();const resultRaw=ref<MarsComparison>();const network=ref<MarsNetwork>();const globalNetwork=ref<MarsNetwork>();const grid=ref<MarsGlobalGrid>()
const loading=ref(true);const busy=ref(false);const error=ref('');const networkError=ref('');const gridError=ref('');const globalError=ref('');const globalBusy=ref(false)
const selected=ref<MarsEarthCandidate>();const selectedTask=ref<MarsTask>();const showGrid=ref(false)
const catalog=computed(()=>raw.value?localizeData(raw.value,locale.value):undefined)
const result=computed(()=>resultRaw.value?localizeData(resultRaw.value,locale.value):undefined)
const ids=['R1','R2','R3','R4','R5','R6'];const dimensions=['terrain','surface','environment','water_ice','atmosphere_dust']
const selectedIds=computed(()=>typeof route.query.tasks==='string'?route.query.tasks.split(',').filter(id=>ids.includes(id)):['R1','R4','R6'])
const taskIds=computed(()=>[...new Set(selectedIds.value)])
const step=computed(()=>[1,2,3].includes(Number(route.query.step))?Number(route.query.step):1)
const site=computed(()=>catalog.value?.mars_sites.find(s=>s.id===(route.query.site||'mars-jezero')))
const mapSites=computed<Site[]>(()=>catalog.value?.mars_sites.map(s=>({id:s.id,mission:'mars',name:s.name,name_en:s.name,lat:s.lat,lon:s.lon,coords_status:'approx',source:'Mars handoff 2026-11-15',description:t('marsStudyRadius',{radius:s.radius_km}),description_en:''}))||[])
const activeTask=computed(()=>typeof route.query.test==='string'&&taskIds.value.includes(route.query.test)?route.query.test:taskIds.value[0])
const activeGroup=computed(()=>result.value?.groups.find(g=>g.task_id===activeTask.value))
const mapCandidates=computed<Candidate[]>(()=>activeGroup.value?.ranking?[...activeGroup.value.ranking.new_candidates.slice(0,3),...activeGroup.value.ranking.least_similar].map(c=>({id:c.id,name:c.lat+'°, '+c.lon+'°',name_en:c.name_en??'',lat:c.lat,lon:c.lon,known_analog:false,is_placeholder:false,overall:c.score===null?null:c.score/100,tasks:{}})):[])
const gridPoints=computed(()=>{if(!showGrid.value||!grid.value||!site.value||!activeGroup.value?.ranking)return [];const index=grid.value.meta.columns.indexOf(site.value.target_id+'_'+activeTask.value);if(index<0)return [];return grid.value.rows.filter(row=>row[index]!==null).map(row=>({lat:row[0]!,lon:row[1]!,score:row[index]!}))})
const mapSettings={gibs_url:'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg',fallback_url:'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',max_zoom:8}
let version=0;let controller:AbortController|undefined;let gridController:AbortController|undefined;let globalController:AbortController|undefined
function query(update:Record<string,string|undefined>){void router.replace({query:{...route.query,...update}})}
function go(value:number){query({step:String(value)})}
function toggle(id:string){const next=taskIds.value.includes(id)?taskIds.value.filter(t=>t!==id):ids.filter(t=>t===id||taskIds.value.includes(t));query({tasks:next.join(','),test:undefined})}
function chooseSite(id:string){query({site:id})}
function open(candidate:MarsEarthCandidate){selectedTask.value=activeGroup.value?.task;selected.value=candidate}
function openMap(id:string){const candidate=activeGroup.value?.ranking?.new_candidates.concat(activeGroup.value.ranking.least_similar).find(c=>c.id===id);if(candidate)open(candidate)}
async function load(){loading.value=true;error.value='';try{raw.value=await api.marsHandoff()}catch(e){error.value=errorMessage(e)}finally{loading.value=false}}
async function calculate(){
 const current=++version;controller?.abort();selected.value=undefined;resultRaw.value=undefined;network.value=undefined;networkError.value='';error.value='';busy.value=false
 if(!raw.value||step.value!==3)return
 if(!site.value){error.value=t('marsUnknownSite');return}
 if(!taskIds.value.length){error.value=t('noTasks');return}
 const targetId=site.value.id;const selectedTests=[...taskIds.value];const requestController=new AbortController();controller=requestController;busy.value=true
 const responses=await Promise.allSettled([api.marsComparison(targetId,selectedTests,requestController.signal),api.marsNetwork(targetId,selectedTests,requestController.signal)])
 if(current!==version)return
 const [comparison,coverage]=responses
 if(comparison.status==='fulfilled'){
  const value=comparison.value
  if(value.site.id!==targetId||value.version!==raw.value.meta.version||value.generated!==raw.value.meta.generated||value.groups.map(g=>g.task_id).join(',')!==selectedTests.join(','))error.value=t('marsResponseMismatch')
  else resultRaw.value=value
 }else if(!requestController.signal.aborted)error.value=errorMessage(comparison.reason)
 if(coverage.status==='fulfilled'&&coverage.value.version===raw.value.meta.version)network.value=coverage.value
 else if(!requestController.signal.aborted)networkError.value=coverage.status==='rejected'?errorMessage(coverage.reason):t('marsResponseMismatch')
 busy.value=false
}
async function loadGrid(){if(!showGrid.value||grid.value)return;gridError.value='';gridController?.abort();gridController=new AbortController();try{const data=await api.marsGrid(gridController.signal);if(data.meta.version!==raw.value?.meta.version)throw new Error(t('marsResponseMismatch'));grid.value=data}catch(e){if(!gridController.signal.aborted){gridError.value=errorMessage(e);showGrid.value=false}}}
async function loadGlobal(){if(globalBusy.value||globalNetwork.value)return;globalError.value='';globalBusy.value=true;globalController=new AbortController();try{const data=await api.marsNetwork('all',[],globalController.signal);if(data.version!==raw.value?.meta.version)throw new Error(t('marsResponseMismatch'));globalNetwork.value=data}catch(e){if(!globalController.signal.aborted)globalError.value=errorMessage(e)}finally{globalBusy.value=false}}
watch(()=>[raw.value?.meta.version,step.value,site.value?.id,taskIds.value.join(',')],calculate)
watch(showGrid,loadGrid)
onMounted(load)
onBeforeUnmount(()=>{version++;controller?.abort();gridController?.abort();globalController?.abort()})
</script>
<template><Shell>
 <div v-if="loading" class="loading-state" role="status"><span class="spinner"></span>{{t('loading')}}</div>
 <div v-if="error" class="error-panel" role="alert">{{error}} <button class="button" @click="raw?calculate():load()">{{t('retry')}}</button></div>
 <template v-if="catalog&&!loading">
  <div class="mission-head"><router-link to="/" class="breadcrumb">← {{t('home')}}</router-link><div class="mission-title-row"><div><span class="eyebrow">MARS / ANALOG EXPLORER</span><h1>{{t('marsMissionHeading')}}</h1><p>{{t('marsMissionIntro')}}</p></div><div class="mini-planet mars" aria-hidden="true"></div></div></div>
  <nav class="wizard-nav" :aria-label="t('marsMissionHeading')"><button v-for="n in [1,2,3]" :key="n" :class="{current:step===n,done:step>n}" :disabled="n>1&&!taskIds.length||n===3&&!site" @click="go(n)"><span class="step-number mono">0{{n}}</span>{{t('step'+n)}}<i v-if="n<3">→</i></button></nav>
  <section v-if="step===1" class="section" data-testid="mars-task-picker"><div class="section-heading"><h2>{{t('step1')}}</h2><span class="eyebrow">06 / {{t('marsTests')}}</span></div><div class="task-grid"><button v-for="id in ids" :key="id" class="task-card" :class="{selected:taskIds.includes(id)}" :aria-pressed="taskIds.includes(id)" :data-task-id="id" @click="toggle(id)"><span class="mono">{{id}}</span><h3>{{catalog.tasks[id].name}}</h3><p>{{t('marsPurpose_'+id)}}</p><span class="badge" :class="catalog.tasks[id].status==='scored'?'similar':''">{{t(catalog.tasks[id].status==='scored'?'marsScored':'marsNotEvaluated')}}</span><span v-if="catalog.tasks[id].applies==='ice'" class="small muted"> · SWIM Ci ≥ 0.1</span></button></div><p class="small muted">{{t('marsRequired')}}</p><div class="step-actions"><button class="button primary" :disabled="!taskIds.length" @click="go(2)">{{t('next')}} →</button></div></section>
  <section v-if="step===2" class="section" data-testid="mars-target-picker"><h2>{{t('step2')}}</h2><p class="small muted">{{t('marsCoordinateNote')}}</p><PlanetTargetMap :sites="mapSites" :selected-id="site?.id??''" mission="mars" :imported-ids="catalog.mars_sites.map(s=>s.id)" @select="chooseSite"/><div class="site-grid"><button v-for="target in catalog.mars_sites" :key="target.id" class="task-card" :class="{selected:site?.id===target.id}" :aria-pressed="site?.id===target.id" :data-site-id="target.id" @click="chooseSite(target.id)"><h3>{{target.name}}</h3><p class="mono">{{target.lat}}°, {{target.lon}}°</p><p>{{t('marsStudyRadius',{radius:target.radius_km})}} · SWIM Ci {{target.ice_ci}}</p><p class="small muted">{{target.scored_tests.join(' · ')}}</p></button></div><div class="step-actions"><button class="button" @click="go(1)">← {{t('back')}}</button><button class="button primary" :disabled="!site" @click="go(3)">{{t('step3')}} →</button></div></section>
  <section v-if="step===3" class="section" data-testid="mars-results" :aria-busy="busy">
   <div class="section-heading"><div><span class="eyebrow">03 / EARTH</span><h2>{{site?.name}}</h2></div><button class="button" @click="go(2)">{{t('changeTarget')}}</button></div>
   <p class="notice">{{t('marsScoreMeaning')}}</p><p class="small muted">{{t('marsRequired')}}</p>
   <div v-if="busy" class="loading-state" role="status"><span class="spinner"></span>{{t('calculating')}}</div>
   <template v-if="result">
    <nav class="lunar-task-tabs" :aria-label="t('taskComparisons')"><button v-for="group in result.groups" :key="group.task_id" class="button" :class="{primary:activeTask===group.task_id}" @click="query({test:group.task_id})">{{group.task_id}} · {{group.task.name}}</button></nav>
    <section v-if="activeGroup" class="result-section" data-testid="mars-task-comparison"><h2>{{activeGroup.task.name}}</h2>
     <div v-if="!activeGroup.ranking" class="no-comparison-panel" data-testid="mars-unscored"><h3>{{t(activeGroup.status==='not_applicable'?'marsNotApplicable':'marsNotEvaluated')}}</h3><p>{{t(activeGroup.status==='not_applicable'?'marsIceRule':'marsR2Reason')}}</p></div>
     <template v-else><p class="small muted">{{t('marsRankingScope',{count:activeGroup.ranking.n_cells_scored.toLocaleString()})}}</p><p class="small muted">{{t('marsPlaceNote')}}</p>
      <div class="mars-contrast-grid"><section data-testid="mars-most"><h3>{{t('lunarMostSimilar')}}</h3><MarsCandidateCard v-for="candidate in activeGroup.ranking.new_candidates.slice(0,3)" :key="candidate.id" :candidate="candidate" @select="open"/></section><section data-testid="mars-least"><h3>{{t('lunarLeastSimilar')}}</h3><MarsCandidateCard v-for="candidate in activeGroup.ranking.least_similar" :key="candidate.id" :candidate="candidate" @select="open"/></section></div>
      <label class="switch-label"><input v-model="showGrid" type="checkbox"/>{{t('marsShowGrid')}}</label><p v-if="gridError" class="warning" role="alert">{{gridError}}</p><p v-if="showGrid" class="small muted">{{t('marsGridMeaning')}} <span class="grid-legend">0 <i></i> 100</span></p><EarthMap :candidates="mapCandidates" :settings="mapSettings" :similar-cutoff=".6" :different-cutoff=".3" :score-scale="100" :grid-points="gridPoints" @select="openMap"/>
      <details class="mars-details"><summary>{{t('lunarMoreCandidates')}}</summary><div class="mars-card-grid"><MarsCandidateCard v-for="candidate in activeGroup.ranking.new_candidates.slice(3)" :key="candidate.id" :candidate="candidate" @select="open"/></div></details>
      <details class="mars-details"><summary>{{t('lunarValidationTitle')}}</summary><p>{{t('marsKnownRule')}}</p><div v-if="activeGroup.ranking.known_analogs_in_top.length" class="mars-card-grid"><MarsCandidateCard v-for="candidate in activeGroup.ranking.known_analogs_in_top" :key="candidate.id" :candidate="candidate" @select="open"/></div><p class="small muted">{{t('marsKnownMedian')}}</p><div class="table-scroll"><table><thead><tr><th>{{t('candidate')}}</th><th>{{t('score')}}</th><th>{{t('marsGlobalPercentile')}}</th></tr></thead><tbody><tr v-for="known in activeGroup.ranking.known_analogs_validation" :key="known.site_id"><th>{{known.name_en}}</th><td>{{known.score?.toFixed(1)??'—'}}</td><td>{{known.global_top_pct===null?'—':known.global_top_pct+'%'}}</td></tr></tbody></table></div></details>
      <details class="mars-details"><summary>{{t('lunarHowScored')}}</summary><p class="mono">100 × exp(Σ ln(max(s, 0.01)) / n)</p><p>{{t('marsConditional')}}</p><div class="table-scroll"><table><thead><tr><th>{{t('features')}}</th><th>{{t('lunarFormula')}}</th></tr></thead><tbody><tr v-for="feature in activeGroup.task.features" :key="feature.id"><th>{{t('marsFeature_'+feature.id)}}</th><td class="small mono">{{feature.formula}}</td></tr></tbody></table></div></details>
     </template>
    </section>
    <section class="result-section"><h2>{{t('marsProfileTitle')}}</h2><p>{{t('marsProfileMeaning')}}</p><details class="mars-details"><summary>{{t('marsProfileOpen')}}</summary><div class="table-scroll"><table><thead><tr><th>{{t('candidate')}}</th><th>{{t('overall')}}</th><th v-for="dimension in dimensions" :key="dimension">{{t('marsDimension_'+dimension)}}</th></tr></thead><tbody><tr v-for="candidate in result.profile.overall_top" :key="candidate.cell_id"><th>{{candidate.lat}}°, {{candidate.lon}}°<small class="profile-place">{{candidate.name_en}}</small><a v-if="candidate.worldview_url" :href="candidate.worldview_url" target="_blank" rel="noopener" class="small">Worldview ↗</a></th><td>{{candidate.score.toFixed(1)}}</td><td v-for="dimension in dimensions" :key="dimension">{{candidate.dimension_scores[dimension]===null?'—':((candidate.dimension_scores[dimension]??0)*100).toFixed(1)}}</td></tr></tbody></table></div><details v-for="dimension in dimensions" :key="dimension" class="mars-details"><summary>{{t('marsDimension_'+dimension)}} · TOP 5</summary><ol><li v-for="candidate in result.profile.by_dimension[dimension]" :key="candidate.cell_id">{{candidate.lat}}°, {{candidate.lon}}° · {{((candidate.dimension_scores[dimension]??0)*100).toFixed(1)}} / 100 · {{candidate.name_en}}</li></ol></details></details></section>
    <section class="result-section" data-testid="mars-network"><h2>{{t('marsNetworkTitle')}}</h2><p>{{t('marsNetworkRule')}}</p><p v-if="networkError" class="warning" role="alert">{{networkError}}</p><template v-if="network"><p class="network-count"><strong>{{network.k_star}}</strong> {{t('sitesUnit')}} / {{network.n_requirements}} {{t('marsRequirements')}}</p><p v-if="network.skipped?.length" class="small muted">{{t('marsSkipped')}}: {{network.skipped.join(' · ')}}</p><div class="table-scroll"><table><thead><tr><th>{{t('candidate')}}</th><th>{{t('marsAssigned')}}</th></tr></thead><tbody><tr v-for="point in network.sites" :key="point.cell_id"><th>{{point.lat}}°, {{point.lon}}°<small class="profile-place">{{point.place}}</small></th><td><span v-for="assignment in point.assigned" :key="assignment.test" class="weight-chip">{{assignment.test}} {{(assignment.score*100).toFixed(1)}} / 100 </span></td></tr></tbody></table></div><p class="small muted">{{t('marsPoolScope')}}</p></template>
     <details class="mars-details" @toggle="e=>{if((e.target as HTMLDetailsElement).open)loadGlobal()}"><summary>{{t('marsGlobalNetwork')}}</summary><p v-if="globalBusy">{{t('loading')}}</p><p v-if="globalError" class="warning" role="alert">{{globalError}} <button @click="loadGlobal">{{t('retry')}}</button></p><template v-if="globalNetwork"><p>{{globalNetwork.k_star}} {{t('sitesUnit')}} / {{globalNetwork.n_requirements}} {{t('marsRequirements')}}</p><ol><li v-for="point in globalNetwork.sites" :key="point.cell_id">{{point.lat}}°, {{point.lon}}° · {{point.place}}<p class="small muted">{{point.assigned.map(a=>a.target+' '+a.test).join(' · ')}}</p></li></ol><h4>{{t('marginal')}}</h4><p class="small">{{globalNetwork.marginal_curve.map(row=>row.k+' → '+row.covered+'/27').join(' · ')}}</p><h4>{{t('sensitivity')}}</h4><p v-for="row in globalNetwork.sensitivity" :key="row.rule" class="small">{{localizeData(row.rule,locale)}} → {{row.k_star}} {{t('sitesUnit')}}</p></template></details>
    </section>
    <section class="result-section"><h2>{{t('marsValidationTitle')}}</h2><p>{{t('marsValidationSummary',{pairs:result.validation.known_pairs,percent:result.validation.median_best_dimension_top_pct,controls:result.validation.negative_controls})}}</p><p class="small muted">{{t('marsStability')}}</p></section>
   </template>
   <div class="step-actions"><button class="button" @click="go(1)">← {{t('step1')}}</button><button class="button" @click="go(2)">{{t('step2')}}</button></div>
  </section>
  <section class="section"><div class="section-heading"><h2>{{t('lunarSourceHeading')}}</h2><router-link to="/method">{{t('method')}} ↗</router-link></div><p>{{t('marsDataScope')}}</p><div class="inline-links"><a href="/api/measurements/mars-handoff" target="_blank" rel="noopener">{{t('lunarDownloadRankings')}} ↗</a><a href="/api/measurements/mars-grid" download>{{t('lunarDownloadGrid')}} ↓</a><a href="/api/measurements/mars-pool" download>{{t('marsDownloadPool')}} ↓</a></div><details class="mars-details"><summary>{{t('lunarSourcesAndLimits')}}</summary><ul><li v-for="note in catalog.meta.limitations" :key="note">{{note}}</li></ul><h4>{{t('earth')}}</h4><ul><li v-for="source in catalog.meta.data_sources.earth_datasets" :key="source">{{source}}</li></ul><h4>{{t('mars')}}</h4><ul><li v-for="source in catalog.meta.data_sources.mars_datasets" :key="source">{{source}}</li></ul><p class="small muted">{{catalog.meta.ai_disclosure}}</p></details></section>
  <MarsEvidenceDrawer v-if="selected&&selectedTask&&site" :candidate="selected" :task="selectedTask" :site="site" @close="selected=undefined"/>
 </template>
</Shell></template>
<style scoped>
.task-grid,.site-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:24px}.task-card{text-align:left;color:inherit;cursor:pointer}.task-card.selected{border-color:#85dfbe}.task-card p{line-height:1.7}.mars-contrast-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px}.mars-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.mars-details{border-top:1px solid var(--line);padding:22px 0}.mars-details summary{cursor:pointer}.profile-place{display:block;font-size:11px;font-weight:400;color:var(--muted);margin:8px 0}.network-count strong{font-size:40px;color:#85dfbe}.weight-chip{display:inline-block;padding:8px;border:1px solid var(--line);margin:4px}.grid-legend{display:inline-flex;align-items:center;gap:8px}.grid-legend i{display:inline-block;width:100px;height:8px;background:linear-gradient(90deg,#be7557,#d8c48e,#85dfbe)}@media(max-width:800px){.task-grid,.site-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mars-contrast-grid,.mars-card-grid{grid-template-columns:1fr}}@media(max-width:500px){.task-grid,.site-grid{grid-template-columns:1fr}}
</style>
