<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1>Privacy Dashboard</h1>
        <p class="subtitle">Your positions are nobody's business.</p>
      </div>
      <button class="btn" @click="loadAll" :disabled="loading">Refresh</button>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="sl">Open Positions</div>
        <div class="sv accent">{{ summary.open }}</div>
      </div>
      <div class="stat-card">
        <div class="sl">Total Closed</div>
        <div class="sv">{{ summary.closed }}</div>
      </div>
      <div class="stat-card">
        <div class="sl">Avg PnL</div>
        <div class="sv" :class="summary.avg_pnl_pct >= 0 ? 'green' : 'red'">
          {{ summary.avg_pnl_pct >= 0 ? '+' : '' }}{{ summary.avg_pnl_pct?.toFixed(2) }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="sl">Vault</div>
        <div class="sv accent2">{{ vaultStatus.encryption }}</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <div class="panel-header"><h2>Open Position</h2><span class="badge">🫥 Commitment Masked</span></div>
        <div class="form-grid">
          <select v-model="form.symbol" class="input">
            <option v-for="m in markets" :key="m" :value="m">{{ m }}</option>
          </select>
          <select v-model="form.direction" class="input">
            <option value="LONG">LONG</option>
            <option value="SHORT">SHORT</option>
          </select>
          <input v-model="form.size" class="input" placeholder="Size (SOL)" type="number" step="0.01" />
          <input v-model="form.entry_price" class="input" placeholder="Entry price" type="number" />
          <input v-model="form.leverage" class="input" placeholder="Leverage (e.g. 5)" type="number" />
        </div>
        <button class="btn btn-accent" @click="openPos" :disabled="opening">
          {{ opening ? "Committing..." : "Open Private Position" }}
        </button>
        <div v-if="openResult" class="result-box">
          <div class="rrow"><span class="rl">Vault ID</span><span class="rv">{{ openResult.vault_id?.slice(0,16) }}...</span></div>
          <div class="rrow"><span class="rl">Commitment</span><span class="rv muted">{{ openResult.commitment_hash }}</span></div>
          <div class="rrow"><span class="rl">Masked Size</span><span class="rv accent">{{ openResult.masked_size }}</span></div>
          <div class="rrow"><span class="rl">Status</span><span class="rv green">{{ openResult.status }}</span></div>
        </div>
        <div v-if="openError" class="err">{{ openError }}</div>
      </div>

      <div class="panel">
        <div class="panel-header"><h2>Open Positions</h2></div>
        <div v-if="positions.length === 0" class="empty">No open positions.</div>
        <div v-for="p in positions" :key="p.id" class="pos-row">
          <span class="pos-dir" :class="p.direction === 'LONG' ? 'green' : 'red'">{{ p.direction }}</span>
          <span class="pos-symbol">{{ p.symbol }}</span>
          <span class="pos-size muted">{{ p.masked_size }}</span>
          <span class="pos-lev">{{ p.leverage }}x</span>
          <span class="pos-pnl" v-if="p.pnl_pct !== null" :class="p.pnl_pct >= 0 ? 'green' : 'red'">
            {{ p.pnl_pct >= 0 ? '+' : '' }}{{ p.pnl_pct?.toFixed(2) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { listPositions, openPosition, getPositionSummary, getVaultStatus, getMarkets } from "@/api/perp.js";

const loading = ref(false);
const opening = ref(false);
const openResult = ref(null);
const openError = ref(null);
const positions = ref([]);
const markets = ref(["SOL-PERP", "BTC-PERP", "ETH-PERP", "WIF-PERP", "BONK-PERP"]);
const summary = reactive({ open: 0, closed: 0, avg_pnl_pct: 0 });
const vaultStatus = reactive({ encryption: "—" });
const form = reactive({ symbol: "SOL-PERP", direction: "LONG", size: "", entry_price: "", leverage: "" });

async function loadAll() {
  loading.value = true;
  try {
    const [posRes, sumRes, vaultRes, mktRes] = await Promise.all([
      listPositions("open"), getPositionSummary(), getVaultStatus(), getMarkets(),
    ]);
    positions.value = posRes.data.positions;
    Object.assign(summary, sumRes.data);
    Object.assign(vaultStatus, vaultRes.data);
    markets.value = mktRes.data.markets;
  } catch {} finally { loading.value = false; }
}

async function openPos() {
  opening.value = true; openResult.value = null; openError.value = null;
  try {
    const res = await openPosition({ ...form, size: +form.size, entry_price: +form.entry_price, leverage: +form.leverage });
    openResult.value = res.data;
    await loadAll();
  } catch (e) { openError.value = e.response?.data?.error || e.message; }
  finally { opening.value = false; }
}

onMounted(loadAll);
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-header h1 { font-size: 18px; color: var(--accent2); }
.subtitle { color: var(--muted); font-size: 11px; margin-top: 2px; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.sl { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.sv { font-size: 22px; font-weight: 700; margin-top: 4px; }
.accent { color: var(--accent2); }
.accent2 { color: var(--green); font-size: 13px; }
.green { color: var(--green); }
.red { color: var(--red); }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.panel-header { display: flex; align-items: center; gap: 10px; }
.panel-header h2 { font-size: 14px; }
.badge { font-size: 10px; background: rgba(124,58,237,0.15); color: var(--accent2); padding: 2px 8px; border-radius: 4px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.input { background: var(--bg); border: 1px solid var(--border); color: var(--text); font-family: var(--font); font-size: 12px; padding: 7px 10px; border-radius: 6px; width: 100%; }

.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 7px 16px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; transition: all 0.2s; }
.btn:hover { border-color: var(--accent2); color: var(--accent2); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-accent { background: var(--accent); border-color: var(--accent); color: white; font-weight: 700; }

.result-box { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 4px; }
.rrow { display: flex; gap: 12px; font-size: 11px; }
.rl { color: var(--muted); min-width: 90px; }
.rv { color: var(--text); }
.muted { color: var(--muted); font-size: 10px; }
.err { color: var(--red); font-size: 11px; }

.empty { color: var(--muted); text-align: center; padding: 20px 0; font-size: 12px; }
.pos-row { display: flex; gap: 12px; align-items: center; font-size: 12px; padding: 6px 0; border-bottom: 1px solid var(--border); }
.pos-dir { font-size: 10px; font-weight: 700; min-width: 40px; }
.pos-symbol { min-width: 80px; }
.pos-size { font-size: 11px; }
.pos-lev { color: var(--muted); font-size: 11px; }
.pos-pnl { margin-left: auto; }
</style>
