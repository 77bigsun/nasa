import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig({
  plugins: [vue(), {name: 'health', configureServer(server) {server.middlewares.use('/health', (_req, res) => {res.setHeader('Content-Type', 'application/json'); res.end('{"status":"ok"}')})}}],
  server: {port: 5173, proxy: {
    '/api/similarity/optimize': {target:'http://127.0.0.1:8004', rewrite:()=>'/optimize'},
    '/api/similarity/sensitivity': {target:'http://127.0.0.1:8004', rewrite:()=>'/sensitivity'},
    '/api/catalog': {target:'http://127.0.0.1:8001', rewrite:p=>p.replace('/api/catalog','')},
    '/api/similarity': {target:'http://127.0.0.1:8002', rewrite:p=>p.replace('/api/similarity','')},
    '/api/measurements': {target:'http://127.0.0.1:8003', rewrite:p=>p.replace('/api/measurements','')},
    '/api/planning': {target:'http://127.0.0.1:8004', rewrite:p=>p.replace('/api/planning','')}
  }},
  build: {chunkSizeWarningLimit: 2200, rollupOptions: {output: {manualChunks(id) {if(id.includes('globe')||id.includes('/three/'))return 'globe';if(id.includes('echarts')||id.includes('zrender'))return 'charts'}}}}
})
