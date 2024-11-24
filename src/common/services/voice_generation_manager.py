import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

async def generate_speech(text: str,
                          output_path: Path,
                          voice: str = "alloy"
                          ) -> str:
    """
    Generate audio from text using OpenAI's Text-to-Speech API.

    Args:
        text (str): Text content to convert to speech
        output_path (Path): Path where the audio file should be saved
        voice (str): Voice model to use for TTS

    Returns:
        str: Path to the generated audio file

    Raises:
        RuntimeError: If audio generation fails
    """
    # Load environment variables
    load_dotenv()
    open_ai_key = os.getenv('OPEN_AI_KEY')
    organization_id = os.getenv('OPENAI_ORGANIZATION_ID')

    if not open_ai_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    if not organization_id:
        raise ValueError("OpenAI organization ID not found in environment variables")

    # Initialize OpenAI client
    client = OpenAI(
        api_key=open_ai_key,
        organization=organization_id
    )

    try:
        # Generate the audio using OpenAI's TTS
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        # Save the audio file
        response.stream_to_file(str(output_path))
        return str(output_path)

    except Exception as e:
        raise RuntimeError(f"Failed to generate audio: {str(e)}") from e
