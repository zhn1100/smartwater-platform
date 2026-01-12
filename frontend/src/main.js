import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/theme.css'

// 导入dataV组件
import dataV from '@kjgl77/datav-vue3'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.use(dataV)
app.mount('#app')
