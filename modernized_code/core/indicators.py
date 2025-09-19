#!/usr/bin/env python3

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Union, Tuple
import logging

from core.ohlc import OHLCContainer

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Technical analysis indicators for trading strategies."""
    
    @staticmethod
    def calculate_sma(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average.
        
        Args:
            prices: Array of price values
            period: Period for moving average calculation
            
        Returns:
            Array of SMA values (with NaN for the first period-1 elements)
        """
        if len(prices) < period:
            return np.array([np.nan] * len(prices))
        
        sma = np.zeros_like(prices) * np.nan
        for i in range(period - 1, len(prices)):
            sma[i] = np.mean(prices[i - period + 1:i + 1])
        
        return sma
    
    @staticmethod
    def calculate_ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average.
        
        Args:
            prices: Array of price values
            period: Period for EMA calculation
            
        Returns:
            Array of EMA values (with NaN for the first period-1 elements)
        """
        if len(prices) < period:
            return np.array([np.nan] * len(prices))
        
        ema = np.zeros_like(prices) * np.nan
        # Start with SMA for the first value
        ema[period - 1] = np.mean(prices[:period])
        
        # Calculate multiplier
        multiplier = 2.0 / (period + 1)
        
        # Calculate EMA for remaining values
        for i in range(period, len(prices)):
            ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Relative Strength Index.
        
        Args:
            prices: Array of price values
            period: Period for RSI calculation
            
        Returns:
            Array of RSI values (with NaN for the first period elements)
        """
        if len(prices) <= period:
            return np.array([np.nan] * len(prices))
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Create arrays for gains and losses
        gains = np.zeros_like(deltas)
        losses = np.zeros_like(deltas)
        
        # Separate gains and losses
        gains[deltas > 0] = deltas[deltas > 0]
        losses[deltas < 0] = -deltas[deltas < 0]
        
        # Prepend a zero to match original prices length
        gains = np.insert(gains, 0, 0)
        losses = np.insert(losses, 0, 0)
        
        # Calculate average gains and losses
        avg_gains = np.zeros_like(prices) * np.nan
        avg_losses = np.zeros_like(prices) * np.nan
        
        # First average is simple average
        avg_gains[period] = np.mean(gains[1:period+1])
        avg_losses[period] = np.mean(losses[1:period+1])
        
        # Calculate subsequent values using smoothing
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (period-1) + gains[i]) / period
            avg_losses[i] = (avg_losses[i-1] * (period-1) + losses[i]) / period
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(prices: np.ndarray, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Moving Average Convergence Divergence.
        
        Args:
            prices: Array of price values
            fast_period: Period for fast EMA
            slow_period: Period for slow EMA
            signal_period: Period for signal line
            
        Returns:
            Tuple of (MACD line, signal line, histogram)
        """
        # Calculate EMAs
        fast_ema = TechnicalIndicators.calculate_ema(prices, fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(prices, slow_period)
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands.
        
        Args:
            prices: Array of price values
            period: Period for moving average
            num_std: Number of standard deviations for bands
            
        Returns:
            Tuple of (upper band, middle band, lower band)
        """
        if len(prices) < period:
            nan_array = np.array([np.nan] * len(prices))
            return nan_array, nan_array, nan_array
        
        # Calculate middle band (SMA)
        middle_band = TechnicalIndicators.calculate_sma(prices, period)
        
        # Calculate standard deviation
        rolling_std = np.zeros_like(prices) * np.nan
        for i in range(period - 1, len(prices)):
            rolling_std[i] = np.std(prices[i - period + 1:i + 1], ddof=1)
        
        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_slope(prices: np.ndarray, period: int = 5) -> np.ndarray:
        """Calculate slope of price trend.
        
        Args:
            prices: Array of price values
            period: Period for slope calculation
            
        Returns:
            Array of slope values
        """
        if len(prices) < period:
            return np.array([np.nan] * len(prices))
        
        slopes = np.zeros_like(prices) * np.nan
        
        for i in range(period - 1, len(prices)):
            # Create x values (0, 1, 2, ..., period-1)
            x = np.arange(period)
            # Get y values (prices)
            y = prices[i - period + 1:i + 1]
            # Calculate slope using polyfit
            slope = np.polyfit(x, y, 1)[0]
            slopes[i] = slope
        
        return slopes
    
    @staticmethod
    def apply_to_container(container: OHLCContainer) -> Dict[str, Any]:
        """Apply technical indicators to OHLC container.
        
        Args:
            container: OHLCContainer with price data
            
        Returns:
            Dictionary with calculated indicators
        """
        if len(container) < 14:  # Minimum data points for indicators
            return {}
        
        close_prices = container.get_close_prices()
        
        # Calculate indicators
        sma_20 = TechnicalIndicators.calculate_sma(close_prices, 20)
        ema_12 = TechnicalIndicators.calculate_ema(close_prices, 12)
        ema_26 = TechnicalIndicators.calculate_ema(close_prices, 26)
        rsi_14 = TechnicalIndicators.calculate_rsi(close_prices, 14)
        macd_line, signal_line, histogram = TechnicalIndicators.calculate_macd(close_prices)
        upper_band, middle_band, lower_band = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        slope_5 = TechnicalIndicators.calculate_slope(close_prices, 5)
        
        # Update container's last values
        container.last_rsi = rsi_14[-1] if not np.isnan(rsi_14[-1]) else None
        container.last_moving_average = sma_20[-1] if not np.isnan(sma_20[-1]) else None
        container.last_slope = slope_5[-1] if not np.isnan(slope_5[-1]) else None
        
        # Return all indicators
        return {
            'sma_20': sma_20,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'rsi_14': rsi_14,
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'upper_band': upper_band,
            'middle_band': middle_band,
            'lower_band': lower_band,
            'slope_5': slope_5
        }
