import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { scannerApi, signalsApi, sentimentApi, patternsApi, tradingApi } from '../services/api';
import SignalBadge from '../components/SignalBadge';
import SentimentIndicator from '../components/SentimentIndicator';

const StockDetail: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [analysis, setAnalysis] = useState<any>(null);
  const [signal, setSignal] = useState<any>(null);
  const [sentiment, setSentiment] = useState<any>(null);
  const [patterns, setPatterns] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tradeLoading, setTradeLoading] = useState(false);
  const [tradeResult, setTradeResult] = useState<any>(null);

  useEffect(() => {
    if (symbol) {
      fetchAllData();
    }
  }, [symbol]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [analysisRes, signalRes, sentimentRes, patternsRes] = await Promise.all([
        scannerApi.analyzeSymbol(symbol!),
        signalsApi.getBreakdown(symbol!),
        sentimentApi.getSymbolSentiment(symbol!),
        patternsApi.getPatterns(symbol!),
      ]);

      setAnalysis(analysisRes.data);
      setSignal(signalRes.data);
      setSentiment(sentimentRes.data);
      setPatterns(patternsRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  };

  const executeTrade = async (side: 'BUY' | 'SELL') => {
    setTradeLoading(true);
    try {
      const response = await tradingApi.executeTrade({
        symbol: symbol,
        side: side,
        risk_pct: 0.02,
        use_risk_management: true,
      });
      setTradeResult(response.data);
    } catch (err: any) {
      setTradeResult({ status: 'error', message: err.message });
    } finally {
      setTradeLoading(false);
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
      <div className="flex justify-between items-start">
        <div>
          <Link to="/" className="text-blue-400 hover:text-blue-300 text-sm mb-2 block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white">{symbol}</h1>
          {analysis && (
            <div className="flex items-center space-x-4 mt-2">
              <span className="text-2xl text-white">${analysis.price?.toFixed(2)}</span>
              <span
                className={`text-lg ${
                  analysis.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {analysis.change_percent >= 0 ? '+' : ''}
                {analysis.change_percent?.toFixed(2)}%
              </span>
            </div>
          )}
        </div>
        {signal && (
          <div className="text-right">
            <SignalBadge signal={signal.final_signal} confidence={signal.final_confidence} size="lg" />
            <p className="text-gray-400 text-sm mt-2">AI Recommendation</p>
          </div>
        )}
      </div>

      {/* Trade Actions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Quick Trade</h2>
        <div className="flex space-x-4">
          <button
            onClick={() => executeTrade('BUY')}
            disabled={tradeLoading}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
          >
            {tradeLoading ? 'Processing...' : 'Buy'}
          </button>
          <button
            onClick={() => executeTrade('SELL')}
            disabled={tradeLoading}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
          >
            {tradeLoading ? 'Processing...' : 'Sell'}
          </button>
        </div>
        {tradeResult && (
          <div
            className={`mt-4 p-4 rounded-lg ${
              tradeResult.status === 'success'
                ? 'bg-green-500/20 border border-green-500'
                : 'bg-red-500/20 border border-red-500'
            }`}
          >
            {tradeResult.status === 'success' ? (
              <div>
                <p className="text-green-400 font-semibold">Order Executed!</p>
                <p className="text-gray-300 text-sm">
                  {tradeResult.order?.side} {tradeResult.order?.quantity} @ ${tradeResult.order?.filled_price?.toFixed(2)}
                </p>
              </div>
            ) : (
              <p className="text-red-400">{tradeResult.message}</p>
            )}
          </div>
        )}
      </div>

      {/* Signal Breakdown */}
      {signal && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Signal Breakdown</h2>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <ScoreBox
              title="Technical"
              score={signal.components?.technical?.score}
              weight={signal.components?.technical?.weight}
              color="blue"
            />
            <ScoreBox
              title="Patterns"
              score={signal.components?.patterns?.score}
              weight={signal.components?.patterns?.weight}
              color="purple"
            />
            <ScoreBox
              title="Sentiment"
              score={signal.components?.sentiment?.score}
              weight={signal.components?.sentiment?.weight}
              color="green"
            />
          </div>

          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-400">Reasoning</h3>
            {signal.reasoning?.map((reason: string, idx: number) => (
              <p key={idx} className="text-gray-300 text-sm">• {reason}</p>
            ))}
          </div>

          {signal.targets && (
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-gray-400 text-sm">Entry</p>
                <p className="text-white font-semibold">${signal.targets.entry_price?.toFixed(2)}</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400 text-sm">Target</p>
                <p className="text-green-400 font-semibold">${signal.targets.target_price?.toFixed(2)}</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400 text-sm">Stop Loss</p>
                <p className="text-red-400 font-semibold">${signal.targets.stop_loss?.toFixed(2)}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sentiment */}
      {sentiment && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">News Sentiment</h2>
          <div className="flex items-center justify-between mb-4">
            <SentimentIndicator
              sentiment={sentiment.sentiment}
              score={sentiment.score}
            />
            <span className="text-gray-400 text-sm">
              {sentiment.news_count} articles analyzed
            </span>
          </div>

          <div className="flex space-x-4 mb-4">
            <div className="flex-1 bg-green-500/20 rounded-lg p-3 text-center">
              <p className="text-green-400 text-2xl font-bold">{sentiment.positive_count}</p>
              <p className="text-gray-400 text-sm">Positive</p>
            </div>
            <div className="flex-1 bg-gray-700 rounded-lg p-3 text-center">
              <p className="text-gray-300 text-2xl font-bold">{sentiment.neutral_count}</p>
              <p className="text-gray-400 text-sm">Neutral</p>
            </div>
            <div className="flex-1 bg-red-500/20 rounded-lg p-3 text-center">
              <p className="text-red-400 text-2xl font-bold">{sentiment.negative_count}</p>
              <p className="text-gray-400 text-sm">Negative</p>
            </div>
          </div>

          {sentiment.news_items?.slice(0, 3).map((item: any, idx: number) => (
            <div key={idx} className="border-t border-gray-700 pt-3 mt-3">
              <p className="text-white text-sm font-medium">{item.title}</p>
              <div className="flex justify-between items-center mt-1">
                <span className="text-gray-500 text-xs">{item.source}</span>
                <span
                  className={`text-xs ${
                    item.sentiment === 'POSITIVE'
                      ? 'text-green-400'
                      : item.sentiment === 'NEGATIVE'
                      ? 'text-red-400'
                      : 'text-gray-400'
                  }`}
                >
                  {item.sentiment}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Patterns */}
      {patterns && patterns.patterns?.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Detected Patterns</h2>
          <div className="space-y-3">
            {patterns.patterns.slice(0, 5).map((pattern: any, idx: number) => (
              <div
                key={idx}
                className="flex justify-between items-center py-2 border-b border-gray-700"
              >
                <div>
                  <p className="text-white font-medium">
                    {pattern.pattern_type.replace(/_/g, ' ')}
                  </p>
                  <p className="text-gray-400 text-sm">{pattern.description}</p>
                </div>
                <div className="text-right">
                  <span
                    className={`text-sm font-medium ${
                      pattern.direction === 'BULLISH'
                        ? 'text-green-400'
                        : pattern.direction === 'BEARISH'
                        ? 'text-red-400'
                        : 'text-gray-400'
                    }`}
                  >
                    {pattern.direction}
                  </span>
                  <p className="text-gray-500 text-xs">
                    {(pattern.confidence * 100).toFixed(0)}% confidence
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Technical Indicators */}
      {analysis && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Technical Indicators</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <IndicatorBox label="RSI" value={analysis.rsi} suffix="" />
            <IndicatorBox label="MACD" value={analysis.macd} />
            <IndicatorBox label="ADX" value={analysis.adx} suffix="" />
            <IndicatorBox label="SMA 20" value={analysis.sma_20} prefix="$" />
            <IndicatorBox label="SMA 50" value={analysis.sma_50} prefix="$" />
            <IndicatorBox label="BB Upper" value={analysis.bollinger_upper} prefix="$" />
            <IndicatorBox label="BB Lower" value={analysis.bollinger_lower} prefix="$" />
            <IndicatorBox
              label="Volume Score"
              value={analysis.volume_score * 100}
              suffix="%"
            />
          </div>
        </div>
      )}
    </div>
  );
};

interface ScoreBoxProps {
  title: string;
  score: number;
  weight: number;
  color: 'blue' | 'purple' | 'green';
}

const ScoreBox: React.FC<ScoreBoxProps> = ({ title, score, weight, color }) => {
  const colors = {
    blue: 'text-blue-400 bg-blue-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    green: 'text-green-400 bg-green-500/20',
  };

  return (
    <div className={`rounded-lg p-4 ${colors[color].split(' ')[1]}`}>
      <p className="text-gray-400 text-sm">{title}</p>
      <p className={`text-2xl font-bold ${colors[color].split(' ')[0]}`}>
        {(score * 100).toFixed(0)}%
      </p>
      <p className="text-gray-500 text-xs">Weight: {(weight * 100).toFixed(0)}%</p>
    </div>
  );
};

interface IndicatorBoxProps {
  label: string;
  value?: number;
  prefix?: string;
  suffix?: string;
}

const IndicatorBox: React.FC<IndicatorBoxProps> = ({
  label,
  value,
  prefix = '',
  suffix = '',
}) => (
  <div className="bg-gray-700 rounded-lg p-3">
    <p className="text-gray-400 text-xs">{label}</p>
    <p className="text-white font-semibold">
      {value !== null && value !== undefined
        ? `${prefix}${value.toFixed(2)}${suffix}`
        : 'N/A'}
    </p>
  </div>
);

export default StockDetail;
