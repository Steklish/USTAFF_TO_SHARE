import time
from vertexai.language_models import TextEmbeddingModel
from .env import *
api_keys = GEMINI_API_KEY_ARRAY
_current_key_index = 0

def get_next_api_key():
    global _current_key_index
    key = api_keys[_current_key_index]
    _current_key_index = (_current_key_index + 1) % len(api_keys)
    return key


from google import genai
from typing import List

class EmbeddingClient:
    def __init__(self):
        """
        Initialize Gemini Embedding API client.
        """
        self.model = "text-embedding-004"
        self.client = genai.Client(api_key=get_next_api_key())
    def get_text_embedding(self, texts: List[str]):
        """
        Get embeddings for a list of texts using Gemini Embedding API.
        
        Args:
            texts: List of input strings to embed
            
        Returns:
            List of embedding vectors (768-dimensional by default)
        """
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts
        )
        time.sleep(0.25)
        return [embedding.values for embedding in response.embeddings]

if __name__ == "__main__":
    a = EmbeddingClient()
    print(a.get_text_embedding(["ads"])[0])
    