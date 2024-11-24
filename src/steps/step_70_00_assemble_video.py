import os
from pathlib import Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..common.decorators.step_tracker import track_step
from ..common.services.media_manager import concatenate_video_clips

@track_step
async def step_70_00_assemble_video(video_id: str, db: AsyncIOMotorDatabase) -> str:
    """
    Assemble video clips with voiceover into a single video file using moviepy and update video record.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Returns:
        str: Video ID of the processed document

    Raises:
        ValueError: If video clips not found or video files are inaccessible
        RuntimeError: If video assembly process fails
    """
    try:
        # Fetch video record
        video_record = await db.videos.find_one({"_id": ObjectId(video_id)})
        if not video_record:
            raise ValueError(f"Video record not found for ID: {video_id}")

        # Setup output directory
        base_dir = Path(os.getenv('BASE_DIR', ''))
        output_dir = base_dir / f"{video_id}/output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{video_id}_output.mp4"

        # Fetch all scenes for the video
        scenes = await db.scenes.find({"video_id": ObjectId(video_id)}).to_list(length=None)

        if not scenes:
            raise ValueError(f"No scenes found for video ID: {video_id}")

        # Process each scene and create clips
        print("[INFO] Assembling video...")
        clips = []

        for scene in scenes:
            clip_with_voiceover = scene.get('clip_with_voiceover')

            if not clip_with_voiceover:
                raise ValueError(f"No voiceover found for scene {scene['_id']}")
            
            clips.append(clip_with_voiceover)

        # Assemble video clips
        concatenate_video_clips(clips, os.path.join(output_dir, filename))

        # Update video record with output file path
        await db.videos.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"files.output_file": str(output_dir / filename)}}
        )

        print(f"[INFO] Video assembled successfully: {output_dir / filename}")

    except Exception as e:
        raise RuntimeError(f"Failed to assemble video: {str(e)}") from e

