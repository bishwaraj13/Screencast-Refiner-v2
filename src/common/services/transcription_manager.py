import os
import asyncio
from dotenv import load_dotenv

from rev_ai import apiclient
from rev_ai.models import JobStatus

async def _process_transcription(audio_file: str) -> dict:
    """
    Process audio file transcription using Rev AI service.

    Args:
        audio_file (str): Path to the audio file

    Returns:
        dict: Transcription result

    Raises:
        ValueError: If Rev AI token is missing or transcription fails
    """
    # Load environment variables
    load_dotenv()

    # Get Rev AI access token
    rev_access_token = os.getenv('REV_ACCESS_TOKEN')
    if not rev_access_token:
        raise ValueError("REV_ACCESS_TOKEN not found in environment variables")

    # Initialize Rev AI client
    client = apiclient.RevAiAPIClient(rev_access_token)

    try:
        print("Submitting audio file for transcription...")
        job = client.submit_job_local_file(audio_file)
        print(f"Transcription job submitted. Job ID: {job.id}")

        # Wait for job completion
        while True:
            job_details = client.get_job_details(job.id)
            print(f"Job status: {job_details.status}")
            
            if job_details.status == JobStatus.TRANSCRIBED:
                break
            elif job_details.status == JobStatus.FAILED:
                raise ValueError(f"Transcription job failed: {job_details.failure_detail}")
            
            await asyncio.sleep(10)  # Wait for 10 seconds before checking again

        print("Transcription completed. Fetching results...")
        transcript = client.get_transcript_json(job.id)
        
        return transcript

    except Exception as e:
        raise ValueError(f"Transcription processing failed: {str(e)}") from e
    