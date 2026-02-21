"""
AI client utility for Stream Deck automation
Supports OpenAI, XAI, and OpenRouter
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    """Client for various AI APIs"""

    def __init__(self, model: str = 'openai'):
        """
        Initialize AI client

        Args:
            model: Model provider (openai, xai, openrouter)
        """
        self.model = model.lower()
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> str:
        """Get API key for selected model"""
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'xai': 'XAI_API_KEY',
            'openrouter': 'OPENROUTER_API_KEY'
        }

        env_var = key_map.get(self.model)
        if not env_var:
            raise ValueError(f"Unknown model: {self.model}")

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found: {env_var}")

        return api_key

    def query(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Send query to AI model

        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens

        Returns:
            AI response text
        """
        if self.model == 'openai':
            return self._query_openai(prompt, max_tokens)
        elif self.model == 'xai':
            return self._query_xai(prompt, max_tokens)
        elif self.model == 'openrouter':
            return self._query_openrouter(prompt, max_tokens)
        else:
            raise ValueError(f"Unknown model: {self.model}")

    def _query_openai(self, prompt: str, max_tokens: int) -> str:
        """Query OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }

        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _query_xai(self, prompt: str, max_tokens: int) -> str:
        """Query XAI API"""
        url = "https://api.x.ai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }

        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _query_openrouter(self, prompt: str, max_tokens: int) -> str:
        """Query OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "anthropic/claude-3-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }

        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def stream_query(self, prompt: str):
        """
        Stream query response (for future implementation)

        Args:
            prompt: User prompt

        Yields:
            Response chunks
        """
        # Placeholder for streaming implementation
        raise NotImplementedError("Streaming not yet implemented")
