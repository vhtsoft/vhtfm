import './index.css'

import { createApp } from 'vue'
import { VhtfmUI, setConfig, vhtfmRequest } from 'vhtfm-ui'
import router from './router'
import App from './App.vue'

let app = createApp(App)

setConfig('resourceFetcher', vhtfmRequest)
app.use(VhtfmUI)
app.use(router)

app.mount('#app')
