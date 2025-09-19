#!/usr/bin/env python3

import sys
import logging
import argparse
from PyQt5.QtWidgets import QApplication

from ui.main_window import TradingBotMainWindow
from config import load_config
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Trader_Bot - Cryptocurrency Trading Bot')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level')
    parser.add_argument('--no-gui', action='store_true',
                        help='Run in headless mode (no GUI)')
    return parser.parse_args()


def run_gui_application(config):
    """Initialize and run the GUI application."""
    app = QApplication(sys.argv)
    main_window = TradingBotMainWindow(config)
    main_window.show()
    return app.exec_()


def run_headless_application(config):
    """Run the application in headless mode."""
    from core.headless_runner import HeadlessRunner
    
    runner = HeadlessRunner(config)
    return runner.run()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Setup logging
    setup_logger(args.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Trader_Bot application")
    
    # Load configuration
    try:
        config = load_config(args.config)
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    # Run application in appropriate mode
    try:
        if args.no_gui:
            logger.info("Running in headless mode")
            return run_headless_application(config)
        else:
            logger.info("Starting GUI application")
            return run_gui_application(config)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
