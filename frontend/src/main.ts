import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { i18n } from './i18n'
import './style.css'
const router = createRouter({history:createWebHistory(), routes:[
  {path:'/',component:()=>import('./pages/Home.vue')},
  {path:'/method',component:()=>import('./pages/Method.vue')},
  {path:'/data',component:()=>import('./pages/Data.vue')},
  {path:'/:mission(moon|mars)',component:()=>import('./pages/Mission.vue')},
  {path:'/:pathMatch(.*)*',redirect:'/'}
],scrollBehavior:()=>({top:0})})
createApp(App).use(createPinia()).use(router).use(i18n).mount('#app')
