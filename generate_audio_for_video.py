#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_script(script_path, *args):
    """Run a Python script with the given arguments."""
    cmd = [sys.executable, script_path] + list(args)
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate audio for a Manim animation")
    parser.add_argument("manim_file", help="Path to the Manim Python file")
    parser.add_argument("--viz-plan", "-v", help="Path to JSON file containing the visualization plan")
    parser.add_argument("--output-dir", "-o", help="Output directory for audio files")
    parser.add_argument("--video-file", help="Path to the video file (if not specified, will find based on name)")
    
    args = parser.parse_args()
    
    # Check if Manim file exists
    if not os.path.exists(args.manim_file):
        print(f"Error: Manim file not found: {args.manim_file}")
        sys.exit(1)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== STEP 1: Generating Narration Script ===")
    voice_script_generator = os.path.join(base_dir, "voice_script_generator.py")
    
    # Build arguments for voice_script_generator
    voice_script_args = [args.manim_file]
    if args.viz_plan:
        voice_script_args.extend(["--viz-plan", args.viz_plan])
    
    manim_path = Path(args.manim_file)
    script_path = str(manim_path.parent / f"{manim_path.stem}_script.json")
    voice_script_args.extend(["--output", script_path])
    
    if not run_script(voice_script_generator, *voice_script_args):
        print("Failed to generate narration script. Aborting.")
        sys.exit(1)
    
    print("\n=== STEP 2: Generating TTS Audio ===")
    generate_tts = os.path.join(base_dir, "generate_tts_from_script.py")
    
    # Build arguments for generate_tts
    tts_args = [script_path]
    if args.output_dir:
        tts_args.extend(["--output-dir", args.output_dir])
    else:
        # Default output directory
        args.output_dir = f"tts_output/{manim_path.stem}"
        tts_args.extend(["--output-dir", args.output_dir])
    
    if not run_script(generate_tts, *tts_args):
        print("Failed to generate TTS audio. Aborting.")
        sys.exit(1)
    
    print("\n=== STEP 3: Combining Audio Segments ===")
    combine_audio = os.path.join(base_dir, "combine_audio_segments.py")
    
    # Timing info is in the output directory
    timing_info = os.path.join(args.output_dir, "timing_info.json")
    
    # Output file path for combined audio
    combined_audio = os.path.join(args.output_dir, f"{manim_path.stem}_voiceover.mp3")
    
    if not run_script(combine_audio, args.output_dir, "--output", combined_audio, "--timing", timing_info):
        print("Failed to combine audio segments. Aborting.")
        sys.exit(1)
    
    print("\n=== STEP 4: Adding Audio to Video ===")
    add_audio = os.path.join(base_dir, "add_audio_to_video_from_file.py")
    
    # Build arguments for add_audio
    add_audio_args = [combined_audio]
    if args.video_file:
        add_audio_args.extend(["--video", args.video_file])
    
    if not run_script(add_audio, *add_audio_args):
        print("Failed to add audio to video.")
        sys.exit(1)
    
    print("\n=== AUDIO GENERATION COMPLETE ===")
    print("All steps completed successfully!")

if __name__ == "__main__":
    main()