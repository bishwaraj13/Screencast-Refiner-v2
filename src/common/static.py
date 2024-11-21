STEP_DEPENDENCIES = {
    "STEP_10_00_preprocess_video": [],  # No dependencies
    "STEP_20_00_fetch_transcription": ["STEP_10_00_preprocess_video"],
    "STEP_30_00_make_scenes": ["STEP_20_00_fetch_transcription"],
    "STEP_40_00_make_video_clips": ["STEP_30_00_make_scenes"],
    "STEP_50_00_tts": ["STEP_30_00_make_scenes"],
    "STEP_60_00_assemble_video": ["STEP_40_00_make_video_clips", "STEP_50_00_tts"],
}
