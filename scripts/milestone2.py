import logging
import os

from pathlib import Path
from src.utils import load_config, setup_logging
from src.agents.speechRecognition import listenAudio, speak
from src.agents.conversationAgent import ConversationAgent
from src.agents.guardAgent import GuardAgent

def main():
    # Load configuration
    config = load_config("config.yaml")

    # Setup logging
    logDir = config.get("paths", {}).get("logDir", "logs")
    setup_logging(log_dir=logDir, logLevel=logging.INFO)
    logger = logging.getLogger(__name__)

    # Ensure trusted faces directory exists
    trustedFacesDir = config.get("paths", {}).get("trustedFaces", "data/trustedFaces")
    Path(trustedFacesDir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Trusted faces directory: {trustedFacesDir}")

    # # Initialize and run the guard agent
    # from guardAgent import GuardAgent  # Import here to avoid circular imports
    agent = GuardAgent(config)
    # agent.run()
    speak("Guard agent initialized.")
    