import React from 'react';

interface SentimentIndicatorProps {
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  score: number;
  showScore?: boolean;
}

const SentimentIndicator: React.FC<SentimentIndicatorProps> = ({
  sentiment,
  score,
  showScore = true,
}) => {
  const colors = {
    POSITIVE: {
      bg: 'bg-green-500',
      text: 'text-green-400',
      label: '😊 Positive',
    },
    NEGATIVE: {
      bg: 'bg-red-500',
      text: 'text-red-400',
      label: '😟 Negative',
    },
    NEUTRAL: {
      bg: 'bg-yellow-500',
      text: 'text-yellow-400',
      label: '😐 Neutral',
    },
  };

  const config = colors[sentiment];

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center">
        <span className={`w-3 h-3 rounded-full ${config.bg} mr-2`}></span>
        <span className={`text-sm font-medium ${config.text}`}>{config.label}</span>
      </div>
      {showScore && (
        <span className="text-gray-400 text-sm">({score.toFixed(2)})</span>
      )}
    </div>
  );
};

export default SentimentIndicator;
