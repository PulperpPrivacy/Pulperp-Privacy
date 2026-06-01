<template>
  <div class="vault-view">
    <div class="page-header">
      <h1>Encrypted Vault</h1>
      <div class="vault-status" :class="vaultStatus.encryption === 'enabled' ? 'secure' : 'warn'">
        {{ vaultStatus.encryption === 'enabled' ? '🔒 Encrypted' : '⚠ Plaintext Mode' }}
      </div>
    </div>

    <div v-if="vaultStatus.encryption !== 'enabled'" class="warn-banner">
      VAULT_ENCRYPTION_KEY not set. Run <code>GET /api/vault/keygen</code> and add keys to .env
    </div>

    <div class="stats-row">
      <div class="stat-card"><div class="sl">Total</div><div class="sv">{{ vaultStatus.total }}</div></div>
      <div class="stat-card"><div class="sl">Open</div><div class="sv accent">{{ vaultStatus.open }}</div></div>
      <div class="stat-card"><div class="sl">Closed</div><div class="sv">{{ vaultStatus.closed }}</div></div>
      <div class="stat-card">
        <div class="sl">Avg PnL</div>
        <div class="sv" :class="(vaultStatus.avg_pnl_pct || 0) >= 0 ? 'green' : 'red'">
          {{ (vaultStatus.avg_pnl_pct || 0) >= 0 ? '+' : '' }}{{ (vaultStatus.avg_pnl_pct || 0).toFixed(2) }}%
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>All Positions</h2>
        <button class="btn" @click="loadPositions">Refresh</button>
      </div>
      <div v-if="positions.length === 0" class="empty">No positions in vault.</div>
      <table v-else class="table">
        <thead>
          <tr><th>Direction</th><th>Symbol</th><th>Size</th><th>Entry ≈</th><th>Lev</th><th>Status</th><th>PnL</th><th>Opened</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in positions" :key="p.id">
            <td><span class="dir" :class="p.direction === 'LONG' ? 'green' : 'red'">{{ p.direction }}</span></td>
            <td>{{ p.symbol }}</td>
            <td class="muted">{{ p.masked_size }}</td>
            <td class="muted">${{ p.entry_price_approx?.toLocaleString() }}</td>
            <td>{{ p.leverage }}x</td>
            <td><span class="status-b" :class="p.status">{{ p.status }}</span></td>
            <td :class="(p.pnl_pct || 0) >= 0 ? 'green' : 'red'">
              {{ p.pnl_pct != null ? ((p.pnl_pct >= 0 ? '+' : '') + p.pnl_pct.toFixed(2) + '%') : '—' }}
            </td>
            <td class="muted ts">{{ fmtTime(p.opened_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { listPositions, getVaultStatus } from "@/api/perp.js";

const positions = ref([]);
const vaultStatus = reactive({ total: 0, open: 0, closed: 0, avg_pnl_pct: 0, encryption: "—" });
const fmtTime = (iso) => { try { return new Date(iso).toLocaleString(); } catch { return ""; } };

async function loadPositions() {
  try { positions.value = (await listPositions()).data.positions; } catch {}
}

onMounted(async () => {
  try { Object.assign(vaultStatus, (await getVaultStatus()).data); } catch {}
  await loadPositions();
});
</script>

<style scoped>
.vault-view { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h1 { font-size: 18px; color: var(--accent2); }
.vault-status { font-size: 12px; padding: 6px 14px; border-radius: 6px; font-weight: 700; }
.vault-status.secure { background: rgba(16,185,129,0.1); color: var(--green); }
.vault-status.warn { background: rgba(239,68,68,0.1); color: var(--red); }
.warn-banner { background: rgba(239,68,68,0.08); border: 1px solid var(--red); color: var(--red); padding: 10px 16px; border-radius: 6px; font-size: 12px; }
.warn-banner code { font-family: var(--font); color: var(--accent2); }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.sl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.sv { font-size: 22px; font-weight: 700; margin-top: 4px; }
.accent { color: var(--accent2); }
.green { color: var(--green); }
.red { color: var(--red); }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-header h2 { font-size: 14px; }
.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 6px 14px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn:hover { border-color: var(--accent2); color: var(--accent2); }
.empty { color: var(--muted); text-align: center; padding: 40px 0; }
.table { width: 100%; border-collapse: collapse; font-size: 12px; }
.table th { text-align: left; color: var(--muted); font-size: 10px; text-transform: uppercase; padding: 8px 10px; border-bottom: 1px solid var(--border); }
.table td { padding: 8px 10px; border-bottom: 1px solid var(--border); }
.dir { font-size: 10px; font-weight: 700; }
.muted { color: var(--muted); }
.ts { font-size: 11px; }
.status-b { font-size: 10px; padding: 2px 6px; border-radius: 3px; }
.status-b.open { background: rgba(16,185,129,0.1); color: var(--green); }
.status-b.closed { background: rgba(71,85,105,0.15); color: var(--muted); }
</style>
