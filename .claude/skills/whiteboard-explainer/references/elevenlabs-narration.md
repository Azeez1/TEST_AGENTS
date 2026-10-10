# ElevenLabs narration

ElevenLabs is the default voice layer. Generate narration only after the script and voice direction are approved.

## Planning

Run `plan_narration.py` to create `audio/elevenlabs-request.json`. It concatenates scene narration in order, records the character count, and makes no API call.

Before a paid call:

- confirm the ElevenLabs connection/subscription is active;
- confirm `voice_id` or `voice_name`;
- preview a short sample when the voice is new;
- show the user any current usage or cost information available from the provider;
- confirm pronunciation for names, acronyms, brands, and numbers.

## Default call

Use `mcp__elevenlabs__text_to_speech` with:

- `model_id`: `eleven_multilingual_v2` for final quality;
- `output_format`: `mp3_44100_128`, unless the audio pipeline requests PCM/WAV;
- `speed`: `1.0`, adjusted only for the intended delivery;
- `output_directory`: the project's absolute `audio/` folder.

Save the audio as `audio/narration.mp3` and record the actual tool response, voice, model, and settings in `audio/narration.json`.

For scene-accurate captions, transcribe the final narration audio after generation and use those timings. Do not estimate word timestamps from script length when tight synchronization matters.

## Performance direction

Favor a conversational explanation with crisp emphasis and short intentional pauses. Avoid announcer cadence. The hook should arrive immediately; the last line should have a clean final hold rather than trailing off.

