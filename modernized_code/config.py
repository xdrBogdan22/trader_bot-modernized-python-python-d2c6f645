#!/usr/bin/env python3

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "api": {
        "binance": {
            "api_key": "",
            "api_secret": "",
            "testnet": True,
        }
    },
    "trading": {
        "default_symbol": "BTCUSDT",
        "default_interval": "1m",
        "default_strategy": "SimpleMovingAverage",
        "initial_balance": 1000.0,
        "fee_rate": 0.001,  # 0.1% trading fee
    },
    "ui": {
        "theme": "dark",
        "chart_update_interval": 1000,  # milliseconds
        "log_max_lines": 1000,
    },
    "backtesting": {
        "default_start_date": "2023-01-01",
        "default_end_date": "2023-01-31",
        "processing_speed": 100,  # ms per candle
    },
    "logging": {
        "level": "INFO",
        "file": "trader_bot.log",
    }
}


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from file and environment variables.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing configuration values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    _deep_update(config, file_config)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load configuration from {config_path}: {e}")
    else:
        logger.warning(f"Configuration file {config_path} not found, using defaults")
    
    # Override with environment variables
    _load_from_env(config)
    
    return config


def _deep_update(target: Dict, source: Dict) -> None:
    """Recursively update a nested dictionary."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value


def _load_from_env(config: Dict) -> None:
    """Override configuration with environment variables."""
    # Binance API credentials
    if os.environ.get('BINANCE_API_KEY'):
        config['api']['binance']['api_key'] = os.environ.get('BINANCE_API_KEY')
    
    if os.environ.get('BINANCE_API_SECRET'):
        config['api']['binance']['api_secret'] = os.environ.get('BINANCE_API_SECRET')
    
    if os.environ.get('BINANCE_TESTNET'):
        config['api']['binance']['testnet'] = os.environ.get('BINANCE_TESTNET').lower() == 'true'
    
    # Trading settings
    if os.environ.get('DEFAULT_SYMBOL'):
        config['trading']['default_symbol'] = os.environ.get('DEFAULT_SYMBOL')
    
    if os.environ.get('INITIAL_BALANCE'):
        try:
            config['trading']['initial_balance'] = float(os.environ.get('INITIAL_BALANCE'))
        except ValueError:
            logger.warning("Invalid INITIAL_BALANCE environment variable")
    
    # Logging settings
    if os.environ.get('LOG_LEVEL'):
        config['logging']['level'] = os.environ.get('LOG_LEVEL')


def get_api_credentials() -> Dict[str, str]:
    """Get Binance API credentials from configuration.
    
    Returns:
        Dict containing API key and secret
    """
    config = load_config('config.yaml')
    return {
        'api_key': config['api']['binance']['api_key'],
        'api_secret': config['api']['binance']['api_secret'],
        'testnet': config['api']['binance']['testnet']
    }


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_path}: {e}")
        return False
