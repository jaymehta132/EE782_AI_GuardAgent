import logging
import os 
from pathlib import Path
from src.agents.conversationAgent import ConversationAgent
from src.agents.speechRecognition import listenAudio, speak
from src.agents.faceRecognition import FaceRecognition

logger = logging.getLogger(__name__)

class GuardAgent:
    def __init__(self, config):
        self.config = config
        # Initialize other components as needed
        self.guardMode = False
        self.addTrustedFace(self.config.get("paths", {}).get("trustedFaces", "data/trusted_faces"))
        self.conversationAgent = ConversationAgent(self.config)

    def activate_guard(self):
        self.guardMode = True
        logger.info("Guard mode activated.")
        speak("Guard mode activated.")

    def deactivate_guard(self):
        self.guardMode = False
        logger.info("Guard mode deactivated.")
        speak("Guard mode deactivated.")
        
    def addTrustedFace(self, trustedFacesPath):
        self.face_recognition = FaceRecognition()
        self.face_recognition.add_known_face(trustedFacesPath)
        logger.info(f"Trusted face added from {trustedFacesPath}")
        # speak(f"Trusted face added from {trustedFacesPath}")

