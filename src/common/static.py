STEP_DEPENDENCIES = {
    "step_10_00_preprocess_video": [],  # No dependencies
    "step_20_00_fetch_transcription": ["step_10_00_preprocess_video"],
    "step_30_00_make_scenes": ["step_20_00_fetch_transcription"],
    "step_40_00_make_video_clips": ["step_30_00_make_scenes"],
    "step_50_00_tts": ["step_30_00_make_scenes"],
    "step_60_00_assemble_video": ["step_40_00_make_video_clips", "step_50_00_tts"],
}
