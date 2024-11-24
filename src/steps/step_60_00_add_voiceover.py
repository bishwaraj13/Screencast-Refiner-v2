"""
This file contains the implementation for adding voiceover audio to video clips using moviepy and updating scene records.
"""
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..common.decorators.step_tracker import track_step
from ..common.services.media_manager import add_audio_to_video

@track_step
async def step_60_00_add_voiceover(video_id: str, db: AsyncIOMotorDatabase) -> str:
    """
    Add voiceover audio to video clips using moviepy and update scene records.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Returns:
        str: Video ID of the processed document

    Raises:
        ValueError: If scenes not found or audio files are inaccessible
        RuntimeError: If voiceover addition process fails
    """
    try:
        # Fetch all scenes for the video
        scenes = await db.scenes.find({"video_id": ObjectId(video_id)}).to_list(length=None)

        if not scenes:
            raise ValueError(f"No scenes found for video ID: {video_id}")

        # Process each scene and generate audio
        print("[INFO] Generating audio files...")
        for scene in scenes:
            scene_id = scene['_id']
            audio_file_path = scene.get('audio_file_path')

            if not audio_file_path:
                print(f"[WARNING] No audio file found for scene {scene_id}")
                continue

            # Add voiceover to video clip
            print(f"[INFO] Adding voiceover to scene {scene_id}")
            video_file_path = scene.get('clip_file_path')

            if not video_file_path:
                print(f"[WARNING] No video file found for scene {scene_id}")
                continue

            output_file_path = video_file_path.replace(".mp4", "_voiceover.mp4")

            # Add voiceover to video clip
            add_audio_to_video(video_file_path, audio_file_path, output_file_path)

            # Update scene record with voiceover file path
            await db.scenes.update_one(
                {"_id": scene_id},
                {"$set": {"clip_with_voiceover": output_file_path}}
            )

            print(f"[INFO] Voiceover added to scene {scene_id}")

    except Exception as e:
        raise RuntimeError(f"Failed to add voiceover: {str(e)}") from e
