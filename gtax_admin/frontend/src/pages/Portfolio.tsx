import React, { useEffect, useState } from 'react';
import { tradingApi } from '../services/api';

interface Position {
  symbol: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  stop_loss?: number;
  take_profit?: number;
}

interface Trade {
  symbol: string;
  side: string;
  quantity: number;
  entry_price?: number;
  exit_price?: number;
  pnl?: number;
  pnl_pct?: number;
  timestamp: string;
}

interface PortfolioData {
  initial_capital: number;
  cash: number;
  positions_value: number;
  portfolio_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  positions: Position[];
  recent_trades: Trade[];
}

const Portfolio: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [tradeHistory, setTradeHistory] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [closingPosition, setClosingPosition] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [portfolioRes, historyRes] = await Promise.all([
        tradingApi.getPortfolio(),
        tradingApi.getTradeHistory(),
      ]);
      setPortfolio(portfolioRes.data);
      setTradeHistory(historyRes.data);
    } catch (err) {
      console.error('Failed to fetch portfolio:', err);
    } finally {
      setLoading(false);
    }
  };

  const closePosition = async (symbol: string) => {
    setClosingPosition(symbol);
    try {
      await tradingApi.closePosition(symbol);
      fetchData();
    } catch (err) {
      console.error('Failed to close position:', err);
    } finally {
      setClosingPosition(null);
    }
  };

  const updatePositions = async () => {
    try {
      await tradingApi.updatePositions();
      fetchData();
    } catch (err) {
      console.error('Failed to update positions:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfolio</h1>
          <p className="text-gray-400">Paper Trading Account</p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={updatePositions}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Update Prices
          </button>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {portfolio && (
        <>
          {/* Portfolio Summary */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <SummaryCard
              title="Portfolio Value"
              value={`$${portfolio.portfolio_value.toLocaleString()}`}
              icon="💰"
            />
            <SummaryCard
              title="Cash"
              value={`$${portfolio.cash.toLocaleString()}`}
              icon="💵"
            />
            <SummaryCard
              title="Positions Value"
              value={`$${portfolio.positions_value.toLocaleString()}`}
              icon="📊"
            />
            <SummaryCard
              title="Total P&L"
              value={`$${portfolio.total_pnl.toLocaleString()}`}
              subtext={`${portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl_pct.toFixed(2)}%`}
              icon={portfolio.total_pnl >= 0 ? '📈' : '📉'}
              color={portfolio.total_pnl >= 0 ? 'green' : 'red'}
            />
            <SummaryCard
              title="Positions"
              value={portfolio.positions.length.toString()}
              icon="🎯"
            />
          </div>

          {/* Positions */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Open Positions</h2>
            {portfolio.positions.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-gray-400 text-sm border-b border-gray-700">
                      <th className="text-left py-3">Symbol</th>
                      <th className="text-right py-3">Quantity</th>
                      <th className="text-right py-3">Avg Cost</th>
                      <th className="text-right py-3">Current</th>
                      <th className="text-right py-3">Market Value</th>
                      <th className="text-right py-3">P&L</th>
                      <th className="text-right py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.positions.map((position) => (
                      <tr key={position.symbol} className="border-b border-gray-700">
                        <td className="py-4">
                          <span className="font-semibold text-white">
                            {position.symbol}
                          </span>
                        </td>
                        <td className="text-right text-gray-300">
                          {position.quantity.toFixed(2)}
                        </td>
                        <td className="text-right text-gray-300">
                          ${position.average_cost.toFixed(2)}
                        </td>
                        <td className="text-right text-white">
                          ${position.current_price.toFixed(2)}
                        </td>
                        <td className="text-right text-gray-300">
                          ${position.market_value.toFixed(2)}
                        </td>
                        <td
                          className={`text-right font-medium ${
                            position.unrealized_pnl >= 0
                              ? 'text-green-400'
                              : 'text-red-400'
                          }`}
                        >
                          ${position.unrealized_pnl.toFixed(2)}
                          <span className="text-xs ml-1">
                            ({position.unrealized_pnl >= 0 ? '+' : ''}
                            {position.unrealized_pnl_pct.toFixed(2)}%)
                          </span>
                        </td>
                        <td className="text-right">
                          <button
                            onClick={() => closePosition(position.symbol)}
                            disabled={closingPosition === position.symbol}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors disabled:opacity-50"
                          >
                            {closingPosition === position.symbol
                              ? 'Closing...'
                              : 'Close'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                No open positions
              </div>
            )}
          </div>

          {/* Trade History */}
          {tradeHistory && (
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-white">Trade History</h2>
                {tradeHistory.count > 0 && (
                  <div className="flex space-x-4 text-sm">
                    <span className="text-gray-400">
                      Win Rate:{' '}
                      <span className="text-white font-medium">
                        {tradeHistory.win_rate.toFixed(1)}%
                      </span>
                    </span>
                    <span className="text-gray-400">
                      Total P&L:{' '}
                      <span
                        className={`font-medium ${
                          tradeHistory.total_pnl >= 0
                            ? 'text-green-400'
                            : 'text-red-400'
                        }`}
                      >
                        ${tradeHistory.total_pnl.toFixed(2)}
                      </span>
                    </span>
                  </div>
                )}
              </div>

              {tradeHistory.trades?.length > 0 ? (
                <div className="space-y-2">
                  {tradeHistory.trades.slice(-10).reverse().map((trade: Trade, idx: number) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center py-3 border-b border-gray-700"
                    >
                      <div className="flex items-center space-x-4">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            trade.side === 'BUY'
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {trade.side}
                        </span>
                        <span className="font-medium text-white">
                          {trade.symbol}
                        </span>
                        <span className="text-gray-400 text-sm">
                          {trade.quantity} shares
                        </span>
                      </div>
                      <div className="text-right">
                        {trade.pnl !== undefined && (
                          <span
                            className={`font-medium ${
                              trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}
                          >
                            {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                          </span>
                        )}
                        <p className="text-gray-500 text-xs">
                          {new Date(trade.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  No trades yet
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

interface SummaryCardProps {
  title: string;
  value: string;
  subtext?: string;
  icon: string;
  color?: 'green' | 'red';
}

const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  subtext,
  icon,
  color,
}) => {
  const textColor = color === 'green' 
    ? 'text-green-400' 
    : color === 'red' 
    ? 'text-red-400' 
    : 'text-white';

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-start">
        <span className="text-2xl">{icon}</span>
        {subtext && (
          <span className={`text-sm ${textColor}`}>{subtext}</span>
        )}
      </div>
      <p className={`text-xl font-bold mt-2 ${textColor}`}>{value}</p>
      <p className="text-gray-400 text-sm">{title}</p>
    </div>
  );
};

export default Portfolio;
