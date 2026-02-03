import os
import json
from groq import AsyncGroq

class LLMClient:
    """
    Wrapper for Groq API interactions.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        self.client = AsyncGroq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    async def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """
        Send a chat completion request to Groq.
        """
        try:
            chat = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=temperature
            )
            return chat.choices[0].message.content
        except Exception as e:
            return f"LLM ERROR: {str(e)}"

    async def get_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict:
        """
        Expects a JSON response from the LLM and parses it.
        """
        response = await self.chat(system_prompt, user_prompt + "\n\nRETURN JSON ONLY.", temperature)
        try:
            # Naive cleanup for markdown code blocks if present
            clean_res = response.strip()
            if "```json" in clean_res:
                clean_res = clean_res.split("```json")[1].split("```")[0]
            elif "```" in clean_res:
                clean_res = clean_res.split("```")[1].split("```")[0]
            
            return json.loads(clean_res)
        except json.JSONDecodeError:
            print(f"FAILED TO PARSE JSON: {response}")
            return {}
