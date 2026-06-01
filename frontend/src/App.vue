<template>
  <div id="pulperp">
    <nav class="nav">
      <div class="brand">
        <span class="logo">🫥</span>
        <span class="name">Pulperp Privacy</span>
        <span class="tag">Private Perps · Solana</span>
      </div>
      <div class="links">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/vault">Vault</router-link>
        <router-link to="/signals">Signals</router-link>
        <router-link to="/analytics">Analytics</router-link>
      </div>
      <div class="status">
        <span class="dot" :class="online ? 'on' : 'off'"></span>
        <span class="blind-badge" v-if="online">🫥 BLIND MODE</span>
      </div>
    </nav>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/api/index.js";
const online = ref(false);
onMounted(async () => {
  try { await api.get("/health", { baseURL: "/" }); online.value = true; } catch {}
});
</script>

<style>
:root {
  --bg: #07070c;
  --surface: #0d0d14;
  --border: #161625;
  --accent: #7c3aed;
  --accent2: #a78bfa;
  --green: #10b981;
  --red: #ef4444;
  --text: #e2e8f0;
  --muted: #475569;
  --font: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 13px; line-height: 1.6; }

#pulperp { min-height: 100vh; display: flex; flex-direction: column; }

.nav {
  display: flex; align-items: center; gap: 24px;
  padding: 12px 24px;
  background: var(--surface); border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
}

.brand { display: flex; align-items: center; gap: 8px; }
.logo { font-size: 18px; }
.name { font-size: 15px; font-weight: 700; color: var(--accent2); }
.tag { font-size: 11px; color: var(--muted); border-left: 1px solid var(--border); padding-left: 10px; }

.links { display: flex; gap: 16px; margin-left: auto; }
.links a { color: var(--muted); text-decoration: none; font-size: 12px; transition: color 0.2s; }
.links a:hover, .links a.router-link-active { color: var(--accent2); }

.status { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.dot { width: 7px; height: 7px; border-radius: 50%; }
.dot.on { background: var(--green); }
.dot.off { background: var(--red); }
.blind-badge { color: var(--accent2); font-size: 10px; background: rgba(124,58,237,0.15); padding: 2px 8px; border-radius: 4px; }

.main { flex: 1; padding: 24px; max-width: 1400px; width: 100%; margin: 0 auto; }
</style>
