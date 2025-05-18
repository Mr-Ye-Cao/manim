#!/usr/bin/env python3
"""
CLI tool for pipeline step 4: generate synchronized audio and merge with video.
"""
import os
import sys
import json
import argparse
import re
import subprocess
from openai import OpenAI
from pydub import AudioSegment


def generate_voice_segments(client, plan_text: str):
    """Use Chat Completion to convert a plan into timed narration segments."""
    system_prompt = (
        "You are an educational video scriptwriter. Given a high-level plan with time ranges, "
        "produce a JSON array of objects with keys: start (in seconds), end (in seconds), text (narration). "
        "Do not include any extra text, only the JSON array."  
    )
    user_prompt = f"Plan:\n{plan_text}\n\nReturn only the JSON array."
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    content = resp.choices[0].message.content
    # Extract JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\n([\s\S]*?)```", content)
        if m:
            return json.loads(m.group(1))
        else:
            print("Error: could not parse JSON from ChatGPT response.")
            print(content)
            sys.exit(1)


def synthesize_tts(client, segments, out_dir):
    """Generate TTS for each segment and return list of file paths."""
    os.makedirs(out_dir, exist_ok=True)
    audio_files = []
    for i, seg in enumerate(segments):
        text = seg['text']
        print(f"Generating TTS for segment {i+1}/{len(segments)}: {text[:30]}...")
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=text
        )
        filename = os.path.join(out_dir, f"segment_{i+1:02d}.mp3")
        response.stream_to_file(filename)
        audio_files.append(filename)
    return audio_files


def combine_segments(segments, audio_files, output_path):
    """Combine audio files with silences to align with segment start times."""
    combined = AudioSegment.silent(duration=int(segments[0]['start'] * 1000))
    for i, (seg, file) in enumerate(zip(segments, audio_files)):
        audio = AudioSegment.from_file(file)
        # If combined duration < segment start, pad silence
        current_ms = len(combined)
        target_ms = int(seg['start'] * 1000)
        if target_ms > current_ms:
            combined += AudioSegment.silent(duration=target_ms - current_ms)
        combined += audio
    # Export
    combined.export(output_path, format="mp3")
    return output_path


def merge_audio_video(video_file, audio_file, output_file):
    """Use FFmpeg to merge the combined audio with the video."""
    cmd = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-y",
        output_file,
    ]
    print("Merging audio and video with command:", ' '.join(cmd))
    subprocess.run(cmd, check=True)
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Step 4: Generate and merge audio for videos.")
    parser.add_argument("-i", "--input", default="step3_output.json", help="Path to step3 output JSON.")
    parser.add_argument("-d", "--id", type=int, default=1, help="ID of the idea/video to process.")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    data = json.load(open(args.input))
    item = next((x for x in data['results'] if x['id'] == args.id), None)
    if not item:
        print(f"Error: no result with id {args.id} found in {args.input}.")
        sys.exit(1)

    plan = item['plan']
    video_file = item['video_path']
    base = os.path.splitext(os.path.basename(video_file))[0]

    print(f"Generating voice segments for Idea {args.id}...")
    segments = generate_voice_segments(client, plan)
    script_json = f"audio_output/{base}_script_segments.json"
    os.makedirs("audio_output", exist_ok=True)
    with open(script_json, 'w') as f:
        json.dump(segments, f, indent=2)
    print(f"Saved segments to {script_json}")

    print("Synthesizing TTS audio...")
    audio_dir = os.path.join("audio_output", base)
    audio_files = synthesize_tts(client, segments, audio_dir)

    combined_audio = os.path.join("audio_output", f"{base}_voiceover.mp3")
    print("Combining audio segments...")
    combine_segments(segments, audio_files, combined_audio)

    final_video = f"videos/{base}_with_audio.mp4"
    print(f"Merging audio into video to create {final_video}...")
    merge_audio_video(video_file, combined_audio, final_video)

    # Summary
    output = {
        "id": args.id,
        "video": video_file,
        "segments_json": script_json,
        "combined_audio": combined_audio,
        "final_video": final_video,
    }
    with open("step4_output.json", 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Step 4 complete. Summary in step4_output.json")


if __name__ == '__main__':
    main() 