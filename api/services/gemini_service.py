from django.conf import settings
from google import genai

class GeminiService:
    def __init__(self, model_name="models/gemini-2.5-flash"):
        genai.Client(api_key=settings.GOOGLE_API_KEY)
        # Access the Gemini API using the genai client library, self.client.models.generate_content, no typing as of this moment from google it seems
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_name = model_name

    def list_supported_models(self):
        return [
            model.name
            for model in self.client.models.list()
            if "generateContent" in getattr(model, "supported_generation_methods", [])
        ]