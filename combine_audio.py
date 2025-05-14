from pydub import AudioSegment
import os

def combine_audio_files():
    """Combine all MP3 files in the tts_output directory into a single audio file."""
    print("Starting audio combination process...")
    
    # Get all MP3 files and sort them
    audio_files = [f for f in os.listdir("tts_output") if f.endswith(".mp3")]
    audio_files.sort()  # Sort files by name
    
    print(f"Found {len(audio_files)} audio files to combine.")
    
    # Create an empty audio segment
    combined = AudioSegment.empty()
    
    # Add a 1-second silence at the beginning
    silence = AudioSegment.silent(duration=1000)
    combined += silence
    
    # Combine all audio files
    for i, file in enumerate(audio_files):
        print(f"Adding file {i+1}/{len(audio_files)}: {file}")
        audio_path = os.path.join("tts_output", file)
        audio = AudioSegment.from_mp3(audio_path)
        
        # Add the audio segment
        combined += audio
        
        # Add silence after each segment to create natural pauses
        # Add longer pauses for certain segments to match the animation timing
        if i in [0, 1, 3, 6, 13, 17, 20, 23]:  # After major section breaks
            silence_duration = 1500  # 1.5 seconds
        else:
            silence_duration = 800  # 0.8 seconds
            
        combined += AudioSegment.silent(duration=silence_duration)
    
    # Export the combined audio
    output_path = "tts_output/taylor_series_voiceover.mp3"
    combined.export(output_path, format="mp3")
    print(f"Combined audio saved to {output_path}")
    
    return output_path

if __name__ == "__main__":
    try:
        output_file = combine_audio_files()
        print(f"Successfully created combined audio file: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}") 