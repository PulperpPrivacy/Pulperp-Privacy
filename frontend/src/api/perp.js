import api from "./index.js";

export const openPosition = (data) => api.post("/position/open", data);
export const closePosition = (id, exitPrice) => api.post(`/position/${id}/close`, { exit_price: exitPrice });
export const listPositions = (status = null) =>
  api.get("/position/", { params: status ? { status } : {} });
export const getPositionSummary = () => api.get("/position/summary");
export const generateSignal = (symbol, blind = true) =>
  api.post("/signal/generate", { symbol, blind });
export const generateAllSignals = (blind = true) =>
  api.post("/signal/generate-all", { blind });
export const getSignalHistory = (limit = 20, symbol = null) =>
  api.get("/signal/history", { params: { limit, ...(symbol && { symbol }) } });
export const getMarkets = () => api.get("/signal/markets");
export const getVaultStatus = () => api.get("/vault/status");
export const generateKeys = () => api.get("/vault/keygen");
