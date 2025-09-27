import logging
from google.generativeai import GenerativeModel
import google.generativeai as genai
from src.utils import load_api_key

logger = logging.getLogger(__name__)

class ConversationAgent:
    def __init__(self, config):
        genai.api_key = load_api_key("googleGemini", config)
        model_name = config.get("model_config", {}).get("model", "gemini-pro")
        self.model = GenerativeModel.get(model_name)

    def generate_response(self, prompt):
        try:
            response = self.model.generate_text(
                model=self.model,
                prompt=prompt,
                max_output_tokens=256,
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                stop_sequences=["\n"]
            )
            logger.debug(f"Generated response: {response.text}")
            return response.text
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "I'm sorry, I couldn't process that."

