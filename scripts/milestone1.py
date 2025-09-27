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
    # Example usage of listenAudio
    while True:
        text = listenAudio()
        if text:
            logger.info(f"Recognized speech: {text}")
            if text in config.get("commands", {}).get("activationCommand", []):
                logger.info("Activating guard mode.")
                speak("Activating guard mode.")
                agent.activate_guard()
            elif text in config.get("commands", {}).get("deactivationCommand", []):
                logger.info("Deactivating guard mode.")
                speak("Deactivating guard mode.")
                agent.deactivate_guard()
            elif text in config.get("commands", {}).get("shutdownCommand", []):
                logger.info("Shutting down the system.")
                speak("Shutting down. Goodbye!")
                break
            else:
                speak("Command not recognized. Please try again.")
        else:
            logger.info("No speech recognized.")

if __name__ == "__main__":
    main()