"""
Learning Model Module.

ML-based model that learns from historical data and past signals
to improve entry timing and exit strategy.
"""
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from loguru import logger

from app.core.config import settings
from app.services.data.data_fetcher import data_fetcher
from app.services.data.technical_indicators import TechnicalIndicators


class BacktestEngine:
    """
    Backtesting engine for validating trading strategies.
    """
    
    def __init__(
        self,
        initial_capital: float = None,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005   # 0.05%
    ):
        self.initial_capital = initial_capital or settings.BACKTEST_INITIAL_CAPITAL
        self.commission = commission
        self.slippage = slippage
    
    async def run_backtest(
        self,
        symbols: List[str],
        start_date: str = None,
        end_date: str = None,
        strategy_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.
        
        Args:
            symbols: List of symbols to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_params: Strategy configuration
        
        Returns:
            Backtest results with metrics
        """
        start_date = start_date or settings.BACKTEST_START_DATE
        end_date = end_date or settings.BACKTEST_END_DATE
        strategy_params = strategy_params or {}
        
        logger.info(f"Running backtest from {start_date} to {end_date}")
        
        # Initialize tracking
        capital = self.initial_capital
        trades = []
        equity_curve = [{'date': start_date, 'equity': capital}]
        positions = {}
        
        for symbol in symbols:
            # Fetch historical data
            df = await data_fetcher.get_stock_data(symbol, period="2y", interval="1d")
            
            if df is None or df.empty:
                continue
            
            # Filter by date range
            df = df[start_date:end_date]
            
            if len(df) < 50:
                continue
            
            # Calculate indicators
            df = TechnicalIndicators.calculate_all(df)
            
            # Generate signals for each bar
            for i in range(50, len(df)):
                bar = df.iloc[i]
                prev_bars = df.iloc[:i+1]
                
                # Get technical score
                tech_result = TechnicalIndicators.get_technical_score(prev_bars)
                signal_score = tech_result['score']
                
                current_price = bar['close']
                date = str(bar.name)
                
                # Simple strategy: Buy if score > 0.3, Sell if score < -0.3
                threshold = strategy_params.get('threshold', 0.3)
                position_size = strategy_params.get('position_size', 0.1)
                
                if symbol not in positions:
                    # Look for entry
                    if signal_score > threshold:
                        # Buy signal
                        trade_value = capital * position_size
                        shares = trade_value / current_price
                        cost = trade_value * (1 + self.commission + self.slippage)
                        
                        if cost <= capital:
                            capital -= cost
                            positions[symbol] = {
                                'shares': shares,
                                'entry_price': current_price,
                                'entry_date': date
                            }
                            trades.append({
                                'symbol': symbol,
                                'side': 'BUY',
                                'price': current_price,
                                'shares': shares,
                                'date': date,
                                'signal_score': signal_score
                            })
                else:
                    # Look for exit
                    position = positions[symbol]
                    entry_price = position['entry_price']
                    
                    # Exit conditions
                    stop_loss = entry_price * (1 - settings.DEFAULT_STOP_LOSS)
                    take_profit = entry_price * (1 + settings.DEFAULT_TAKE_PROFIT)
                    
                    should_exit = (
                        signal_score < -threshold or
                        current_price <= stop_loss or
                        current_price >= take_profit
                    )
                    
                    if should_exit:
                        shares = position['shares']
                        sale_value = shares * current_price * (1 - self.commission - self.slippage)
                        capital += sale_value
                        
                        pnl = sale_value - (shares * entry_price)
                        pnl_pct = (current_price - entry_price) / entry_price
                        
                        trades.append({
                            'symbol': symbol,
                            'side': 'SELL',
                            'price': current_price,
                            'shares': shares,
                            'date': date,
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'signal_score': signal_score
                        })
                        
                        del positions[symbol]
                
                # Update equity curve
                portfolio_value = capital
                for sym, pos in positions.items():
                    if sym == symbol:
                        portfolio_value += pos['shares'] * current_price
                
                equity_curve.append({
                    'date': date,
                    'equity': portfolio_value
                })
        
        # Close remaining positions
        final_equity = capital
        for symbol, position in positions.items():
            # Use last known price
            final_equity += position['shares'] * position['entry_price']
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, equity_curve, final_equity)
        
        return {
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_capital': round(final_equity, 2),
            'total_return': round((final_equity - self.initial_capital) / self.initial_capital * 100, 2),
            'total_trades': len(trades),
            'strategy_params': strategy_params,
            'metrics': metrics,
            'equity_curve': equity_curve[-100:],  # Last 100 points
            'trades': trades
        }
    
    def _calculate_metrics(
        self,
        trades: List[Dict],
        equity_curve: List[Dict],
        final_equity: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics."""
        
        if not trades:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_trade_pnl': 0
            }
        
        # Filter completed trades (with pnl)
        completed = [t for t in trades if 'pnl' in t]
        
        if not completed:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_trade_pnl': 0
            }
        
        pnls = [t['pnl'] for t in completed]
        pnl_pcts = [t['pnl_pct'] for t in completed]
        
        # Win rate
        winners = [p for p in pnls if p > 0]
        losers = [p for p in pnls if p < 0]
        win_rate = len(winners) / len(completed) if completed else 0
        
        # Profit factor
        gross_profit = sum(winners) if winners else 0
        gross_loss = abs(sum(losers)) if losers else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Sharpe ratio (simplified, annualized)
        returns = np.array(pnl_pcts)
        if len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = np.std(downside_returns)
            sortino = np.mean(returns) / downside_std * np.sqrt(252) if downside_std > 0 else 0
        else:
            sortino = sharpe  # No downside, use Sharpe
        
        # Max drawdown
        equity_values = [e['equity'] for e in equity_curve]
        peak = equity_values[0]
        max_dd = 0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        
        return {
            'sharpe_ratio': round(sharpe, 3),
            'sortino_ratio': round(sortino, 3),
            'max_drawdown': round(max_dd * 100, 2),
            'win_rate': round(win_rate * 100, 2),
            'profit_factor': round(profit_factor, 3),
            'avg_trade_pnl': round(np.mean(pnls), 2),
            'total_pnl': round(sum(pnls), 2),
            'winning_trades': len(winners),
            'losing_trades': len(losers)
        }


class MLPredictor:
    """
    Machine Learning predictor for trading signals.
    
    Uses historical data to train models that predict:
    - Price direction
    - Optimal entry points
    - Exit timing
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.models: Dict[str, Any] = {}
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for ML model.
        
        Features include:
        - Technical indicators
        - Price ratios
        - Volume patterns
        """
        if len(df) < 60:
            return np.array([]), np.array([])
        
        # Calculate all indicators
        df = TechnicalIndicators.calculate_all(df)
        
        # Create features
        features = []
        labels = []
        
        for i in range(50, len(df) - 5):  # Need 5 days forward for label
            row = df.iloc[i]
            
            # Feature vector
            feature = [
                row.get('rsi', 50) / 100,
                row.get('macd', 0),
                row.get('macd_signal', 0),
                (row['close'] - row.get('sma_20', row['close'])) / row['close'],
                (row.get('sma_20', 0) - row.get('sma_50', 0)) / row.get('sma_50', 1) if row.get('sma_50', 0) != 0 else 0,
                row.get('adx', 25) / 100,
                row.get('stoch_k', 50) / 100,
                row.get('volume_ratio', 1) if pd.notna(row.get('volume_ratio')) else 1,
                (row['high'] - row['low']) / row['close'],  # Volatility
                (row['close'] - row['open']) / row['open']  # Candle direction
            ]
            
            # Replace NaN/Inf
            feature = [0 if (pd.isna(f) or np.isinf(f)) else f for f in feature]
            features.append(feature)
            
            # Label: Price change in 5 days
            future_price = df.iloc[i + 5]['close']
            current_price = row['close']
            change = (future_price - current_price) / current_price
            
            # Classify: 1 = buy (>2%), 0 = hold, -1 = sell (<-2%)
            if change > 0.02:
                label = 1
            elif change < -0.02:
                label = -1
            else:
                label = 0
            
            labels.append(label)
        
        return np.array(features), np.array(labels)
    
    async def train_model(
        self, 
        symbols: List[str],
        model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Train ML model on historical data.
        
        Args:
            symbols: Symbols to use for training
            model_type: Type of model (random_forest, gradient_boosting, etc.)
        
        Returns:
            Training results and metrics
        """
        logger.info(f"Training {model_type} model on {len(symbols)} symbols")
        
        all_features = []
        all_labels = []
        
        for symbol in symbols:
            df = await data_fetcher.get_stock_data(symbol, period="2y", interval="1d")
            
            if df is None or df.empty:
                continue
            
            features, labels = self.prepare_features(df)
            
            if len(features) > 0:
                all_features.extend(features)
                all_labels.extend(labels)
        
        if len(all_features) < 100:
            return {
                'status': 'error',
                'message': 'Insufficient training data'
            }
        
        X = np.array(all_features)
        y = np.array(all_labels)
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.metrics import accuracy_score, classification_report
            
            if model_type == "random_forest":
                model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            else:
                model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            model_path = self.model_dir / f"{model_type}_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            self.models[model_type] = model
            
            return {
                'status': 'success',
                'model_type': model_type,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'accuracy': round(accuracy * 100, 2),
                'model_path': str(model_path),
                'feature_importance': dict(zip(
                    ['rsi', 'macd', 'macd_signal', 'price_sma_ratio', 'sma_cross', 
                     'adx', 'stoch_k', 'volume_ratio', 'volatility', 'candle_dir'],
                    model.feature_importances_.tolist()
                ))
            }
            
        except ImportError:
            return {
                'status': 'error',
                'message': 'scikit-learn not installed'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def load_model(self, model_type: str = "random_forest") -> bool:
        """Load a trained model from disk."""
        model_path = self.model_dir / f"{model_type}_model.pkl"
        
        if not model_path.exists():
            return False
        
        try:
            with open(model_path, 'rb') as f:
                self.models[model_type] = pickle.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    async def predict(
        self, 
        symbol: str,
        model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Make prediction for a symbol using trained model.
        """
        if model_type not in self.models:
            if not self.load_model(model_type):
                return {
                    'status': 'error',
                    'message': f'Model {model_type} not found'
                }
        
        df = await data_fetcher.get_stock_data(symbol, period="3mo", interval="1d")
        
        if df is None or len(df) < 60:
            return {
                'status': 'error',
                'message': 'Insufficient data'
            }
        
        features, _ = self.prepare_features(df)
        
        if len(features) == 0:
            return {
                'status': 'error',
                'message': 'Could not prepare features'
            }
        
        # Use latest features for prediction
        latest_features = features[-1].reshape(1, -1)
        
        model = self.models[model_type]
        prediction = model.predict(latest_features)[0]
        probabilities = model.predict_proba(latest_features)[0]
        
        signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
        classes = model.classes_
        
        prob_dict = {signal_map.get(c, str(c)): round(p, 3) for c, p in zip(classes, probabilities)}
        
        return {
            'status': 'success',
            'symbol': symbol,
            'prediction': signal_map.get(prediction, 'HOLD'),
            'probabilities': prob_dict,
            'confidence': round(max(probabilities), 3),
            'model_type': model_type,
            'timestamp': datetime.now().isoformat()
        }


# Singleton instances
backtest_engine = BacktestEngine()
ml_predictor = MLPredictor()
