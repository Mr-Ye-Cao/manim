#!/usr/bin/env python3
"""
Analyze a video using Gemini 1.5 Pro and provide constructive feedback on improvements.
Make sure you have installed the Google GenAI client: `pip install google-genai`.
Set your API key in the environment variable `GOOGLE_API_KEY`.
"""

import os
import sys
import time
from google import genai


def main():
    # Retrieve API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set the GOOGLE_API_KEY environment variable and try again.", file=sys.stderr)
        sys.exit(1)

    # Initialize the GenAI client
    client = genai.Client(api_key=api_key)

    # Path to the video file relative to this script
    video_path = os.path.join(os.path.dirname(__file__), "TaylorSeriesDirectorsCut_with_audio.mp4")
    if not os.path.isfile(video_path):
        print(f"Error: Video file not found at {video_path}", file=sys.stderr)
        sys.exit(1)

    # Upload the video file using the Files API
    print(f"Uploading video: {video_path}...")
    video_file = client.files.upload(file=video_path)
    print(f"Uploaded. File URI: {video_file.uri}\n")

    # Wait for the file to become active
    print("Waiting for file activation (30 seconds)...")
    time.sleep(30)

    # Define a prompt for feedback
    prompt = (
        "Please watch the attached video and provide constructive feedback on how "
        "to improve its pacing, visual clarity, audio quality, and overall engagement."
    )

    # Generate feedback using Gemini 1.5 Pro
    print("Generating feedback with Gemini 1.5 Pro...")
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=[video_file, prompt],
    )

    # Output the feedback
    print("\n=== Video Improvement Feedback ===\n")
    print(response.text)


if __name__ == "__main__":
    main() 