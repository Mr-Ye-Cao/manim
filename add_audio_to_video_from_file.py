#!/usr/bin/env python3
import os
import sys
import glob
import argparse
import subprocess
from pathlib import Path

def add_audio_to_video(audio_file, video_file=None, output_file=None):
    """
    Add audio to a video file using FFmpeg.
    
    Args:
        audio_file: Path to the audio file
        video_file: Path to the video file (if None, will search in videos directory)
        output_file: Path to save the output video (if None, will create based on video name)
    """
    print("Starting process to add audio to video...")
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return None
    
    # If no video file is specified, find the most recent matching video
    if not video_file:
        # Get the scene name from the audio filename
        audio_path = Path(audio_file)
        scene_name = audio_path.stem.replace("_voiceover", "")
        
        # Look for video files in the videos directory
        video_pattern = f"videos/*{scene_name}*.mp4"
        video_files = glob.glob(video_pattern)
        
        if not video_files:
            print(f"Error: No matching video files found with pattern: {video_pattern}")
            return None
        
        # Get the most recent video by modification time
        video_file = max(video_files, key=os.path.getmtime)
    
    # Check if video file exists
    if not os.path.exists(video_file):
        print(f"Error: Video file not found: {video_file}")
        return None
    
    print(f"Using video file: {video_file}")
    print(f"Using audio file: {audio_file}")
    
    # Output file with audio
    if not output_file:
        video_path = Path(video_file)
        output_file = str(video_path.parent / f"{video_path.stem}_with_audio.mp4")
    
    # Use FFmpeg to combine video and audio
    print(f"Combining video and audio into {output_file}...")
    
    # FFmpeg command to add audio to video while preserving original video
    cmd = [
        "ffmpeg", 
        "-i", video_file,  # Input video file
        "-i", audio_file,  # Input audio file
        "-map", "0:v",     # Use video from the first input
        "-map", "1:a",     # Use audio from the second input
        "-c:v", "copy",    # Copy the video stream without re-encoding
        "-c:a", "aac",     # Audio codec
        "-shortest",       # End when the shortest input ends
        "-y",              # Overwrite output file if it exists
        output_file        # Output file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        print("Audio successfully added to video!")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")
        print(f"Error output: {e.stderr.decode()}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Add audio to a video file")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("--video", "-v", help="Path to the video file")
    parser.add_argument("--output", "-o", help="Output file path for the combined video")
    
    args = parser.parse_args()
    
    output_file = add_audio_to_video(args.audio_file, args.video, args.output)
    
    if output_file and os.path.exists(output_file):
        print(f"\nFinal video with audio available at: {output_file}")
        
        # Try to open the video file
        try:
            if os.name == 'posix':  # macOS or Linux
                os.system(f"open '{output_file}'")
            elif os.name == 'nt':   # Windows
                os.system(f'start "" "{output_file}"')
            print("Video opened in default player.")
        except Exception as e:
            print(f"Video created but couldn't automatically open it: {e}")
    else:
        print("Failed to create video with audio.")
        sys.exit(1)

if __name__ == "__main__":
    main()