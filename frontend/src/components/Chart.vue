<script setup lang="ts">
import {use} from 'echarts/core'
import {CanvasRenderer} from 'echarts/renderers'
import {LineChart,BarChart} from 'echarts/charts'
import {GridComponent,TooltipComponent,LegendComponent,TitleComponent} from 'echarts/components'
import VChart from 'vue-echarts'
import type {EChartsOption} from 'echarts'
use([CanvasRenderer,LineChart,BarChart,GridComponent,TooltipComponent,LegendComponent,TitleComponent])
defineProps<{option:EChartsOption;label:string}>()
</script>
<template><VChart :option="option" autoresize class="chart" role="img" :aria-label="label" /></template>
