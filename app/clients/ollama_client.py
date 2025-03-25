"""Client for interacting with Ollama API."""

import aiohttp
import json
from typing import Dict, Any, Optional


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize the Ollama client.

        Args:
            base_url: Base URL for the Ollama API
            model: The model to use for generation
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a response from the model.

        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            The generated text response
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                # Ollama returns a stream of JSON objects, one per line
                full_response = ""
                async for line in response.content:
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                    except json.JSONDecodeError:
                        continue

                return full_response

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_format: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Generate a structured response from the model.

        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt to guide the model
            output_format: Expected output format structure
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            The generated response as a structured dictionary
        """
        format_prompt = ""
        if output_format:
            format_prompt = (
                "\nYour response must be a valid JSON object with the following structure:\n"
                f"{json.dumps(output_format, indent=2)}\n"
                "Ensure your entire response can be parsed as JSON."
            )

        full_prompt = f"{prompt}{format_prompt}"

        response_text = await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Extract JSON from the response
        try:
            # Try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the response
            try:
                # Look for content between triple backticks
                json_match = response_text.split("```json")
                if len(json_match) > 1:
                    json_content = json_match[1].split("```")[0].strip()
                    return json.loads(json_content)

                # Look for content between single backticks
                json_match = response_text.split("`")
                if len(json_match) > 1:
                    for i in range(1, len(json_match), 2):
                        try:
                            return json.loads(json_match[i])
                        except:
                            continue

                # Last resort: try to find anything that looks like JSON
                import re

                json_pattern = r"\{(?:[^{}]|(?R))*\}"
                matches = re.findall(json_pattern, response_text)
                if matches:
                    for match in matches:
                        try:
                            return json.loads(match)
                        except:
                            continue

                # If all else fails, return the raw text
                return {"error": "Could not parse JSON", "raw_response": response_text}
            except Exception as e:
                return {
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": response_text,
                }
