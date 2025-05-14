import os
import subprocess
import glob

def add_audio_to_video():
    """Add the generated voiceover to the Taylor Series animation video."""
    print("Starting process to add audio to video...")
    
    # Find the most recent Taylor Series video file
    video_files = glob.glob("videos/TaylorSeriesDirectorsCut*.mp4")
    
    if not video_files:
        print("Error: No Taylor Series video files found in the videos directory.")
        return None
    
    # Get the most recent video by modification time
    video_file = max(video_files, key=os.path.getmtime)
    print(f"Found video file: {video_file}")
    
    # The audio file we generated
    audio_file = "tts_output/taylor_series_voiceover.mp3"
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found.")
        return None
    
    # Output file with audio
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    output_file = f"videos/{base_name}_with_audio.mp4"
    
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

if __name__ == "__main__":
    output_file = add_audio_to_video()
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