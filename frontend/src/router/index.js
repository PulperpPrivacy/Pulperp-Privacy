import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "@/views/Dashboard.vue";
import Vault from "@/views/Vault.vue";
import Signals from "@/views/Signals.vue";
import Analytics from "@/views/Analytics.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "Dashboard", component: Dashboard },
    { path: "/vault", name: "Vault", component: Vault },
    { path: "/signals", name: "Signals", component: Signals },
    { path: "/analytics", name: "Analytics", component: Analytics },
  ],
});
