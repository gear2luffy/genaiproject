import React, { useState } from 'react';
import { backtestApi } from '../services/api';

interface BacktestResult {
  symbols: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  total_trades: number;
  metrics: {
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    win_rate: number;
    profit_factor: number;
    avg_trade_pnl: number;
    total_pnl: number;
    winning_trades: number;
    losing_trades: number;
  };
  equity_curve?: Array<{ date: string; equity: number }>;
  trades?: Array<any>;
}

const Backtest: React.FC = () => {
  const [symbols, setSymbols] = useState('AAPL,GOOGL,MSFT,AMZN');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  const [initialCapital, setInitialCapital] = useState(100000);
  const [threshold, setThreshold] = useState(0.3);
  const [positionSize, setPositionSize] = useState(0.1);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await backtestApi.runDetailedBacktest({
        symbols: symbols.split(',').map((s) => s.trim().toUpperCase()),
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        strategy_params: {
          threshold: threshold,
          position_size: positionSize,
        },
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Backtesting</h1>
        <p className="text-gray-400">Test trading strategies on historical data</p>
      </div>

      {/* Configuration */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-400 text-sm mb-2">Symbols (comma-separated)</label>
            <input
              type="text"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">Initial Capital ($)</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">Signal Threshold</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">Position Size (%)</label>
            <input
              type="number"
              step="0.05"
              min="0.01"
              max="1"
              value={positionSize}
              onChange={(e) => setPositionSize(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={runBacktest}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 font-semibold"
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              title="Final Capital"
              value={`$${result.final_capital.toLocaleString()}`}
              subtitle={`${result.total_return >= 0 ? '+' : ''}${result.total_return.toFixed(2)}%`}
              color={result.total_return >= 0 ? 'green' : 'red'}
            />
            <MetricCard
              title="Total Trades"
              value={result.total_trades.toString()}
              subtitle={`${result.metrics.winning_trades}W / ${result.metrics.losing_trades}L`}
            />
            <MetricCard
              title="Win Rate"
              value={`${result.metrics.win_rate.toFixed(1)}%`}
              color={result.metrics.win_rate >= 50 ? 'green' : 'red'}
            />
            <MetricCard
              title="Profit Factor"
              value={result.metrics.profit_factor.toFixed(2)}
              color={result.metrics.profit_factor >= 1 ? 'green' : 'red'}
            />
          </div>

          {/* Detailed Metrics */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Performance Metrics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <MetricItem
                label="Sharpe Ratio"
                value={result.metrics.sharpe_ratio.toFixed(3)}
                description="Risk-adjusted return"
              />
              <MetricItem
                label="Sortino Ratio"
                value={result.metrics.sortino_ratio.toFixed(3)}
                description="Downside risk-adjusted"
              />
              <MetricItem
                label="Max Drawdown"
                value={`${result.metrics.max_drawdown.toFixed(2)}%`}
                description="Largest peak-to-trough"
                negative
              />
              <MetricItem
                label="Avg Trade P&L"
                value={`$${result.metrics.avg_trade_pnl.toFixed(2)}`}
                description="Per trade average"
              />
            </div>
          </div>

          {/* Trade History */}
          {result.trades && result.trades.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4">
                Trade History ({result.trades.length} trades)
              </h2>
              <div className="max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-gray-800">
                    <tr className="text-gray-400 text-sm border-b border-gray-700">
                      <th className="text-left py-2">Date</th>
                      <th className="text-left py-2">Symbol</th>
                      <th className="text-left py-2">Side</th>
                      <th className="text-right py-2">Price</th>
                      <th className="text-right py-2">Shares</th>
                      <th className="text-right py-2">P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.trades.map((trade, idx) => (
                      <tr key={idx} className="border-b border-gray-700 text-sm">
                        <td className="py-2 text-gray-400">
                          {trade.date?.split('T')[0]}
                        </td>
                        <td className="py-2 text-white font-medium">
                          {trade.symbol}
                        </td>
                        <td className="py-2">
                          <span
                            className={`px-2 py-0.5 rounded text-xs ${
                              trade.side === 'BUY'
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-red-500/20 text-red-400'
                            }`}
                          >
                            {trade.side}
                          </span>
                        </td>
                        <td className="py-2 text-right text-gray-300">
                          ${trade.price?.toFixed(2)}
                        </td>
                        <td className="py-2 text-right text-gray-300">
                          {trade.shares?.toFixed(2)}
                        </td>
                        <td
                          className={`py-2 text-right font-medium ${
                            trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          {trade.pnl !== undefined
                            ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}`
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  color?: 'green' | 'red';
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, color }) => {
  const valueColor = color === 'green' 
    ? 'text-green-400' 
    : color === 'red' 
    ? 'text-red-400' 
    : 'text-white';

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <p className="text-gray-400 text-sm">{title}</p>
      <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
      {subtitle && <p className={`text-sm ${valueColor}`}>{subtitle}</p>}
    </div>
  );
};

interface MetricItemProps {
  label: string;
  value: string;
  description: string;
  negative?: boolean;
}

const MetricItem: React.FC<MetricItemProps> = ({ label, value, description, negative }) => (
  <div>
    <p className="text-gray-400 text-sm">{label}</p>
    <p className={`text-xl font-bold ${negative ? 'text-red-400' : 'text-white'}`}>
      {value}
    </p>
    <p className="text-gray-500 text-xs">{description}</p>
  </div>
);

export default Backtest;
