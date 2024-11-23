from moviepy.editor import VideoFileClip
from pathlib import Path
from typing import Dict, Optional

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