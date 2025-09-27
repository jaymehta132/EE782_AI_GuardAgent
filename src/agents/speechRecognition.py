import speech_recognition as sr
import logging
import os
import pyttsx3
from rapidfuzz import fuzz, process

tts = pyttsx3.init()
rate = tts.getProperty("rate")
tts.setProperty("rate", int(rate * 0.95))

logger = logging.getLogger(__name__)

def listenAudio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        logger.info("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        logger.info(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        logger.warning("Sorry, I did not understand that.")
        return None
    except sr.RequestError as e:
        logger.error(f"Could not request results; {e}")
        return None
    

def speak(text):
    try:
        tts.say(text)
        tts.runAndWait()
    except ImportError:
        logger.error("pyttsx3 is not installed. Please install it to use text-to-speech functionality.")
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
    
