# AI-Powered Video Polisher

## Overview

This project is designed to take any screen-recorded explainer videos created by a Product Manager and convert them into polished, professional-quality videos. The process involves rephrasing sentences to correct grammatical errors and remove fillers, and using AI-generated professional voiceovers. This project aims to automate the video editing process, similar to what Loom does, but with the added power of AI for content enhancement and voice generation.

## Features

- **Video Preprocessing**: Extracts metadata and audio from the original video.
- **Transcription**: Converts the audio to text using Rev AI.
- **Content Generation**: Rephrases the transcribed text to correct grammar and remove fillers using Gemini AI.
- **Scene Generation**: Breaks down the video into scenes based on the rephrased text.
- **Clip Extraction**: Extracts video clips for each scene.
- **Audio Generation**: Generates professional voiceovers for each scene using OpenAI's Text-to-Speech (TTS) API.
- **Voiceover Addition**: Adds the generated voiceovers to the video clips.
- **Video Assembly**: Assembles the video clips with voiceovers into a final polished video.

## Project Structure
```bash
.
├── __init__.py
├── .env
├── .env.example
├── .gitignore
├── poetry.lock
├── pyproject.toml
├── README.md
├── run_orchestrator.py
└── src/
    ├── __init__.py
    ├── common/
    │   ├── __init__.py
    │   ├── decorators/
    │   │   ├── __init__.py
    │   │   └── step_tracker.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── media_manager.py
    │   │   ├── voice_generation_manager.py
    │   │   ├── content_generation_manager.py
    │   │   └── transcription_manager.py
    │   ├── static.py
    │   └── utils/
    ├── db/
    │   ├── __init__.py
    │   ├── mongo_client.py
    │   └── mongo_utils.py
    ├── orchestrator.py
    └── steps/
        ├── __init__.py
        ├── step_10_00_preprocess_video.py
        ├── step_20_00_transcribe_video.py
        ├── step_30_00_make_scenes.py
        ├── step_40_00_extract_clips.py
        ├── step_50_00_generate_audio.py
        ├── step_60_00_add_voiceover.py
        └── step_70_00_assemble_video.py
```

## Installation

1. Clone the repository:

```
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies

```
poetry install
```

3. Setup environment variables
- Copy `.env.example` to `.env` and fill in the required values.

## MongoDB Setup

This project requires a MongoDB database. The name of the DB has to be updated to .env file.

The following collections are needed:

- `videos`

    Initially, a document needs to be manually inserted into the `videos` collection. The document should have the look like following:

    Example document:

    ```json
    {
    "_id": ObjectId("673f39375ed8d665005a52b4"),
    "files": {
        "video_file": "/path/to/video.mp4"
    }
    }
    ```

- `pipeline_errors`

    Create an empty collection called `pipeline_errors`. This will store detailed logs about where it errored out. This is useful for debugging.

- `transcriptions`

    Create an empty collection called `transcriptions`. The transcriptions will be stored here.

- `scenes`

    Create an empty collection called `scenes`. Here the script breaks down the final transcripts to small sscenes.

- `voices`

    These are list of voices. Currently, its all by Open AI, but later you may add more form other service providers like Eleven Labs.

    Example:

    ```json
    {
        "_id" : ObjectId("6742b2d65ed8d665005a5346"),
        "name" : "alloy",
        "adulthood" : "Young",
        "gender" : "Male",
        "description" : "Neutral, professional, and clear",
        "service_provider" : "OpenAI",
        "dashboard_name" : "Alloy"
    }
    ```

## Usage
 1. Run the orchestrator

 `python run_orchestrator.py <video_id>`

 video_id is the `_id` from `videos` collection in MongoDB.

 ## Key steps that processes the raw video and makes it a polished one

 1. Video Preprocessing

    - Function: step_10_00_preprocess_video
    - File: src/steps/step_10_00_preprocess_video.py
    - Description: Extracts metadata and audio from the original video.

2. Transcription

    - Function: step_20_00_transcribe_video
    - File: src/steps/step_20_00_transcribe_video.py
    - Description: Converts the audio to text using Rev AI.

3. Scene Generation

    - Function: step_30_00_make_scenes
    - File: src/steps/step_30_00_make_scenes.py
    - Description: Rephrases the transcribed text to correct grammar and remove fillers using Gemini AI. Further, breaks down the video into scenes based on the rephrased text.

4. Clip Extraction

    - Function: step_40_00_extract_clips
    - File: src/steps/step_40_00_extract_clips.py
    - Description: Extracts video clips for each scene.

5. Audio Generation

    - Function: step_50_00_generate_audio
    - File: src/steps/step_50_00_generate_audio.py
    - Description: Generates professional voiceovers for each scene using OpenAI's Text-to-Speech (TTS) API.

6. Voiceover addition

    - Function: step_60_00_add_voiceover
    - File: src/steps/step_60_00_add_voiceover.py
    - Description: Adds the generated voiceovers to the video clips.

7. Video Assembly

    - Function: step_70_00_assemble_video
    - File: src/steps/step_70_00_assemble_video.py
    - Description: Assembles the video clips with voiceovers into a final polished video.



