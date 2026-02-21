#!/usr/bin/env python3
"""
Script Name: ai_query.py
Purpose: Send query to AI models (OpenAI, XAI, OpenRouter)
Author: Rifat Erdem Sahin
Description: Reads prompt from clipboard and sends to selected AI model
"""

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.ai_client import AIClient
from utils.clipboard_manager import get_clipboard, set_clipboard
from utils.notification import show_notification

logger = setup_logger('ai_query')

def main():
    """Query AI model with clipboard content"""
    try:
        # Get model from command line arg or default to OpenAI
        model = sys.argv[1] if len(sys.argv) > 1 else 'openai'
        logger.info(f"Querying AI model: {model}")

        # Get prompt from clipboard
        prompt = get_clipboard()
        if not prompt or not prompt.strip():
            show_notification("AI Query Error", "Clipboard is empty")
            logger.warning("No prompt found in clipboard")
            return 1

        # Initialize AI client
        ai_client = AIClient(model=model)

        # Send query
        show_notification("AI Query", f"Sending to {model}...")
        response = ai_client.query(prompt)

        # Copy response to clipboard
        set_clipboard(response)
        show_notification("AI Response", f"Response copied to clipboard\nModel: {model}")
        logger.info(f"AI query successful: {len(response)} chars returned")

        return 0

    except Exception as e:
        logger.error(f"AI query failed: {e}", exc_info=True)
        show_notification("AI Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
