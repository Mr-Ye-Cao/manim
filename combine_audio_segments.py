#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from pydub import AudioSegment

def combine_audio_files(audio_dir, output_file=None, timing_info=None):
    """
    Combine all MP3 files in the given directory into a single audio file.
    
    Args:
        audio_dir: Directory containing the audio segments
        output_file: Path to save the combined audio
        timing_info: Path to JSON file with timing information
    """
    print(f"Starting audio combination process for {audio_dir}...")
    
    # Get all MP3 files and sort them
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3") and f.startswith("segment_")]
    audio_files.sort()  # Sort files by name
    
    print(f"Found {len(audio_files)} audio files to combine.")
    
    # Try to load timing information if available
    segments_info = None
    if timing_info:
        try:
            with open(timing_info, 'r') as f:
                segments_info = json.load(f)
                print(f"Loaded timing information for {len(segments_info['segments'])} segments")
        except Exception as e:
            print(f"Warning: Could not load timing information: {e}")
    
    # If timing info wasn't provided but exists in the audio directory, use it
    if not segments_info and os.path.exists(os.path.join(audio_dir, "timing_info.json")):
        try:
            with open(os.path.join(audio_dir, "timing_info.json"), 'r') as f:
                segments_info = json.load(f)
                print(f"Loaded timing information from {audio_dir}/timing_info.json")
        except Exception as e:
            print(f"Warning: Could not load timing information: {e}")
    
    # Set default output file if not specified
    if not output_file:
        dir_name = os.path.basename(os.path.normpath(audio_dir))
        output_file = f"{audio_dir}/{dir_name}_voiceover.mp3"
    
    # Create an empty audio segment
    combined = AudioSegment.empty()
    
    # Add a 1-second silence at the beginning
    silence = AudioSegment.silent(duration=1000)
    combined += silence
    
    # Get the total animation duration if available
    total_animation_duration = 0
    if segments_info:
        for segment in segments_info['segments']:
            end_time = segment['start_time'] + segment['duration']
            if end_time > total_animation_duration:
                total_animation_duration = end_time
        print(f"Total animation duration: {total_animation_duration:.1f} seconds")
    
    # Current position in the combined audio (in milliseconds)
    current_position = 1000  # Start after the initial 1-second silence
    
    # Combine all audio files
    for i, file in enumerate(audio_files):
        print(f"Adding file {i+1}/{len(audio_files)}: {file}")
        segment_id = int(file.replace("segment_", "").replace(".mp3", ""))
        audio_path = os.path.join(audio_dir, file)
        audio = AudioSegment.from_mp3(audio_path)
        
        # If we have timing information, calculate the needed silence before this segment
        if segments_info:
            # Find the corresponding segment in timing_info
            segment_info = next((s for s in segments_info['segments'] if s['segment_id'] == segment_id), None)
            
            if segment_info:
                # Calculate the target start time in milliseconds
                target_start_time = segment_info['start_time'] * 1000
                
                # If we're behind, add silence to catch up
                if current_position < target_start_time:
                    silence_needed = target_start_time - current_position
                    print(f"Adding {silence_needed/1000:.2f}s silence before segment {segment_id} to sync with animation")
                    combined += AudioSegment.silent(duration=silence_needed)
                    current_position = target_start_time
                # If we're ahead, print a warning (we can't cut audio that's already added)
                elif current_position > target_start_time:
                    print(f"Warning: Audio is {(current_position - target_start_time)/1000:.2f}s ahead of animation at segment {segment_id}")
        
        # Add the audio segment
        combined += audio
        current_position += len(audio)
        
        # Add silence after segments (if we don't have specific timing information)
        if not segments_info:
            # Add longer pauses after major transitions, shorter pauses elsewhere
            if i % 3 == 0:  # Every third segment gets a longer pause
                silence_duration = 1500  # 1.5 seconds
            else:
                silence_duration = 800  # 0.8 seconds
                
            combined += AudioSegment.silent(duration=silence_duration)
            current_position += silence_duration
    
    # If we have timing info, add silence at the end to match animation duration
    if segments_info and total_animation_duration > 0:
        # Convert to milliseconds
        animation_end = total_animation_duration * 1000
        
        # If our audio is shorter than the animation, add silence
        if current_position < animation_end:
            silence_needed = animation_end - current_position
            print(f"Adding {silence_needed/1000:.2f}s silence at the end to match animation duration")
            combined += AudioSegment.silent(duration=silence_needed)
        # If our audio is longer, print warning
        elif current_position > animation_end:
            print(f"Warning: Final audio is {(current_position - animation_end)/1000:.2f}s longer than animation")
    
    # Export the combined audio
    combined.export(output_file, format="mp3")
    print(f"Combined audio saved to {output_file}")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Combine audio segments into a single audio file")
    parser.add_argument("audio_dir", help="Directory containing the audio segments")
    parser.add_argument("--output", "-o", help="Output file path for the combined audio")
    parser.add_argument("--timing", "-t", help="Path to JSON file with timing information")
    
    args = parser.parse_args()
    
    # Check if audio directory exists
    if not os.path.exists(args.audio_dir):
        print(f"Error: Audio directory not found: {args.audio_dir}")
        sys.exit(1)
    
    try:
        output_file = combine_audio_files(args.audio_dir, args.output, args.timing)
        print(f"Successfully created combined audio file: {output_file}")
        print(f"You can now add this audio to your video using:")
        print(f"python add_audio_to_video.py {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()