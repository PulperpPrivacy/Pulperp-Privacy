<template>
  <div class="signals-view">
    <div class="page-header">
      <h1>Blind Signals</h1>
      <div class="actions">
        <select v-model="selectedMarket" class="input">
          <option value="">All Markets</option>
          <option v-for="m in markets" :key="m" :value="m">{{ m }}</option>
        </select>
        <button class="btn btn-accent" @click="generate" :disabled="generating">
          {{ generating ? "Generating..." : "Generate Signal" }}
        </button>
        <button class="btn" @click="loadHistory">History</button>
      </div>
    </div>

    <div class="blind-notice">
      🫥 All signals generated in <strong>blind mode</strong> — no wallet metadata attached to LLM queries.
    </div>

    <div v-if="signals.length === 0" class="empty">No signals yet.</div>

    <div class="signals-list">
      <div v-for="sig in signals" :key="sig.id" class="sig-card" :class="sig.direction.toLowerCase()">
        <div class="sig-header">
          <span class="dir-badge" :class="sig.direction.toLowerCase()">{{ sig.direction }}</span>
          <span class="sym">{{ sig.symbol }}</span>
          <span class="conf">{{ (sig.confidence * 100).toFixed(0) }}%</span>
          <span class="tf">{{ sig.timeframe }}</span>
          <span class="blind" v-if="sig.blind_mode">🫥</span>
          <span class="ts">{{ fmtTime(sig.created_at) }}</span>
        </div>
        <div class="thesis">{{ sig.thesis }}</div>
        <div class="stats-row">
          <div class="ss"><span class="sl">Funding 8h</span><span class="sv" :class="sig.funding_rate_8h > 0 ? 'green' : 'red'">{{ (sig.funding_rate_8h * 100).toFixed(4) }}%</span></div>
          <div class="ss"><span class="sl">OI Imbal</span><span class="sv" :class="sig.oi_imbalance > 0 ? 'green' : 'red'">{{ (sig.oi_imbalance * 100).toFixed(1) }}%</span></div>
          <div class="ss"><span class="sl">Price</span><span class="sv">${{ fmtPrice(sig.price) }}</span></div>
        </div>
        <div v-if="sig.risks?.length" class="risks">
          <span v-for="r in sig.risks" :key="r" class="risk">⚠ {{ r }}</span>
        </div>
        <div v-if="sig.privacy_note" class="privacy-note">🫥 {{ sig.privacy_note }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { generateSignal, getSignalHistory, getMarkets } from "@/api/perp.js";

const signals = ref([]);
const generating = ref(false);
const markets = ref([]);
const selectedMarket = ref("SOL-PERP");

const fmtTime = (iso) => { try { return new Date(iso).toLocaleTimeString(); } catch { return ""; } };
const fmtPrice = (p) => p >= 1000 ? p.toLocaleString("en", { maximumFractionDigits: 0 }) : p?.toFixed(4);

async function generate() {
  generating.value = true;
  try {
    const symbol = selectedMarket.value || "SOL-PERP";
    const res = await generateSignal(symbol, true);
    signals.value.unshift(res.data);
  } catch (e) { console.error(e); }
  finally { generating.value = false; }
}

async function loadHistory() {
  try {
    const res = await getSignalHistory(50);
    signals.value = res.data.signals;
  } catch {}
}

onMounted(async () => {
  try { markets.value = (await getMarkets()).data.markets; } catch {}
});
</script>

<style scoped>
.signals-view { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h1 { font-size: 18px; color: var(--accent2); }
.actions { display: flex; gap: 10px; align-items: center; }
.input { background: var(--surface); border: 1px solid var(--border); color: var(--text); font-family: var(--font); font-size: 12px; padding: 7px 12px; border-radius: 6px; }
.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 7px 16px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn:hover { border-color: var(--accent2); color: var(--accent2); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-accent { background: var(--accent); border-color: var(--accent); color: white; font-weight: 700; }

.blind-notice { background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3); color: var(--accent2); padding: 10px 16px; border-radius: 6px; font-size: 12px; }
.empty { text-align: center; color: var(--muted); padding: 60px 0; }
.signals-list { display: flex; flex-direction: column; gap: 12px; }

.sig-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.sig-card.long { border-left: 3px solid var(--green); }
.sig-card.short { border-left: 3px solid var(--red); }
.sig-card.neutral { border-left: 3px solid var(--muted); }

.sig-header { display: flex; align-items: center; gap: 12px; font-size: 12px; }
.dir-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 1px; }
.dir-badge.long { background: rgba(16,185,129,0.15); color: var(--green); }
.dir-badge.short { background: rgba(239,68,68,0.15); color: var(--red); }
.dir-badge.neutral { background: rgba(71,85,105,0.2); color: var(--muted); }
.sym { font-weight: 700; }
.conf { color: var(--accent2); }
.tf { color: var(--muted); }
.blind { font-size: 14px; }
.ts { color: var(--muted); font-size: 11px; margin-left: auto; }

.thesis { font-size: 12px; line-height: 1.7; }
.stats-row { display: flex; gap: 20px; }
.ss { display: flex; flex-direction: column; gap: 2px; }
.sl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.sv { font-size: 12px; }
.green { color: var(--green); }
.red { color: var(--red); }

.risks { display: flex; flex-wrap: wrap; gap: 8px; }
.risk { font-size: 11px; color: var(--red); background: rgba(239,68,68,0.08); padding: 2px 8px; border-radius: 4px; }

.privacy-note { font-size: 11px; color: var(--accent2); background: rgba(124,58,237,0.08); padding: 6px 10px; border-radius: 4px; }
</style>
