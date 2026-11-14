import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { i18n,loadContentTranslations } from './i18n'
import './style.css'
const router = createRouter({history:createWebHistory(), routes:[
  {path:'/',component:()=>import('./pages/Home.vue')},
  {path:'/method',component:()=>import('./pages/Method.vue')},
  {path:'/research',component:()=>import('./pages/Research.vue')},
  {path:'/data',component:()=>import('./pages/Data.vue')},
  {path:'/moon',name:'lunar-tasks',component:()=>import('./pages/LunarMission.vue')},
  {path:'/moon/:task(M2|M3|M4|M6)',name:'lunar-task',component:()=>import('./pages/LunarMission.vue')},
  {path:'/moon/observed',redirect:to=>({path:'/moon',query:to.query})},
  {path:'/:mission(mars)',component:()=>import('./pages/Mission.vue')},
  {path:'/:pathMatch(.*)*',redirect:'/'}
],scrollBehavior:(to,from)=>to.path===from.path?false:({top:0})})
createApp(App).use(createPinia()).use(router).use(i18n).mount('#app')

void loadContentTranslations()
