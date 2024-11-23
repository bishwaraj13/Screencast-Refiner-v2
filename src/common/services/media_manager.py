from pathlib import Path
from typing import Dict, Optional

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def extract_video_metadata(video_file: str) -> Dict[str, Optional[float]]:
    """Extract basic metadata from the video file."""
    try:
        with VideoFileClip(video_file) as video:
            return {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'audio_fps': video.audio.fps if video.audio else None,
                'audio_nchannels': video.audio.nchannels if video.audio else None
            }
    except Exception as e:
        raise ValueError(f"Failed to extract video metadata: {str(e)}") from e


def generate_audio_from_video(video_file: str, audio_path: Path) -> None:
    """Generate audio from the given video file and save it."""
    try:
        with VideoFileClip(video_file) as video:
            if video.audio is None:
                raise ValueError("Video has no audio track")
            video.audio.write_audiofile(str(audio_path))
    except Exception as e:
        raise ValueError(f"Failed to generate audio: {str(e)}") from e
    
def trim_video(video_file: str, time_start: float, time_end: float, output_filepath: str) -> None:
    """
    Generate a video clip from the given video file and save it.
    
    :param video_file: Path to the original video file
    :param time_start: Start time of the clip in seconds
    :param time_end: End time of the clip in seconds
    :param output_filepath: Path to save the generated video clip
    :return: Path to the generated video clip
    """
    try:
        # Generate the video clip
        ffmpeg_extract_subclip(video_file, time_start, time_end, targetname=output_filepath)
    except Exception as e:
        raise ValueError(f"Failed to extract video clip: {str(e)}") from e
