# Manim Educational Video Pipeline

This repository contains a complete pipeline for creating educational videos using Manim, powered by AI. The pipeline handles everything from idea generation to final video production with narration.

## Pipeline Overview

The pipeline consists of 5 main steps:

1. **Idea Generation**: Generate novel, interesting educational ideas worth illustrating
2. **Creative Direction**: Develop detailed visualization plans for your ideas
3. **Manim Implementation**: Generate, debug, and render Manim code
4. **Voice Script Generation**: Create narration that matches your animation
5. **Audio-Video Combination**: Combine audio and video for the final product

## Components

### 1. Idea Generation & Creative Direction
- `manim_idea_generator.py`: Interactive CLI for generating and selecting ideas, then creating detailed visualization plans

### 2. Manim Implementation
- `manim_implementer.py`: Converts visualization plans to executable Manim code with automated debugging

### 3-5. Audio Generation & Combination
- `voice_script_generator.py`: Analyzes Manim code and generates a narration script
- `generate_tts_from_script.py`: Generates TTS audio for each segment
- `combine_audio_segments.py`: Combines audio with appropriate timing
- `add_audio_to_video_from_file.py`: Adds audio to the rendered video
- `generate_audio_for_video.py`: One-click script for the entire audio pipeline

## Quick Start

### Step 1: Generate Ideas and Visualization Plan
```bash
python manim_idea_generator.py
```
This will prompt you for a topic and generate ideas, then create a visualization plan for your selected idea.

### Step 2: Implement the Visualization
```bash
python manim_implementer.py path/to/visualization_plan.json
```
This will generate Manim code, debug it automatically, and render the animation.

### Step 3: Generate Audio and Combine with Video
```bash
python generate_audio_for_video.py path/to/your_manim_file.py --viz-plan path/to/visualization_plan.json
```
This will analyze your Manim code, generate a narration script, create audio, and combine it with your video.

## Example Workflow

1. **Generate ideas about black holes**:
   ```bash
   python manim_idea_generator.py
   # Enter "black holes" when prompted
   # Select idea #3 when prompted
   # This creates visualization_plan.json
   ```

2. **Implement the visualization**:
   ```bash
   python manim_implementer.py visualization_plan.json
   # This creates black_hole_photon_sphere.py and renders it
   # The video is saved in videos/BLACK_HOLE_PHOTON_SPHERE_SCENE.mp4
   ```

3. **Generate audio and add to video**:
   ```bash
   python generate_audio_for_video.py illustrate/black_hole_photon_sphere.py --viz-plan visualization_plan.json
   # This creates a script, generates audio, and combines it with the video
   # The final video is saved as videos/BLACK_HOLE_PHOTON_SPHERE_SCENE_with_audio.mp4
   ```

## Requirements

- Python 3.7+
- OpenAI API key (set as OPENAI_API_KEY environment variable)
- ManimGL
- FFmpeg
- Python packages: openai, pydub, numpy

## Documentation

For detailed documentation on each component:

- [Audio Pipeline Documentation](audio_pipeline_docs.md): Details on the voice script generation and audio combination
- Check the header comments in each Python file for specific usage instructions

## Project Structure

```
manim-claude/
├── manim_idea_generator.py     # Step 1-2: Idea generation & creative direction
├── manim_implementer.py        # Step 3: Manim code generation & debugging
├── voice_script_generator.py   # Step 4: Voice script generation 
├── generate_tts_from_script.py # Step 4: TTS audio generation
├── combine_audio_segments.py   # Step 5: Audio segment combination
├── add_audio_to_video_from_file.py  # Step 5: Audio-video combination
├── generate_audio_for_video.py # All-in-one script for steps 4-5
├── illustrate/                 # Generated Manim code files
├── videos/                     # Rendered videos
└── tts_output/                 # Generated audio files
```

## Advanced Usage

### Custom Output Locations
You can specify custom output directories for both the Manim code and the audio:

```bash
python manim_implementer.py visualization_plan.json --output-dir custom/manim/dir
python generate_audio_for_video.py path/to/manim_file.py --output-dir custom/audio/dir
```

### Pipeline Integration
To run the entire pipeline in one go:

```bash
# 1. Generate idea and plan
python manim_idea_generator.py --topic "quantum mechanics" --output plan.json

# 2. Implement visualization
python manim_implementer.py plan.json --output-dir illustrate

# 3. Generate audio and combine with video
python generate_audio_for_video.py illustrate/quantum_mechanics.py --viz-plan plan.json
```