# llm_interface.py
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

class LLMInterface:
    def __init__(self):
        # Instantiate an OpenAI client with the API key
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS

    def get_response(self, prompt):
        try:
            # Use the instantiated client to create a chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful jobs-to-be-done job mapping research expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Updated way to access the content of the response
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return ""
