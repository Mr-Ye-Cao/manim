#!/usr/bin/env python3
"""
Orchestration pipeline script: runs the full workflow end-to-end.
Steps:
 1. Generate ideas and director plans (step1_and_2.py)
 2. Implement Manim scenes (step3_code_impl.py)
 3. Generate TTS, combine audio, and merge with videos (step4_generate_audio.py)
"""
import subprocess
import sys
import json

def run_cmd(cmd):
    print(f"\n>>> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"Error: command failed with exit code {result.returncode}: {' '.join(cmd)}")


def main():
    # Step 1 & 2: ideas + plans
    run_cmd([sys.executable, 'step1_and_2.py'])

    # Step 3: generate and render scenes for selected ideas
    run_cmd([sys.executable, 'step3_code_impl.py', '--input', 'step1_and_2_output.json'])

    # Load results to know which IDs to process
    with open('step3_output.json') as f:
        data = json.load(f)
    ids = [item['id'] for item in data.get('results', [])]
    if not ids:
        sys.exit('No rendered scenes found in step3_output.json')

    # Step 4 & 5: for each idea, generate audio and merge
    for id_ in ids:
        run_cmd([
            sys.executable, 'step4_generate_audio.py',
            '--input', 'step3_output.json',
            '--id', str(id_),
        ])

    print("\nPipeline complete! Final videos with audio are in the 'videos' directory.")

if __name__ == '__main__':
    main() 