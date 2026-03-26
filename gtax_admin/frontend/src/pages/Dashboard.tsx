import React, { useEffect, useState } from 'react';
import { scannerApi, signalsApi } from '../services/api';
import StockCard from '../components/StockCard';
import useWebSocket from '../hooks/useWebSocket';

interface ScanResult {
  symbol: string;
  price: number;
  change_percent: number;
  opportunity_score: number;
  technical_score: number;
  volume_score: number;
  rsi?: number;
  adx?: number;
}

interface Signal {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
}

const Dashboard: React.FC = () => {
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [signals, setSignals] = useState<Map<string, Signal>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { isConnected, lastMessage } = useWebSocket('/live');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'scanner') {
      setScanResults(lastMessage.data);
    }
  }, [lastMessage]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [scanResponse, signalsResponse] = await Promise.all([
        scannerApi.scan(10, true),
        signalsApi.getBulkSignals(undefined, false),
      ]);

      setScanResults(scanResponse.data.data);
      
      const signalMap = new Map<string, Signal>();
      signalsResponse.data.signals.forEach((s: Signal) => {
        signalMap.set(s.symbol, s);
      });
      setSignals(signalMap);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
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
          <h1 className="text-2xl font-bold text-white">Market Dashboard</h1>
          <p className="text-gray-400">Top AI-picked trading opportunities</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-sm">
            <span
              className={`w-2 h-2 rounded-full mr-2 ${
                isConnected ? 'bg-green-400' : 'bg-red-400'
              }`}
            ></span>
            <span className="text-gray-400">
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Scanned"
          value={scanResults.length.toString()}
          icon="📊"
        />
        <StatCard
          title="Buy Signals"
          value={Array.from(signals.values()).filter(s => s.signal === 'BUY').length.toString()}
          icon="🟢"
          color="green"
        />
        <StatCard
          title="Sell Signals"
          value={Array.from(signals.values()).filter(s => s.signal === 'SELL').length.toString()}
          icon="🔴"
          color="red"
        />
        <StatCard
          title="Avg Opportunity"
          value={`${(
            (scanResults.reduce((sum, r) => sum + r.opportunity_score, 0) /
              scanResults.length) *
            100
          ).toFixed(0)}%`}
          icon="🎯"
          color="blue"
        />
      </div>

      {/* Stock Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">
          Top Opportunities
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scanResults.map((result) => {
            const signal = signals.get(result.symbol);
            return (
              <StockCard
                key={result.symbol}
                symbol={result.symbol}
                price={result.price}
                changePercent={result.change_percent}
                opportunityScore={result.opportunity_score}
                technicalScore={result.technical_score}
                volumeScore={result.volume_score}
                signal={signal?.signal}
                confidence={signal?.confidence}
              />
            );
          })}
        </div>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Best Technical */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            🔧 Best Technical Setup
          </h3>
          <div className="space-y-3">
            {[...scanResults]
              .sort((a, b) => b.technical_score - a.technical_score)
              .slice(0, 5)
              .map((result) => (
                <div
                  key={result.symbol}
                  className="flex justify-between items-center py-2 border-b border-gray-700"
                >
                  <span className="font-medium text-white">{result.symbol}</span>
                  <div className="flex items-center space-x-4">
                    {result.rsi && (
                      <span className="text-gray-400 text-sm">
                        RSI: {result.rsi.toFixed(0)}
                      </span>
                    )}
                    <span className="text-blue-400">
                      {(result.technical_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* High Volume */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            📈 High Volume Activity
          </h3>
          <div className="space-y-3">
            {[...scanResults]
              .sort((a, b) => b.volume_score - a.volume_score)
              .slice(0, 5)
              .map((result) => (
                <div
                  key={result.symbol}
                  className="flex justify-between items-center py-2 border-b border-gray-700"
                >
                  <span className="font-medium text-white">{result.symbol}</span>
                  <div className="flex items-center space-x-4">
                    <span
                      className={`text-sm ${
                        result.change_percent >= 0
                          ? 'text-green-400'
                          : 'text-red-400'
                      }`}
                    >
                      {result.change_percent >= 0 ? '+' : ''}
                      {result.change_percent?.toFixed(2)}%
                    </span>
                    <span className="text-purple-400">
                      {(result.volume_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string;
  icon: string;
  color?: 'green' | 'red' | 'blue' | 'yellow';
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  color = 'blue',
}) => {
  const colors = {
    green: 'text-green-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        <span className={`text-2xl font-bold ${colors[color]}`}>{value}</span>
      </div>
      <p className="text-gray-400 text-sm mt-2">{title}</p>
    </div>
  );
};

export default Dashboard;
