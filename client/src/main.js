import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap"
import { createPinia } from 'pinia'

createApp(App).use(router).use(createPinia()).mount('#app')
