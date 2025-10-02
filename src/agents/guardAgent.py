import logging
import os 
from pathlib import Path
from src.agents.conversationAgent import ConversationAgent
from src.agents.speechRecognition import listenAudio, speak
from src.agents.faceRecognition import FaceRecognition
import cv2

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
        self.guardRoom()

    def deactivate_guard(self):
        self.guardMode = False
        logger.info("Guard mode deactivated.")
        speak("Guard mode deactivated.")
        
    def addTrustedFace(self, trustedFacesPath):
        self.face_recognition = FaceRecognition()
        self.face_recognition.add_known_face(trustedFacesPath)
        logger.info(f"Trusted face added from {trustedFacesPath}")
        # speak(f"Trusted face added from {trustedFacesPath}")

    def guardRoom(self):
        if not self.guardMode:
            logger.info("Guard mode is not activated.")
            return
        
        logger.info("Guarding the room...")
        speak("Guarding the room.")
        
        while self.guardMode:
            # Here you would integrate with a camera feed to capture images
            # For demonstration, we will assume an image path
            videoCapture = cv2.VideoCapture(0)
            ret, frame = videoCapture.read()
            if not ret:
                logger.warning("Failed to capture image from camera.")
                continue

            recognized_faces = self.face_recognition.recognize_faces(frame)
            if any(recognized_faces):
                logger.info("Known face detected.")
                speak("Known face detected. Access granted.")
                command = listenAudio()
                if command and command in self.config.get("commands", {}).get("deactivationCommand", []):
                    self.deactivate_guard()
                    break
            else:
                logger.warning("Unknown face detected!")
                speak("Warning! Unknown face detected!")
                response = self.level1Response()
                videoCapture = cv2.VideoCapture(0)
                ret, frame = videoCapture.read()
                if not ret:
                    logger.warning("Failed to capture image from camera.")
                    continue
                recognized_faces = self.face_recognition.recognize_faces(frame)
                if any(recognized_faces):
                    logger.info("Known face detected after Level 1 Response.")
                    speak("Known face detected. Access granted.")
                    command = listenAudio()
                    if command and command in self.config.get("commands", {}).get("deactivationCommand", []):
                        self.deactivate_guard()
                        break
                else:
                    logger.error("Intruder detected! Escalating to Level 2 Response.")
                    speak("Intruder detected! Escalating to Level 2 Response.")
                    self.level2Response(response)
                    # Here you could add more actions like sending alerts, etc.
                    videoCapture = cv2.VideoCapture(0)
                    ret, frame = videoCapture.read()
                    if not ret:
                        logger.warning("Failed to capture image from camera.")
                        continue
                    recognized_faces = self.face_recognition.recognize_faces(frame)
                    if any(recognized_faces):
                        logger.info("Known face detected after Level 2 Response.")
                        speak("Known face detected. Access granted.")
                        command = listenAudio()
                        if command and command in self.config.get("commands", {}).get("deactivationCommand", []):
                            self.deactivate_guard()
                            break
                    else:
                        logger.error("Intruder still present after Level 2 Response. Authorities have been contacted.")
                        speak("Intruder still present. Authorities have been contacted.")
                        # Here you could add code to contact authorities
        videoCapture.release()


    def level1Response(self):
        logger.info("Initiating Level 1 Response.")
        speak("Initiating Level 1 Response. Who are you? Please state your purpose.")
        response = listenAudio()
        if response:
            return response
        else:
            return "No response received."
        
    def level2Response(self, intruderResponse):
        logger.info("Initiating Level 2 Response.")
        prompt = f"You are an AI security agent tasked to handle a potential intruder. You asked the intruder to state their purpose. They responded: '{intruderResponse}'. Based on this, give the second level response, asking them to leave immediately and warn them that authorities will be contacted if they do not comply."
        response = self.conversationAgent.generate_response(prompt)
        logger.info(f"Level 2 Response: {response}")
        speak("Initiating Level 2 Response.")
        speak(response)
        
