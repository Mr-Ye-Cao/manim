#!/usr/bin/env python3
"""
Manim Educational Video Workflow Orchestration

This script orchestrates the complete workflow for creating educational videos with Manim:
1. Idea generation with topic-based prompts
2. Implementation of selected ideas using Manim
3. Voice script generation for each video
4. Text-to-speech audio generation
5. Audio segment combination
6. Final video with audio production

The workflow is designed to be flexible, allowing for both automated and interactive use.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import traceback
import re

# Define directories
IDEA_DIR = Path("idea_outputs")
CODE_DIR = Path("manim_code")
TTS_DIR = Path("tts_output")
VIDEO_DIR = Path("videos")

def ensure_dirs_exist():
    """Create all necessary directories if they don't exist."""
    for dir_path in [IDEA_DIR, CODE_DIR, TTS_DIR, VIDEO_DIR]:
        dir_path.mkdir(exist_ok=True)
    print("✓ All required directories exist")

def check_environment():
    """Check if all required environment variables and tools are available."""
    # Check OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key using:")
        print("  export OPENAI_API_KEY=\"your-api-key\"")
        return False
        
    # Check for FFmpeg installation
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: FFmpeg not found. Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
        
    # Check for Manim installation
    try:
        subprocess.run(["manimgl", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Manim (ManimGL) not found or not in PATH.")
        print("Please make sure Manim is installed and available in your PATH.")
        print("Installation instructions: https://docs.manim.community/en/stable/installation.html")
        return False
        
    print("✓ Environment check passed")
    return True

def run_script(script_path, *args, capture_output=True):
    """
    Run a Python script with the given arguments.
    
    Args:
        script_path: Path to the Python script
        *args: Arguments to pass to the script
        capture_output: Whether to capture and return stdout/stderr
        
    Returns:
        tuple: (success, stdout, stderr)
    """
    # Convert Path objects to strings
    script_path_str = str(script_path)
    args_str = [str(arg) for arg in args]
    
    cmd = [sys.executable, script_path_str] + args_str
    print(f"Running: {' '.join(cmd)}")
    
    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            # Run with stdout/stderr passed through to console
            result = subprocess.run(cmd)
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"Error running script: {e}")
        traceback.print_exc()
        return False, "", str(e)

def step1_generate_ideas(topic, num_ideas=5, all_ideas=False, select_ids=None):
    """
    Step 1: Generate ideas for educational videos on a given topic.
    
    Args:
        topic: The topic to generate ideas for
        num_ideas: Number of ideas to generate
        all_ideas: Whether to select all generated ideas
        select_ids: Specific idea IDs to select (comma-separated string)
        
    Returns:
        tuple: (success, ideas_filepath)
    """
    print("\n" + "="*80)
    print(f"STEP 1: GENERATING IDEAS FOR TOPIC: {topic}")
    print("="*80)
    
    script_path = Path("manim_idea_generator.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, None
    
    # Build command arguments
    cmd_args = ["--topic", topic, "--num-ideas", str(num_ideas)]
    
    if all_ideas:
        cmd_args.append("--all")
    elif select_ids:
        cmd_args.extend(["--select", select_ids])
    
    # Execute idea generator script
    success, stdout, stderr = run_script(script_path, *cmd_args, capture_output=False)
    
    if not success:
        print("Error generating ideas. Check the output above for details.")
        return False, None
    
    # Find the output file path from the stdout
    idea_files = sorted(IDEA_DIR.glob(f"{topic.lower().replace(' ', '_')}*.json"), 
                        key=os.path.getmtime, 
                        reverse=True)
    
    if not idea_files:
        print("Error: No idea file was generated.")
        return False, None
    
    idea_filepath = str(idea_files[0])
    print(f"✓ Ideas generated and saved to: {idea_filepath}")
    return True, idea_filepath

def step2_implement_ideas(idea_filepath, selected_ids=None):
    """
    Step 2: Implement selected ideas using Manim.
    
    Args:
        idea_filepath: Path to the JSON file with ideas
        selected_ids: Specific idea IDs to implement (comma-separated string)
        
    Returns:
        tuple: (success, results)
    """
    print("\n" + "="*80)
    print("STEP 2: IMPLEMENTING IDEAS WITH MANIM")
    print("="*80)
    
    script_path = Path("manim_implementer.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, None
    
    # Build command arguments
    cmd_args = ["--file", idea_filepath]
    if selected_ids:
        cmd_args.extend(["--ids", selected_ids])
    
    # Execute implementation script
    success, stdout, stderr = run_script(script_path, *cmd_args, capture_output=False)
    
    # Parse the results from the implementation
    # The implementer outputs a summary of which ideas succeeded/failed
    # We'll need to extract the video paths for successful implementations
    
    # Find any files created in the manim_code directory during this run
    code_files = sorted(CODE_DIR.glob("*.py"), key=os.path.getmtime, reverse=True)
    
    # Find new video files created in the videos directory
    video_files = sorted(VIDEO_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    
    # Results data structure to track outcomes
    results = {
        "timestamp": datetime.now().isoformat(),
        "idea_file": idea_filepath,
        "implementations": []
    }
    
    # Print found code and video files for debugging
    print(f"Found {len(code_files)} code files and {len(video_files)} video files")
    
    # Load the original idea file to get idea details
    try:
        with open(idea_filepath, 'r') as f:
            idea_data = json.load(f)
            
        # For each idea in the file, check if it was implemented successfully
        for idea in idea_data.get('ideas', []):
            idea_id = idea.get('id')
            
            # Skip if we're only implementing specific IDs and this isn't one of them
            if selected_ids and idea_id not in selected_ids.split(','):
                continue
                
            # Find code file for this idea
            title = idea.get('title', '')
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            # Log what we're looking for
            print(f"Looking for code files containing '{safe_title}'")
            
            matching_code_files = [f for f in code_files if safe_title in str(f).lower()]
            
            # Find video files created for this idea - use more flexible matching
            # First try exact matching
            matching_videos = [v for v in video_files if safe_title in str(v).lower()]
            
            # If no exact matches, check if any videos were created during this run
            if not matching_videos and video_files:
                # Use the most recent video file as a fallback
                video_age = os.path.getmtime(video_files[0])
                current_time = time.time()
                # If the video was created in the last 5 minutes, it's likely from this run
                if current_time - video_age < 300:  # 300 seconds = 5 minutes
                    print(f"Using recently created video file: {video_files[0]}")
                    matching_videos = [video_files[0]]
            
            # Check if implementation was successful (video exists)
            success = len(matching_videos) > 0
            code_path = str(matching_code_files[0]) if matching_code_files else None
            video_path = str(matching_videos[0]) if matching_videos else None
            
            print(f"Implementation success: {success}, video path: {video_path}")
            
            results["implementations"].append({
                "id": idea_id,
                "title": title,
                "success": success,
                "code_path": code_path,
                "video_path": video_path,
                "script_path": None,  # Will be populated in step 3
                "audio_path": None    # Will be populated in steps 4-5
            })
                
    except Exception as e:
        print(f"Error parsing implementation results: {e}")
        traceback.print_exc()
    
    # Count successes
    successful = sum(1 for impl in results["implementations"] if impl["success"])
    total = len(results["implementations"])
    
    print(f"\nImplementation summary: {successful}/{total} ideas successfully implemented")
    
    # If there are video files but no successful implementations, something went wrong with the parsing
    if not successful and video_files:
        print("⚠️ Warning: Found video files but no successful implementations were detected.")
        print("This may indicate a filename mismatch or parsing issue.")
        # Force set success to True if we have videos
        forced_success = True
        print("Forcing success flag to continue the workflow...")
    else:
        forced_success = successful > 0
    
    # Return success if at least one implementation worked
    return forced_success, results

def step3_generate_voice_scripts(results):
    """
    Step 3: Generate voice scripts for each successful implementation.
    
    Args:
        results: Results dictionary from step 2
        
    Returns:
        tuple: (success, updated_results)
    """
    print("\n" + "="*80)
    print("STEP 3: GENERATING VOICE SCRIPTS")
    print("="*80)
    
    script_path = Path("voice_script_generator.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, results
    
    # Track whether any scripts were generated successfully
    any_success = False
    
    # For each successful implementation, generate a voice script
    for impl in results["implementations"]:
        if not impl["success"] or not impl["code_path"]:
            print(f"Skipping voice script for failed implementation: {impl['title']}")
            continue
            
        print(f"\nGenerating voice script for: {impl['title']}")
        code_path = impl["code_path"]
        
        # Get the idea visualization plan from the original idea file
        viz_plan = None
        try:
            with open(results["idea_file"], 'r') as f:
                idea_data = json.load(f)
                
            for idea in idea_data.get('ideas', []):
                if idea.get('id') == impl['id']:
                    viz_plan_path = str(IDEA_DIR / f"vizplan_{impl['id']}.json")
                    
                    # Save visualization plan to a temporary file
                    with open(viz_plan_path, 'w') as f:
                        json.dump({
                            "title": idea.get('title', ''),
                            "description": idea.get('description', ''),
                            "visualization_plan": idea.get('visualization_plan', '')
                        }, f, indent=2)
                        
                    viz_plan = viz_plan_path
                    break
        except Exception as e:
            print(f"Warning: Could not extract visualization plan: {e}")
        
        # Generate the script
        script_output = str(Path(code_path).parent / f"{Path(code_path).stem}_script.json")
        
        args = [code_path, "--output", script_output]
        if viz_plan:
            args.extend(["--viz-plan", viz_plan])
            
        success, stdout, stderr = run_script(script_path, *args)
        
        if success:
            impl["script_path"] = script_output
            print(f"✓ Voice script generated: {script_output}")
            any_success = True
        else:
            print(f"Failed to generate voice script for {impl['title']}")
    
    return any_success, results

def step4_generate_tts_audio(results):
    """
    Step 4: Generate TTS audio for each voice script.
    
    Args:
        results: Results dictionary from step 3
        
    Returns:
        tuple: (success, updated_results)
    """
    print("\n" + "="*80)
    print("STEP 4: GENERATING TTS AUDIO")
    print("="*80)
    
    script_path = Path("generate_tts_from_script.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, results
    
    # Track whether any audio was generated successfully
    any_success = False
    
    # For each implementation with a script, generate TTS audio
    for impl in results["implementations"]:
        if not impl["script_path"]:
            continue
            
        print(f"\nGenerating TTS audio for: {impl['title']}")
        
        # Create output directory based on implementation title
        safe_title = re.sub(r'[^\w\s-]', '', impl['title']).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        output_dir = str(TTS_DIR / safe_title)
        
        # Generate TTS audio
        success, stdout, stderr = run_script(script_path, impl["script_path"], "--output-dir", output_dir)
        
        if success:
            impl["tts_dir"] = output_dir
            print(f"✓ TTS audio generated in directory: {output_dir}")
            any_success = True
        else:
            print(f"Failed to generate TTS audio for {impl['title']}")
    
    return any_success, results

def step5_combine_audio(results):
    """
    Step 5: Combine audio segments for each implementation.
    
    Args:
        results: Results dictionary from step 4
        
    Returns:
        tuple: (success, updated_results)
    """
    print("\n" + "="*80)
    print("STEP 5: COMBINING AUDIO SEGMENTS")
    print("="*80)
    
    script_path = Path("combine_audio_segments.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, results
    
    # Track whether any audio was combined successfully
    any_success = False
    
    # For each implementation with TTS audio, combine segments
    for impl in results["implementations"]:
        if not impl.get("tts_dir"):
            continue
            
        print(f"\nCombining audio segments for: {impl['title']}")
        
        # Timing info file
        timing_info = str(Path(impl["tts_dir"]) / "timing_info.json")
        
        # Output combined audio file
        safe_title = re.sub(r'[^\w\s-]', '', impl['title']).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        combined_audio = str(Path(impl["tts_dir"]) / f"{safe_title}_voiceover.mp3")
        
        # Combine audio segments
        success, stdout, stderr = run_script(script_path, impl["tts_dir"], "--output", combined_audio, "--timing", timing_info)
        
        if success:
            impl["audio_path"] = combined_audio
            print(f"✓ Audio segments combined: {combined_audio}")
            any_success = True
        else:
            print(f"Failed to combine audio for {impl['title']}")
    
    return any_success, results

def step6_add_audio_to_video(results):
    """
    Step 6: Add audio to video for each implementation.
    
    Args:
        results: Results dictionary from step 5
        
    Returns:
        tuple: (success, updated_results)
    """
    print("\n" + "="*80)
    print("STEP 6: ADDING AUDIO TO VIDEOS")
    print("="*80)
    
    script_path = Path("add_audio_to_video_from_file.py")
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return False, results
    
    # Track whether any final videos were created successfully
    any_success = False
    
    # For each implementation with audio and video, combine them
    for impl in results["implementations"]:
        if not impl.get("audio_path") or not impl.get("video_path"):
            continue
            
        print(f"\nAdding audio to video for: {impl['title']}")
        
        # Add audio to video
        success, stdout, stderr = run_script(script_path, impl["audio_path"], "--video", impl["video_path"])
        
        # Extract the output path from stdout if available
        output_path = None
        if success and stdout:
            match = re.search(r"Final video with audio available at: (.*?)(?:\n|$)", stdout)
            if match:
                output_path = match.group(1)
        
        if success:
            impl["final_video_path"] = output_path
            print(f"✓ Final video created: {output_path}")
            any_success = True
        else:
            print(f"Failed to add audio to video for {impl['title']}")
    
    return any_success, results

def save_workflow_results(results, filepath=None):
    """Save workflow results to a JSON file for future reference."""
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"workflow_results_{timestamp}.json"
        
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nWorkflow results saved to: {filepath}")
    return filepath

def print_summary(results):
    """Print a summary of the workflow results."""
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    
    total = len(results["implementations"])
    implemented = sum(1 for impl in results["implementations"] if impl["success"])
    with_script = sum(1 for impl in results["implementations"] if impl.get("script_path"))
    with_audio = sum(1 for impl in results["implementations"] if impl.get("audio_path"))
    with_final = sum(1 for impl in results["implementations"] if impl.get("final_video_path"))
    
    print(f"Total ideas: {total}")
    print(f"Successfully implemented: {implemented}/{total}")
    print(f"With voice script: {with_script}/{implemented}")
    print(f"With audio: {with_audio}/{implemented}")
    print(f"Final videos: {with_final}/{implemented}")
    
    if with_final > 0:
        print("\nFinal videos created:")
        for impl in results["implementations"]:
            if impl.get("final_video_path"):
                print(f"- {impl['title']}: {impl['final_video_path']}")
    
    print("\nWorkflow complete!")

def run_workflow(topic, num_ideas=5, all_ideas=False, select_ids=None):
    """
    Run the complete Manim educational video workflow.
    
    Args:
        topic: Topic to generate ideas for
        num_ideas: Number of ideas to generate
        all_ideas: Whether to select all generated ideas
        select_ids: Specific idea IDs to select
        
    Returns:
        dict: Workflow results
    """
    # Check environment
    if not check_environment():
        print("Aborting workflow due to environment check failure.")
        return None
        
    # Ensure all directories exist
    ensure_dirs_exist()
    
    # Step 1: Generate ideas
    success, idea_filepath = step1_generate_ideas(topic, num_ideas, all_ideas, select_ids)
    if not success:
        print("Workflow stopped at step 1 (idea generation).")
        return None
    
    # Step 2: Implement ideas
    success, results = step2_implement_ideas(idea_filepath, select_ids)
    if not success:
        print("Workflow stopped at step 2 (implementation).")
        return results
    
    # Step 3: Generate voice scripts
    success, results = step3_generate_voice_scripts(results)
    if not success:
        print("Workflow stopped at step 3 (voice script generation).")
        return results
    
    # Step 4: Generate TTS audio
    success, results = step4_generate_tts_audio(results)
    if not success:
        print("Workflow stopped at step 4 (TTS audio generation).")
        return results
    
    # Step 5: Combine audio segments
    success, results = step5_combine_audio(results)
    if not success:
        print("Workflow stopped at step 5 (audio combination).")
        return results
    
    # Step 6: Add audio to video
    success, results = step6_add_audio_to_video(results)
    
    # Save and print results
    save_workflow_results(results)
    print_summary(results)
    
    return results

def main():
    """Main entry point for the workflow script."""
    parser = argparse.ArgumentParser(description="Manim Educational Video Workflow")
    parser.add_argument("--topic", type=str, help="Topic to generate ideas about")
    parser.add_argument("--num-ideas", type=int, default=5, help="Number of ideas to generate")
    parser.add_argument("--all", action="store_true", help="Select all generated ideas for implementation")
    parser.add_argument("--select", type=str, help="Comma-separated list of idea IDs to implement")
    
    args = parser.parse_args()
    
    # If no topic provided, ask for one
    topic = args.topic
    if not topic:
        topic = input("Enter a topic to generate ideas about: ")
    
    # Run the complete workflow
    run_workflow(topic, args.num_ideas, args.all, args.select)

if __name__ == "__main__":
    main()