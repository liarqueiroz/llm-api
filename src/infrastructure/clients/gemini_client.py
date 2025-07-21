import logging
from google import genai
from src.domain.clients.llm_client import LLMClient, LLMGenerationError


logger = logging.getLogger(__name__)

class GeminiClient(LLMClient):
    def __init__(self, genai_client=None):
        self.client = genai_client if genai_client is not None else genai.Client()
        self.model_name = "gemini-2.5-flash"
    
    def generate_text(self, prompt, config = None):
        try:
            logger.info(f"Generating response using model: {self.model_name}")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            logger.info("LLM response generated successfully.")
            return response.text
    
        except Exception as e:
            logger.error("An unexpected error occurred during LLM generation.")
            raise LLMGenerationError(f"An unexpected error occurred during LLM response generation: {e}") from e
    
    def get_model_name(self) -> str:
        """
        Returns the name of the LLM model being used.
        """
        return self.model_name
