import { createApp } from "vue";
import App from "./App.vue";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import HighchartsVue from "highcharts-vue";

const app = createApp(App);

app.use(HighchartsVue);
app.mount("#app");
