import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.debug(f"Configuration loaded from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def setup_logging(log_dir: str = "logs", logLevel: int = logging.INFO) -> None:
    """Set up logging to a file with a timestamp."""
    logPath = Path(log_dir)
    logPath.mkdir(parents=True, exist_ok=True)
    log_filename = datetime.now().strftime("log_%Y%m%d_%H%M%S.txt")
    logFile = logPath / log_filename
    logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logger = logging.getLogger()
    logger.setLevel(logLevel)

    if logger.hasHandlers():
        logger.handlers.clear()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormat)
    logger.addHandler(consoleHandler)

    fileHandler = logging.FileHandler(logFile)
    fileHandler.setFormatter(logFormat)
    logger.addHandler(fileHandler)

    logger.info(f"Logging initialized. Log file: {logFile}")

def load_api_key(service_name: str, config: Dict[str, Any]) -> str:
    """Load API key for a given service from the configuration."""
    try:
        api_keys = config.get("model_config", {})
        api_key = api_keys.get(service_name)
        if not api_key:
            raise ValueError(f"API key for {service_name} not found in configuration.")
        logger.debug(f"API key for {service_name} loaded successfully.")
        return api_key
    except Exception as e:
        logger.error(f"Failed to load API key for {service_name}: {e}")
        raise 