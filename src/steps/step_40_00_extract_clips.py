"""
This function handles the extraction of video clips based on scene timestamps using moviepy.
It processes scenes from the database and creates corresponding video clips.
"""

import os
from pathlib import Path
from bson import ObjectId

from moviepy.editor import VideoFileClip
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..common.decorators.step_tracker import track_step
from ..common.services.media_manager import trim_video


@track_step
async def step_40_00_extract_clips(video_id: str, db: AsyncIOMotorDatabase) -> str:
    """
    Extract video clips based on scene timestamps using moviepy and update scene records.

    Args:
        video_id (str): MongoDB ObjectId of the video document as string
        db (AsyncIOMotorDatabase): MongoDB database connection

    Returns:
        str: Video ID of the processed document

    Raises:
        ValueError: If scenes not found or video file is inaccessible
        RuntimeError: If clip extraction process fails
    """
    try:
         # Fetch video record
        video_record = await db.videos.find_one({"_id": ObjectId(video_id)})
        if not video_record:
            raise ValueError(f"Video record not found for ID: {video_id}")

        video_file_path = video_record['files']['video_file']

        # Setup clips directory
        base_dir = Path(os.getenv('BASE_DIR', ''))
        clips_dir = base_dir / f"{video_id}/clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        # Ensure clips directory exists
        os.makedirs(clips_dir, exist_ok=True)

        # Fetch all scenes for the video
        scenes = await db.scenes.find({"video_id": ObjectId(video_id)}).to_list(length=None)

        if not scenes:
            raise ValueError(f"No scenes found for video ID: {video_id}")

        if not os.path.exists(video_file_path):
            raise ValueError(f"Video file not found at path: {video_file_path}")

        # Process each scene and create clips
        print("[INFO] Extracting clips...")
        for scene in scenes:
            scene_id = scene['_id']
            time_start = scene['time_start']
            time_end = scene['time_end']

            # Generate output path for the clip
            clip_filename = f"scene_{time_start}_{time_end}.mp4"
            clip_file_path = os.path.join(clips_dir, clip_filename)

            trim_video(video_file_path,
                       time_start,
                       time_end,
                       clip_file_path)
            
            db.scenes.update_one(
                {"_id": ObjectId(scene_id)},
                {"$set": {"clip_file_path": clip_file_path}}
            )

    except Exception as e:
        raise RuntimeError(f"Clip extraction process failed: {str(e)}") from e
    