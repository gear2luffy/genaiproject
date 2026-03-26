import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Scanner API
export const scannerApi = {
  scan: (topN = 10, refresh = false) => 
    api.get(`/scan?top_n=${topN}&refresh=${refresh}`),
  analyzeSymbol: (symbol: string) => 
    api.get(`/scan/${symbol}`),
  getStatus: () => 
    api.get('/scan/status'),
};

// Sentiment API
export const sentimentApi = {
  getSymbolSentiment: (symbol: string, refresh = false) =>
    api.get(`/news-sentiment/${symbol}?refresh=${refresh}`),
  getBulkSentiment: (symbols?: string[]) => {
    const params = symbols ? `?symbols=${symbols.join(',')}` : '';
    return api.get(`/news-sentiment${params}`);
  },
  getSummary: (symbol: string) =>
    api.get(`/news-sentiment/${symbol}/summary`),
};

// Patterns API
export const patternsApi = {
  getPatterns: (symbol: string, period = '3mo', interval = '1d') =>
    api.get(`/patterns/${symbol}?period=${period}&interval=${interval}`),
  getSummary: (symbol: string) =>
    api.get(`/patterns/${symbol}/summary`),
  getSupportResistance: (symbol: string) =>
    api.get(`/patterns/${symbol}/support-resistance`),
};

// Signals API
export const signalsApi = {
  getSignal: (symbol: string, includeSentiment = true) =>
    api.get(`/signals/${symbol}?include_sentiment=${includeSentiment}`),
  getBulkSignals: (symbols?: string[], actionableOnly = false) => {
    let params = `?actionable_only=${actionableOnly}`;
    if (symbols) params += `&symbols=${symbols.join(',')}`;
    return api.get(`/signals${params}`);
  },
  getBreakdown: (symbol: string) =>
    api.get(`/signals/${symbol}/breakdown`),
  getCustomSignal: (symbol: string, config: any) =>
    api.post(`/signals/custom/${symbol}`, config),
};

// Trading API
export const tradingApi = {
  executeTrade: (tradeRequest: any) =>
    api.post('/trade', tradeRequest),
  getPortfolio: () =>
    api.get('/portfolio'),
  getPositions: () =>
    api.get('/positions'),
  closePosition: (symbol: string) =>
    api.post(`/close/${symbol}`),
  getOrders: () =>
    api.get('/orders'),
  getTradeHistory: () =>
    api.get('/trades'),
  updatePositions: () =>
    api.post('/update-positions'),
  calculatePositionSize: (capital: number, riskPct: number, entryPrice: number, stopLoss: number) =>
    api.get(`/risk/position-size?capital=${capital}&risk_pct=${riskPct}&entry_price=${entryPrice}&stop_loss=${stopLoss}`),
  calculateRiskLevels: (entryPrice: number, stopLossPct = 0.02, riskReward = 2.0) =>
    api.get(`/risk/levels?entry_price=${entryPrice}&stop_loss_pct=${stopLossPct}&risk_reward=${riskReward}`),
};

// Backtest API
export const backtestApi = {
  runBacktest: (request: any) =>
    api.post('/backtest', request),
  runDetailedBacktest: (request: any) =>
    api.post('/backtest/detailed', request),
  trainModel: (request: any) =>
    api.post('/train', request),
  getPrediction: (symbol: string, modelType = 'random_forest') =>
    api.get(`/predict/${symbol}?model_type=${modelType}`),
  listModels: () =>
    api.get('/models'),
};

export default api;
