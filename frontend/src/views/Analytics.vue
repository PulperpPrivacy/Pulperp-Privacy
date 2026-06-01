<template>
  <div class="analytics-view">
    <div class="page-header">
      <h1>Blind Analytics</h1>
      <span class="badge">🫥 No wallet metadata</span>
    </div>
    <div class="info-box">
      Market data is queried without associating your wallet address to the request.
      Blind query keys rotate per session.
    </div>
    <div class="markets-grid">
      <div v-for="m in markets" :key="m" class="market-card" @click="selectedMarket = m" :class="{ selected: selectedMarket === m }">
        <div class="mname">{{ m }}</div>
      </div>
    </div>
    <div v-if="selectedMarket" class="panel">
      <div class="panel-header">
        <h2>{{ selectedMarket }}</h2>
        <button class="btn btn-accent" @click="genSignal" :disabled="generating">
          {{ generating ? "..." : "Generate Blind Signal" }}
        </button>
      </div>
      <div v-if="signal" class="signal-preview">
        <div class="sp-dir" :class="signal.direction.toLowerCase()">{{ signal.direction }}</div>
        <div class="sp-conf">{{ (signal.confidence * 100).toFixed(0) }}% confidence</div>
        <div class="sp-thesis">{{ signal.thesis }}</div>
        <div class="sp-privacy">🫥 {{ signal.privacy_note }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getMarkets, generateSignal } from "@/api/perp.js";

const markets = ref([]);
const selectedMarket = ref(null);
const generating = ref(false);
const signal = ref(null);

async function genSignal() {
  if (!selectedMarket.value) return;
  generating.value = true; signal.value = null;
  try { signal.value = (await generateSignal(selectedMarket.value, true)).data; }
  catch {} finally { generating.value = false; }
}

onMounted(async () => {
  try { markets.value = (await getMarkets()).data.markets; } catch {}
});
</script>

<style scoped>
.analytics-view { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; align-items: center; gap: 12px; }
.page-header h1 { font-size: 18px; color: var(--accent2); }
.badge { font-size: 11px; background: rgba(124,58,237,0.15); color: var(--accent2); padding: 3px 10px; border-radius: 4px; }
.info-box { background: var(--surface); border: 1px solid var(--border); padding: 14px 18px; border-radius: 8px; font-size: 12px; color: var(--muted); }
.markets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; }
.market-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px; cursor: pointer; transition: all 0.2s; text-align: center; }
.market-card:hover { border-color: var(--accent2); }
.market-card.selected { border-color: var(--accent2); background: rgba(124,58,237,0.08); }
.mname { font-size: 12px; font-weight: 700; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; }
.panel-header h2 { font-size: 14px; }
.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 7px 16px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn-accent { background: var(--accent); border-color: var(--accent); color: white; font-weight: 700; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.signal-preview { display: flex; flex-direction: column; gap: 10px; }
.sp-dir { font-size: 18px; font-weight: 700; }
.sp-dir.long { color: var(--green); }
.sp-dir.short { color: var(--red); }
.sp-dir.neutral { color: var(--muted); }
.sp-conf { font-size: 12px; color: var(--accent2); }
.sp-thesis { font-size: 12px; line-height: 1.7; }
.sp-privacy { font-size: 11px; color: var(--accent2); background: rgba(124,58,237,0.08); padding: 8px 12px; border-radius: 4px; }
</style>
