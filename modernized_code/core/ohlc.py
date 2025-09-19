#!/usr/bin/env python3

import numpy as np
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class OHLC:
    """Represents a single Open-High-Low-Close candlestick."""
    
    def __init__(self, open_price: float, high_price: float, low_price: float, close_price: float, 
                 timestamp: int, volume: float = 0.0):
        """Initialize OHLC object.
        
        Args:
            open_price: Opening price
            high_price: Highest price during period
            low_price: Lowest price during period
            close_price: Closing price
            timestamp: Unix timestamp in milliseconds
            volume: Trading volume during period
        """
        self.open = float(open_price)
        self.high = float(high_price)
        self.low = float(low_price)
        self.close = float(close_price)
        self.timestamp = int(timestamp)
        self.volume = float(volume)
    
    @classmethod
    def from_binance_kline(cls, kline_data: List) -> 'OHLC':
        """Create OHLC object from Binance kline data.
        
        Args:
            kline_data: Binance kline data list
            
        Returns:
            OHLC object
        """
        return cls(
            open_price=float(kline_data[1]),
            high_price=float(kline_data[2]),
            low_price=float(kline_data[3]),
            close_price=float(kline_data[4]),
            timestamp=int(kline_data[0]),
            volume=float(kline_data[5])
        )
    
    def to_dict(self) -> Dict[str, Union[float, int]]:
        """Convert OHLC to dictionary.
        
        Returns:
            Dictionary representation of OHLC
        """
        return {
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }
    
    def __str__(self) -> str:
        """String representation of OHLC."""
        return f"OHLC(timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close})"


class OHLCContainer:
    """Container for OHLC data with technical analysis capabilities."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize OHLCContainer.
        
        Args:
            max_size: Maximum number of OHLC objects to store
        """
        self.max_size = max_size
        self.container: List[OHLC] = []
        self.last_rsi: Optional[float] = None
        self.last_moving_average: Optional[float] = None
        self.last_slope: Optional[float] = None
        
    def add(self, ohlc: OHLC) -> None:
        """Add OHLC object to container.
        
        Args:
            ohlc: OHLC object to add
        """
        self.container.append(ohlc)
        
        # Trim container if it exceeds max size
        if len(self.container) > self.max_size:
            self.container = self.container[-self.max_size:]
    
    def clear(self) -> None:
        """Clear all OHLC data."""
        self.container = []
        self.last_rsi = None
        self.last_moving_average = None
        self.last_slope = None
    
    def get_close_prices(self) -> np.ndarray:
        """Get array of close prices.
        
        Returns:
            NumPy array of close prices
        """
        return np.array([ohlc.close for ohlc in self.container])
    
    def get_high_prices(self) -> np.ndarray:
        """Get array of high prices.
        
        Returns:
            NumPy array of high prices
        """
        return np.array([ohlc.high for ohlc in self.container])
    
    def get_low_prices(self) -> np.ndarray:
        """Get array of low prices.
        
        Returns:
            NumPy array of low prices
        """
        return np.array([ohlc.low for ohlc in self.container])
    
    def get_open_prices(self) -> np.ndarray:
        """Get array of open prices.
        
        Returns:
            NumPy array of open prices
        """
        return np.array([ohlc.open for ohlc in self.container])
    
    def get_volumes(self) -> np.ndarray:
        """Get array of volumes.
        
        Returns:
            NumPy array of volumes
        """
        return np.array([ohlc.volume for ohlc in self.container])
    
    def get_timestamps(self) -> np.ndarray:
        """Get array of timestamps.
        
        Returns:
            NumPy array of timestamps
        """
        return np.array([ohlc.timestamp for ohlc in self.container])
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert container to pandas DataFrame.
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.container:
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        data = {
            'timestamp': self.get_timestamps(),
            'open': self.get_open_prices(),
            'high': self.get_high_prices(),
            'low': self.get_low_prices(),
            'close': self.get_close_prices(),
            'volume': self.get_volumes()
        }
        
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def __len__(self) -> int:
        """Get number of OHLC objects in container."""
        return len(self.container)
    
    def __getitem__(self, index: int) -> OHLC:
        """Get OHLC object at index."""
        return self.container[index]
    
    def __iter__(self):
        """Iterate over OHLC objects."""
        return iter(self.container)
    
    def get_latest(self) -> Optional[OHLC]:
        """Get latest OHLC object.
        
        Returns:
            Latest OHLC object or None if container is empty
        """
        if not self.container:
            return None
        return self.container[-1]
    
    def has_enough_data(self, min_data_points: int) -> bool:
        """Check if container has enough data points.
        
        Args:
            min_data_points: Minimum number of data points required
            
        Returns:
            True if container has enough data, False otherwise
        """
        return len(self.container) >= min_data_points
