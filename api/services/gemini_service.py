from django.conf import settings
from google import genai

class GeminiService:
    def __init__(self, model_name="models/gemini-2.5-flash"):
        self.client = genai.Client(location="europe-west4", transport="grpc")
        self.model_name = model_name

    def list_supported_models(self):
        return [
            model.name
            for model in self.client.models.list()
            if "generateContent" in getattr(model, "supported_generation_methods", [])
        ]