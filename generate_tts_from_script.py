#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from openai import OpenAI

def get_client():
    """Initialize the OpenAI client with API key from environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def load_script(script_path):
    """Load the script file, which can be JSON or TXT format."""
    if script_path.endswith('.json'):
        # Load the JSON script format
        with open(script_path, 'r') as f:
            return json.load(f)
    elif script_path.endswith('.txt'):
        # Parse the text format script
        with open(script_path, 'r') as f:
            content = f.read()
            
        # Extract the scene name from the first line
        lines = content.splitlines()
        scene_name = lines[0].replace("Script for: ", "").strip()
        
        # Parse segments from the text file
        segments = []
        current_segment = None
        
        for line in lines[2:]:  # Skip the first two header lines
            if not line.strip():
                continue
                
            if line.startswith('['):
                # This is a new segment header
                if current_segment:
                    segments.append(current_segment)
                
                # Parse the time information and description
                time_info, description = line.split(']', 1)
                time_info = time_info[1:]  # Remove the opening bracket
                start_time, end_time = time_info.split('-')
                start_time = float(start_time.replace('s', '').strip())
                end_time = float(end_time.replace('s', '').strip())
                duration = end_time - start_time
                
                current_segment = {
                    "start_time": start_time,
                    "duration": duration,
                    "description": description.strip(),
                    "narration": ""
                }
            elif current_segment:
                # This is narration text for the current segment
                current_segment["narration"] += line + " "
        
        # Add the last segment
        if current_segment:
            segments.append(current_segment)
            
        return {
            "scene_name": scene_name,
            "segments": segments
        }
    else:
        print(f"Error: Unsupported file format for {script_path}")
        sys.exit(1)

def generate_audio(client, script, output_dir):
    """Generate TTS audio for each script segment."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate audio for each segment
    for i, segment in enumerate(script["segments"]):
        segment_id = i + 1
        narration = segment["narration"].strip()
        description = segment["description"]
        
        print(f"Generating audio for segment {segment_id}/{len(script['segments'])}: {description}")
        print(f"Text: {narration[:50]}...")
        
        try:
            # Use the OpenAI TTS API
            response = client.audio.speech.create(
                model="tts-1-hd",  # Using high-definition quality
                voice="onyx",      # Using Onyx voice which is good for educational content
                input=narration
            )
            
            # Save audio file
            filename = f"{output_dir}/segment_{segment_id:02d}.mp3"
            response.stream_to_file(filename)
            print(f"Saved to {filename}")
            
        except Exception as e:
            print(f"Error generating audio for segment {segment_id}: {e}")
    
    print("All audio files generated!")
    
    # Create a reference file with timing information
    with open(f"{output_dir}/timing_info.json", "w") as f:
        json.dump({
            "scene_name": script["scene_name"],
            "segments": [
                {
                    "segment_id": i + 1,
                    "start_time": segment["start_time"],
                    "duration": segment["duration"],
                    "description": segment["description"]
                }
                for i, segment in enumerate(script["segments"])
            ]
        }, f, indent=2)
    
    print(f"Timing information saved to {output_dir}/timing_info.json")
    return output_dir

def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio from a script")
    parser.add_argument("script_path", help="Path to the script file (JSON or TXT)")
    parser.add_argument("--output-dir", "-o", help="Output directory for audio files")
    
    args = parser.parse_args()
    
    # Check if script file exists
    if not os.path.exists(args.script_path):
        print(f"Error: Script file not found: {args.script_path}")
        sys.exit(1)
    
    # Set default output directory
    if not args.output_dir:
        script_path = Path(args.script_path)
        scene_name = script_path.stem.replace("_script", "")
        args.output_dir = f"tts_output/{scene_name}"
    
    client = get_client()
    script = load_script(args.script_path)
    output_dir = generate_audio(client, script, args.output_dir)
    
    print(f"\nAll audio segments have been generated in {output_dir}")
    print(f"You can now combine these segments using:")
    print(f"python combine_audio_segments.py {output_dir}")

if __name__ == "__main__":
    main()