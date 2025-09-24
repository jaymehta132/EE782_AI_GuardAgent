"""
guard_agent.py
Milestone 1: Activation and Basic Input for Guard Agent.

Listens for a wake phrase (default: "guard my room"), confirms activation,
opens webcam to verify hardware access, manages guard on/off state.

Notes:
- Uses Google Web Speech (SpeechRecognition) by default (high accuracy, needs internet).
- Uses fuzzy matching (rapidfuzz) to accept close variants of the phrase.
- Uses pyttsx3 for offline TTS confirmation.
- Optional: Integrate Vosk offline ASR as fallback (notes below).
"""

import threading
import time
import queue
import sys
import cv2
import speech_recognition as sr
import pyttsx3
from rapidfuzz import fuzz, process

# --- Config ---
WAKE_PHRASES = ["guard my room", "guard the room", "guard my room please"]
DEACTIVATE_PHRASES = ["stop guard", "deactivate guard", "turn off guard", "disarm guard"]
CONFIRM_YES = ["yes", "yeah", "yup", "confirm", "activate"]
FUZZY_THRESHOLD = 78  # tune between 70-90; lower = more permissive
PHRASE_TIME_LIMIT = 8  # seconds for each listen chunk
LANG = "en-IN"  # adjust to accent; "en-US" / "en-GB" / "en-IN" etc.

# --- Helper classes ---
class CameraThread(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.running = True
        self.cap = None

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"[camera] Cannot open camera index {self.camera_index}")
                return
            print("[camera] Camera opened OK.")
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("[camera] Failed to read frame.")
                    break
                # Keep CPU low: don't display unless you want; just sleep a bit
                time.sleep(0.05)
            self.cap.release()
        except Exception as e:
            print("[camera] Exception:", e)

    def stop(self):
        self.running = False

class GuardAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # dynamic energy helps adapt to environment (background noise)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.4

        # TTS engine
        self.tts = pyttsx3.init()
        # optional: tune voice rate/volume
        rate = self.tts.getProperty("rate")
        self.tts.setProperty("rate", int(rate * 0.95))

        self.guard_on = False
        self.camera_thread = CameraThread()
        self.listen_lock = threading.Lock()
        self.stop_event = threading.Event()

    def speak(self, text):
        # synchronous TTS (pyttsx3)
        print("[TTS]", text)
        self.tts.say(text)
        self.tts.runAndWait()

    def fuzzy_match(self, phrase, candidates):
        # returns (best_candidate, score)
        # Use rapidfuzz.process.extractOne for best match
        best = process.extractOne(phrase, candidates, scorer=fuzz.WRatio)
        if best:
            return best[0], best[1]
        return None, 0

    def recognize_audio(self, audio):
        """
        Try Google Web Speech first (good accuracy). On errors, return None
        (optionally you can integrate Vosk for offline fallback).
        """
        try:
            text = self.recognizer.recognize_google(audio, language=LANG)
            print("[ASR] Google recognized:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("[ASR] Google could not understand audio.")
            return None
        except sr.RequestError as e:
            print("[ASR] Google request failed:", e)
            return None
        except Exception as e:
            print("[ASR] ASR exception:", e)
            return None

    def listen_once(self, timeout=None):
        """
        Listen once from the mic and return recognized text (lowercased) or None.
        """
        with self.listen_lock:
            with sr.Microphone() as source:
                # Adjust for ambient noise briefly to improve recognition
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                except Exception:
                    pass
                print("[listen] Listening...")
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=PHRASE_TIME_LIMIT)
                except sr.WaitTimeoutError:
                    print("[listen] Wait timeout; no speech.")
                    return None
            return self.recognize_audio(audio)

    def confirm_with_user(self, prompt="Do you want to activate guard mode? Say 'yes' to confirm."):
        # Speak prompt and listen for confirmation (simple)
        self.speak(prompt)
        text = self.listen_once(timeout=3)
        if not text:
            return False
        candidate, score = self.fuzzy_match(text, CONFIRM_YES)
        print(f"[confirm] heard='{text}' best='{candidate}' score={score}")
        return score >= 70

    def handle_candidate_phrase(self, text):
        """
        Returns True if we toggled guard state.
        """
        if not text:
            return False

        # Check for activation
        cand_act, score_act = self.fuzzy_match(text, WAKE_PHRASES)
        cand_deact, score_deact = self.fuzzy_match(text, DEACTIVATE_PHRASES)
        print(f"[match] act_best='{cand_act}' ({score_act}), deact_best='{cand_deact}' ({score_deact})")

        if score_act >= FUZZY_THRESHOLD:
            # Ask confirmation to reduce false positives (improves real-world accuracy)
            if self.confirm_with_user("I heard activation. Confirm activation by saying 'yes'."):
                self.activate_guard()
                return True
            else:
                self.speak("Activation canceled.")
                return False

        if score_deact >= FUZZY_THRESHOLD:
            if self.confirm_with_user("I heard request to stop guard. Say 'yes' to confirm."):
                self.deactivate_guard()
                return True
            else:
                self.speak("Deactivation canceled.")
                return False

        return False

    def activate_guard(self):
        if self.guard_on:
            self.speak("Guard mode is already active.")
            return
        # start camera thread if not already started
        if not self.camera_thread.is_alive():
            self.camera_thread = CameraThread()
            self.camera_thread.start()
            time.sleep(0.5)
        self.guard_on = True
        self.speak("Guard mode activated. I will monitor the room.")
        print("[state] GUARD ON")

    def deactivate_guard(self):
        if not self.guard_on:
            self.speak("Guard mode is already off.")
            return
        self.guard_on = False
        try:
            self.camera_thread.stop()
        except Exception:
            pass
        self.speak("Guard mode deactivated.")
        print("[state] GUARD OFF")

    def run(self):
        self.speak("Guard agent started. Say 'guard my room' to activate.")
        # main loop
        try:
            while not self.stop_event.is_set():
                text = self.listen_once(timeout=6)
                if text:
                    toggled = self.handle_candidate_phrase(text)
                    # if toggled - we already confirmed etc. continue listening
                # small sleep to avoid tight loop
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Stopping by KeyboardInterrupt.")
        finally:
            self.stop()

    def stop(self):
        self.stop_event.set()
        try:
            self.camera_thread.stop()
        except Exception:
            pass
        self.speak("Guard agent stopped.")
        print("Agent stopped.")

# --- Entry point ---
if __name__ == "__main__":
    agent = GuardAgent()
    agent.run()
