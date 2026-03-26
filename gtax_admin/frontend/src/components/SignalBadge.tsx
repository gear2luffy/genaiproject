import React from 'react';

interface SignalBadgeProps {
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
}

const SignalBadge: React.FC<SignalBadgeProps> = ({ signal, confidence, size = 'md' }) => {
  const colors = {
    BUY: 'bg-green-500/20 text-green-400 border-green-500',
    SELL: 'bg-red-500/20 text-red-400 border-red-500',
    HOLD: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border ${colors[signal]} ${sizes[size]}`}
    >
      {signal}
      {confidence !== undefined && (
        <span className="ml-1 opacity-75">({(confidence * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
};

export default SignalBadge;
