import { createApp } from 'vue'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap"
import App from './App.vue'
import router from './router'

import "@/assets/base.css"

const app = createApp(App)
app.use(router);
app.mount('#app');

