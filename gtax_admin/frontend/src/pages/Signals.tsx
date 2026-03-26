import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { signalsApi } from '../services/api';
import SignalBadge from '../components/SignalBadge';

interface Signal {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  technical_score: number;
  pattern_score: number;
  sentiment_score: number;
  price: number;
  target_price?: number;
  stop_loss?: number;
  reasoning: string[];
  timestamp: string;
}

const Signals: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL');
  const [sortBy, setSortBy] = useState<'confidence' | 'timestamp'>('confidence');

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const response = await signalsApi.getBulkSignals(undefined, false);
      setSignals(response.data.signals);
    } catch (err) {
      console.error('Failed to fetch signals:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredSignals = signals
    .filter((s) => filter === 'ALL' || s.signal === filter)
    .sort((a, b) => {
      if (sortBy === 'confidence') {
        return b.confidence - a.confidence;
      }
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

  const actionableCount = signals.filter(
    (s) => s.signal !== 'HOLD' && s.confidence >= 0.65
  ).length;

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
          <h1 className="text-2xl font-bold text-white">AI Trading Signals</h1>
          <p className="text-gray-400">
            {actionableCount} actionable signals from {signals.length} analyzed
          </p>
        </div>
        <button
          onClick={fetchSignals}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Signals
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <div className="flex bg-gray-800 rounded-lg p-1">
          {(['ALL', 'BUY', 'SELL', 'HOLD'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === f
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'confidence' | 'timestamp')}
          className="bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700"
        >
          <option value="confidence">Sort by Confidence</option>
          <option value="timestamp">Sort by Time</option>
        </select>
      </div>

      {/* Signal Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Total Signals</p>
          <p className="text-2xl font-bold text-white">{signals.length}</p>
        </div>
        <div className="bg-green-500/20 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Buy Signals</p>
          <p className="text-2xl font-bold text-green-400">
            {signals.filter((s) => s.signal === 'BUY').length}
          </p>
        </div>
        <div className="bg-red-500/20 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Sell Signals</p>
          <p className="text-2xl font-bold text-red-400">
            {signals.filter((s) => s.signal === 'SELL').length}
          </p>
        </div>
        <div className="bg-yellow-500/20 rounded-lg p-4">
          <p className="text-gray-400 text-sm">Hold Signals</p>
          <p className="text-2xl font-bold text-yellow-400">
            {signals.filter((s) => s.signal === 'HOLD').length}
          </p>
        </div>
      </div>

      {/* Signal Cards */}
      <div className="space-y-4">
        {filteredSignals.map((signal) => (
          <Link
            key={signal.symbol}
            to={`/stock/${signal.symbol}`}
            className="block bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 hover:border-gray-600"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="flex items-center space-x-3">
                  <h3 className="text-xl font-bold text-white">{signal.symbol}</h3>
                  <SignalBadge signal={signal.signal} confidence={signal.confidence} />
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  ${signal.price?.toFixed(2)}
                </p>
              </div>
              <div className="text-right">
                {signal.target_price && (
                  <p className="text-green-400 text-sm">
                    Target: ${signal.target_price.toFixed(2)}
                  </p>
                )}
                {signal.stop_loss && (
                  <p className="text-red-400 text-sm">
                    Stop: ${signal.stop_loss.toFixed(2)}
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <ScoreBar
                label="Technical"
                value={signal.technical_score}
                color="blue"
              />
              <ScoreBar
                label="Pattern"
                value={signal.pattern_score}
                color="purple"
              />
              <ScoreBar
                label="Sentiment"
                value={signal.sentiment_score}
                color="green"
              />
            </div>

            <div className="text-gray-400 text-sm">
              {signal.reasoning?.slice(0, 2).map((r, idx) => (
                <p key={idx}>• {r}</p>
              ))}
            </div>
          </Link>
        ))}
      </div>

      {filteredSignals.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400">No signals match the current filter</p>
        </div>
      )}
    </div>
  );
};

interface ScoreBarProps {
  label: string;
  value: number;
  color: 'blue' | 'purple' | 'green';
}

const ScoreBar: React.FC<ScoreBarProps> = ({ label, value, color }) => {
  const colors = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
  };

  const isPositive = value >= 0;
  const absValue = Math.abs(value);
  const percentage = Math.min(absValue * 100, 100);

  return (
    <div>
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{label}</span>
        <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
          {isPositive ? '+' : ''}{(value * 100).toFixed(0)}%
        </span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors[color]} rounded-full transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default Signals;
