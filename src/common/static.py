STEP_DEPENDENCIES = {
    "step_10_00_preprocess_video": [],  # No dependencies
    "step_20_00_fetch_transcription": ["step_10_00_preprocess_video"],
    "step_30_00_make_scenes": ["step_20_00_fetch_transcription"],
    "step_40_00_make_video_clips": ["step_30_00_make_scenes"],
    "step_50_00_tts": ["step_30_00_make_scenes"],
    "step_60_00_assemble_video": ["step_40_00_make_video_clips", "step_50_00_tts"],
}

prompt_template = '''
You are a video transcription analysis expert. I will provide you with a JSON object containing the transcription of a video. The JSON will have a structure like this:
{
  "monologues": [
    {
      "speaker": 0,
      "elements": [
        {
          "type": "text",
          "value": "Let's",
          "ts": 0.175,
          "end_ts": 0.525,
          "confidence": 0.81
        },
        // ... other elements
      ]
    }
  ]
}

Please analyze the transcription and break it down into small granular steps. 

E.g, if you have "Let's see. You can add a button on, um, notion. So here I'm on welcome, uh, page. I can click here. Then I can put a slash, let me write button and then select button."

This can be broken down to three steps (1) showing welcome page, (2) clicking on the '+' sign, and (3) adding a button.

Based on the timestamps (ts and end_ts), provide a JSON response with the following structure:

{
  "steps": [
    {
      "title": "Introduction to A/B Testing",
      "time_start": 0.175,
      "time_end": 12.525,
      "original_narration": "Okay, so A/B testing is like, um, comparing two versions of something to see which one works better. It's pretty useful for websites and apps.",
      "polished_narration": "Let's explore A/B testing, a powerful method for comparing two versions of a webpage or app to determine which performs better. This approach allows you to make data-driven decisions for your digital products."
    }
  ]
}

The steps should be granular and aim to synchronize the narration with specific visual cues. The "polished_narration" should sound professional.

transcription_dict = {transcription_dict}

'''
