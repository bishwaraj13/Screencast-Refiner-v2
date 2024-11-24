from pathlib import Path
from typing import Dict, Optional, List

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips
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
    
def add_audio_to_video(video_path, audio_path, output_path):
    """
    Add audio to a video clip and save the result to a new file.
    
    :param video_path: Path to the original video file
    :param audio_path: Path to the audio file
    :param output_path: Path to save the video with audio
    """
    # Load the video and audio clips
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Get durations
    video_duration = video.duration
    audio_duration = audio.duration

    if audio_duration > video_duration:
        # If audio is longer, extend the first frame of the video
        first_frame = video.to_ImageClip(t=0).set_duration(audio_duration - video_duration)
        extended_video = CompositeVideoClip([first_frame, video.set_start(audio_duration - video_duration)])
        video_with_audio = extended_video.set_audio(audio)
    else:
        # If video is longer, speed up the video
        speed_factor = video_duration / audio_duration
        video_with_audio = video.speedx(factor=speed_factor).set_audio(audio)

    # Write the result to a file
    video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Close the clips
    video.close()
    audio.close()
    video_with_audio.close()

def concatenate_video_clips(video_clips: List[str], output_path: str) -> None:
    """
    Concatenate multiple video clips into a single video file.
    
    :param video_clips: List of video clips to concatenate
    :param output_path: Path to save the concatenated video
    """
    # Load the video clips
    clips = [VideoFileClip(clip) for clip in video_clips]

    # Concatenate the clips
    composite_video = concatenate_videoclips(clips)

    # Write the result to a file
    composite_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Close the clips
    composite_video.close()
    for clip in clips:
        clip.close()
