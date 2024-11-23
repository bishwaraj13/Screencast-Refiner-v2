"""
Service module for handling Gemini AI content generation operations.
Provides functionality to generate content using Google's Gemini AI model.
"""

import os
from typing import Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

def generate_content(prompt: str, 
                     model: str = "gemini-1.5-flash", 
                     generation_config: Dict[str, Any] = None) -> str:
    """
    Generate content using Gemini AI model.
    
    Args:
        prompt (str): Input prompt for content generation
        model (str): Model name to use for content generation
        generation_config (Dict[str, Any]): Configuration for content generation
        
    Returns:
        str: Generated content response
        
    Raises:
        ValueError: If API key is not provided
        RuntimeError: If content generation fails
    """
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        raise ValueError("Gemini API key not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Set default values for generation_config if not provided
    if not generation_config:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 100000,
            "response_mime_type": "application/json",
        }

    print("Generating content using Gemini AI model...")

    model = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
    )

    return model.generate_content(prompt)
