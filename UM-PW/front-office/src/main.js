import { createApp } from "vue";
import App from "./App.vue";
import router from "./router"; // Importa o roteador

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

const app = createApp(App);

app.config.devtools = true;

app.use(router); // Usa o Vue Router
app.mount("#app");
