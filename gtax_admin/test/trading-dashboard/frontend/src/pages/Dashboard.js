import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import StockChart from '../components/StockChart';
import PriceTable from '../components/PriceTable';

function Dashboard() {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockPrices, setStockPrices] = useState(null);
  const [loading, setLoading] = useState(true);
  const [priceLoading, setPriceLoading] = useState(false);
  const [chartDays, setChartDays] = useState(30);

  // Fetch dashboard summary
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/summary');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search
  const searchStocks = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await api.get(`/stocks/search?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data || []);
    } catch (error) {
      console.error('Error searching stocks:', error);
      setSearchResults([]);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchStocks(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, searchStocks]);

  // Fetch stock prices
  const fetchStockPrices = async (symbol, days = 30) => {
    setPriceLoading(true);
    try {
      const response = await api.get(`/stocks/${symbol}/prices?days=${days}`);
      setStockPrices(response.data);
    } catch (error) {
      console.error('Error fetching stock prices:', error);
    } finally {
      setPriceLoading(false);
    }
  };

  const handleStockSelect = async (stock) => {
    setSelectedStock(stock);
    setShowSearchResults(false);
    setSearchQuery('');
    await fetchStockPrices(stock.symbol, chartDays);
  };

  const handleChartDaysChange = async (days) => {
    setChartDays(days);
    if (selectedStock) {
      await fetchStockPrices(selectedStock.symbol, days);
    }
  };

  const handleBackToDashboard = () => {
    setSelectedStock(null);
    setStockPrices(null);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatChange = (change, percent) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${formatPrice(change)} (${sign}${percent.toFixed(2)}%)`;
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>📈 TradingHub</h1>
        </div>
        <div className="navbar-user">
          <span>Welcome, {user?.name}</span>
          <button className="btn-logout" onClick={logout}>
            Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Search Bar */}
        <div className="search-container">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="search-input"
              placeholder="Search stocks by symbol or name..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSearchResults(true);
              }}
              onFocus={() => setShowSearchResults(true)}
              onBlur={() => setTimeout(() => setShowSearchResults(false), 200)}
            />
            {showSearchResults && searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((stock) => (
                  <div
                    key={stock.id}
                    className="search-result-item"
                    onClick={() => handleStockSelect(stock)}
                  >
                    <div>
                      <span className="search-result-symbol">{stock.symbol}</span>
                      <span className="search-result-name"> - {stock.name}</span>
                    </div>
                    <span style={{ color: '#8888aa', fontSize: '12px' }}>
                      {stock.exchange}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Stock Detail View */}
        {selectedStock && (
          <>
            <button className="btn-back" onClick={handleBackToDashboard}>
              ← Back to Dashboard
            </button>

            <div className="stock-detail">
              <div className="stock-detail-header">
                <div className="stock-detail-info">
                  <h2>{selectedStock.symbol}</h2>
                  <p>{selectedStock.name}</p>
                  <p style={{ fontSize: '12px', marginTop: '4px' }}>
                    {selectedStock.exchange} • {selectedStock.sector}
                  </p>
                </div>
                {stockPrices && stockPrices.prices && stockPrices.prices.length > 0 && (
                  <div className="stock-detail-price">
                    <div className="current-price">
                      {formatPrice(stockPrices.prices[stockPrices.prices.length - 1].close_price)}
                    </div>
                    {stockPrices.prices.length > 1 && (
                      <div
                        className={`price-change ${
                          stockPrices.prices[stockPrices.prices.length - 1].close_price -
                            stockPrices.prices[stockPrices.prices.length - 2].close_price >=
                          0
                            ? 'positive'
                            : 'negative'
                        }`}
                        style={{
                          color:
                            stockPrices.prices[stockPrices.prices.length - 1].close_price -
                              stockPrices.prices[stockPrices.prices.length - 2].close_price >=
                            0
                              ? '#00ff88'
                              : '#ff4d4d',
                        }}
                      >
                        {formatChange(
                          stockPrices.prices[stockPrices.prices.length - 1].close_price -
                            stockPrices.prices[stockPrices.prices.length - 2].close_price,
                          ((stockPrices.prices[stockPrices.prices.length - 1].close_price -
                            stockPrices.prices[stockPrices.prices.length - 2].close_price) /
                            stockPrices.prices[stockPrices.prices.length - 2].close_price) *
                            100
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Chart Tabs */}
              <div className="chart-tabs">
                <button
                  className={`chart-tab ${chartDays === 1 ? 'active' : ''}`}
                  onClick={() => handleChartDaysChange(1)}
                >
                  1 Day
                </button>
                <button
                  className={`chart-tab ${chartDays === 7 ? 'active' : ''}`}
                  onClick={() => handleChartDaysChange(7)}
                >
                  1 Week
                </button>
                <button
                  className={`chart-tab ${chartDays === 30 ? 'active' : ''}`}
                  onClick={() => handleChartDaysChange(30)}
                >
                  30 Days
                </button>
                <button
                  className={`chart-tab ${chartDays === 60 ? 'active' : ''}`}
                  onClick={() => handleChartDaysChange(60)}
                >
                  60 Days
                </button>
              </div>

              {priceLoading ? (
                <div className="loading-container">
                  <div className="spinner"></div>
                </div>
              ) : (
                <>
                  {/* Price Chart */}
                  <div className="chart-container">
                    {stockPrices && <StockChart priceData={stockPrices} />}
                  </div>

                  {/* Price Table */}
                  <div className="price-table-container">
                    {stockPrices && <PriceTable prices={stockPrices.prices} />}
                  </div>
                </>
              )}
            </div>
          </>
        )}

        {/* Dashboard Grid */}
        {!selectedStock && dashboardData && (
          <div className="dashboard-grid">
            {/* Trending Stocks */}
            <div className="dashboard-card">
              <h2>📊 All Stocks</h2>
              <div className="stock-list">
                {dashboardData.trending_stocks?.map((stock) => (
                  <div
                    key={stock.id}
                    className="stock-item"
                    onClick={() => handleStockSelect(stock)}
                  >
                    <div className="stock-info">
                      <span className="stock-symbol">{stock.symbol}</span>
                      <span className="stock-name">{stock.name}</span>
                    </div>
                    <div className="stock-price-info">
                      <span className="stock-price">{formatPrice(stock.current_price)}</span>
                      <span
                        className={`stock-change ${
                          stock.change_percent >= 0 ? 'positive' : 'negative'
                        }`}
                      >
                        {stock.change_percent >= 0 ? '+' : ''}
                        {stock.change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Gainers */}
            <div className="dashboard-card">
              <h2>🚀 Top Gainers</h2>
              <div className="stock-list">
                {dashboardData.top_gainers?.map((stock) => (
                  <div
                    key={stock.id}
                    className="stock-item"
                    onClick={() => handleStockSelect(stock)}
                  >
                    <div className="stock-info">
                      <span className="stock-symbol">{stock.symbol}</span>
                      <span className="stock-name">{stock.name}</span>
                    </div>
                    <div className="stock-price-info">
                      <span className="stock-price">{formatPrice(stock.current_price)}</span>
                      <span className="stock-change positive">
                        +{stock.change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Losers */}
            <div className="dashboard-card">
              <h2>📉 Top Losers</h2>
              <div className="stock-list">
                {dashboardData.top_losers?.map((stock) => (
                  <div
                    key={stock.id}
                    className="stock-item"
                    onClick={() => handleStockSelect(stock)}
                  >
                    <div className="stock-info">
                      <span className="stock-symbol">{stock.symbol}</span>
                      <span className="stock-name">{stock.name}</span>
                    </div>
                    <div className="stock-price-info">
                      <span className="stock-price">{formatPrice(stock.current_price)}</span>
                      <span className="stock-change negative">
                        {stock.change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
