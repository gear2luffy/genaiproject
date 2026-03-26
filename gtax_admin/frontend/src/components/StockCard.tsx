import React from 'react';
import { Link } from 'react-router-dom';
import SignalBadge from './SignalBadge';

interface StockCardProps {
  symbol: string;
  price: number;
  changePercent: number;
  opportunityScore: number;
  technicalScore: number;
  volumeScore: number;
  signal?: 'BUY' | 'SELL' | 'HOLD';
  confidence?: number;
}

const StockCard: React.FC<StockCardProps> = ({
  symbol,
  price,
  changePercent,
  opportunityScore,
  technicalScore,
  volumeScore,
  signal,
  confidence,
}) => {
  const isPositive = changePercent >= 0;

  return (
    <Link
      to={`/stock/${symbol}`}
      className="block bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition-colors border border-gray-700 hover:border-gray-600"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-bold text-white">{symbol}</h3>
          <p
            className={`text-sm ${
              isPositive ? 'text-green-400' : 'text-red-400'
            }`}
          >
            ${price?.toFixed(2)} ({isPositive ? '+' : ''}
            {changePercent?.toFixed(2)}%)
          </p>
        </div>
        {signal && <SignalBadge signal={signal} confidence={confidence} />}
      </div>

      <div className="space-y-2">
        <ScoreBar label="Opportunity" value={opportunityScore} />
        <ScoreBar label="Technical" value={technicalScore} color="blue" />
        <ScoreBar label="Volume" value={volumeScore} color="purple" />
      </div>
    </Link>
  );
};

interface ScoreBarProps {
  label: string;
  value: number;
  color?: 'green' | 'blue' | 'purple' | 'yellow';
}

const ScoreBar: React.FC<ScoreBarProps> = ({ label, value, color = 'green' }) => {
  const colors = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500',
  };

  const percentage = Math.max(0, Math.min(100, value * 100));

  return (
    <div>
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{label}</span>
        <span>{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors[color]} rounded-full transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default StockCard;
