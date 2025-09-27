import logging
import os 
from pathlib import Path
from src.agents.conversationAgent import ConversationAgent
from src.agents.speechRecognition import listenAudio, speak

logger = logging.getLogger(__name__)

class GuardAgent:
    def __init__(self, config):
        self.config = config
        # Initialize other components as needed
        self.guardMode = False


    def activate_guard(self):
        self.guardMode = True
        logger.info("Guard mode activated.")
        speak("Guard mode activated.")

    def deactivate_guard(self):
        self.guardMode = False
        logger.info("Guard mode deactivated.")
        speak("Guard mode deactivated.")
        
