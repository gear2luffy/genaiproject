import React from 'react';

function PriceTable({ prices }) {
  if (!prices || prices.length === 0) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#8888aa' }}>No price data available</div>;
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(2) + 'M';
    }
    if (volume >= 1000) {
      return (volume / 1000).toFixed(2) + 'K';
    }
    return volume.toString();
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Show prices in reverse chronological order (most recent first)
  const sortedPrices = [...prices].reverse();

  return (
    <div style={{ marginTop: '24px' }}>
      <h3 style={{ color: '#aaaacc', marginBottom: '16px', fontSize: '16px' }}>
        📋 Historical Prices
      </h3>
      <table className="price-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Volume</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {sortedPrices.map((price, index) => {
            const prevPrice = sortedPrices[index + 1];
            const change = prevPrice
              ? ((price.close_price - prevPrice.close_price) / prevPrice.close_price) * 100
              : 0;

            return (
              <tr key={price.id || index}>
                <td>{formatDate(price.date)}</td>
                <td>{formatPrice(price.open_price)}</td>
                <td style={{ color: '#00ff88' }}>{formatPrice(price.high_price)}</td>
                <td style={{ color: '#ff4d4d' }}>{formatPrice(price.low_price)}</td>
                <td style={{ fontWeight: '600' }}>{formatPrice(price.close_price)}</td>
                <td>{formatVolume(price.volume)}</td>
                <td
                  style={{
                    color: change >= 0 ? '#00ff88' : '#ff4d4d',
                    fontWeight: '500',
                  }}
                >
                  {change >= 0 ? '+' : ''}
                  {change.toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default PriceTable;
