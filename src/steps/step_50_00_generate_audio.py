"""
This file contains the implementation for generating audio files for each scene's narration using voice_generation_manager
"""
import os
from pathlib import Path
from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..common.decorators.step_tracker import track_step
from ..common.services.voice_generation_manager import generate_speech

@track_step
async def step_50_00_generate_audio(video_id: str,
                                    db: AsyncIOMotorDatabase,
                                    voice: str = "alloy") -> str:
    """
    Generate audio files for each scene's narration using OpenAI's Text-to-Speech API.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection
        voice (str): Voice model to use for TTS (default: "alloy")

    Returns:
        str: Video ID of the processed document

    Raises:
        ValueError: If scenes not found or configuration is invalid
        RuntimeError: If audio generation process fails
    """
    try:
        # Load environment variables
        load_dotenv()

        # Setup generated audio directory
        base_dir = Path(os.getenv('BASE_DIR', ''))
        audio_dir = base_dir / f"{video_id}/gen_audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Fetch all scenes for the video
        scenes = await db.scenes.find({"video_id": ObjectId(video_id)}).to_list(length=None)

        if not scenes:
            raise ValueError(f"No scenes found for video ID: {video_id}")

        # Process each scene and generate audio
        print("[INFO] Generating audio files...")
        for scene in scenes:
            print(f"[INFO] Generating audio for scene {scene['_id']}")
            scene_id = scene['_id']
            polished_narration = scene.get('polished_narration')
            
            if not polished_narration:
                print(f"[WARNING] No narration found for scene {scene_id}")
                continue

            # Generate audio file path
            audio_filename = f"scene_{scene_id}.mp3"
            audio_file_path = os.path.join(audio_dir, audio_filename)

            await generate_speech(
                polished_narration,
                audio_file_path,
                voice
            )

            # Update scene record with audio file path
            await db.scenes.update_one(
                {"_id": ObjectId(scene_id)},
                {"$set": {"audio_file_path": str(audio_file_path)}}
            )

    except Exception as e:
        raise RuntimeError(f"Audio generation process failed: {str(e)}") from e