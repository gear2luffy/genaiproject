import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function StockChart({ priceData }) {
  if (!priceData || !priceData.prices || priceData.prices.length === 0) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#8888aa' }}>No price data available</div>;
  }

  const prices = priceData.prices;
  const isPositive = prices.length > 1 && prices[prices.length - 1].close_price >= prices[0].close_price;

  const data = {
    labels: prices.map((p) =>
      new Date(p.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    ),
    datasets: [
      {
        label: 'Close Price',
        data: prices.map((p) => p.close_price),
        borderColor: isPositive ? '#00ff88' : '#ff4d4d',
        backgroundColor: isPositive
          ? 'rgba(0, 255, 136, 0.1)'
          : 'rgba(255, 77, 77, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: prices.length > 15 ? 0 : 4,
        pointHoverRadius: 6,
        pointBackgroundColor: isPositive ? '#00ff88' : '#ff4d4d',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#1a1a2e',
        titleColor: '#ffffff',
        bodyColor: '#aaaacc',
        borderColor: '#3a3a5a',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: function (context) {
            return `$${context.parsed.y.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#8888aa',
          maxTicksLimit: 10,
        },
      },
      y: {
        grid: {
          color: '#2a2a4a',
        },
        ticks: {
          color: '#8888aa',
          callback: function (value) {
            return '$' + value.toFixed(2);
          },
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  return (
    <div style={{ height: '300px' }}>
      <Line data={data} options={options} />
    </div>
  );
}

export default StockChart;
