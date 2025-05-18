#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
def get_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def extract_scene_code(manim_file):
    """Extract the main scene class code from a Manim file."""
    with open(manim_file, 'r') as f:
        content = f.read()
    
    # Find the scene class - typical pattern is 'class SomeName(Scene):'
    scene_pattern = r'class\s+(\w+)\s*\(\s*[A-Za-z]*Scene\s*\):'
    scene_match = re.search(scene_pattern, content)
    
    if not scene_match:
        return None, content
    
    scene_name = scene_match.group(1)
    
    # Extract the class definition
    class_pattern = fr'class\s+{scene_name}\s*\(\s*[A-Za-z]*Scene\s*\):.*?(?=\n\S)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if class_match:
        return scene_name, class_match.group(0)
    else:
        return scene_name, content

def extract_animation_segments(code):
    """Extract animation segments with timestamps from code, comments, and structure."""
    segments = []
    
    # Look for timing comments in the format "# Description: Xs-Ys: Text"
    timing_pattern = r'#\s*(\d+)-(\d+)s:\s*(.*?)$'
    
    # First look for the special comment format that indicates segment boundaries
    # This is the format used in the example: "# 0-3s: Cold-open hook"
    section_comments = re.finditer(timing_pattern, code, re.MULTILINE)
    section_timings = []
    
    for comment in section_comments:
        start_time = float(comment.group(1))
        end_time = float(comment.group(2))
        description = comment.group(3).strip()
        section_timings.append({
            "start_time": start_time, 
            "end_time": end_time,
            "duration": end_time - start_time,
            "description": description,
            "animations": []
        })
    
    # Now process the animations between these segments
    if section_timings:
        # Sort by start time
        section_timings.sort(key=lambda x: x["start_time"])
        
        # Extract all animations
        animations = re.finditer(r'self\.(?:play|wait)\((.*?)\)(?:.*?#.*?)?', code, re.DOTALL)
        
        for anim in animations:
            anim_text = anim.group(0)
            anim_content = anim.group(1)
            
            # Let's try to estimate the runtime
            runtime_match = re.search(r'run_time=(\d+(?:\.\d+)?)', anim_text)
            wait_match = re.search(r'self\.wait\((\d+(?:\.\d+)?)\)', anim_text)
            
            if runtime_match:
                runtime = float(runtime_match.group(1))
            elif wait_match:
                runtime = float(wait_match.group(1))
            else:
                # Default estimation
                runtime = 1.5
            
            # Find which section this animation belongs to
            # We can only guess based on the order in the code
            for section in section_timings:
                section["animations"].append({
                    "description": anim_content.strip(),
                    "runtime": runtime
                })
        
        # Use all the sections with timing info
        return section_timings
    
    # Fallback: if no timing comments found, try to extract based on more standard comments
    animations = []
    anim_pattern = r'self\.(?:play|wait)\((.*?)\)(?:.*?)(?:#\s*(.*?))?$'
    for match in re.finditer(anim_pattern, code, re.MULTILINE):
        anim_content = match.group(1)
        comment = match.group(2).strip() if match.group(2) else ""
        
        # Extract runtime if available
        runtime_match = re.search(r'run_time=(\d+(?:\.\d+)?)', match.group(0))
        wait_match = re.search(r'self\.wait\((\d+(?:\.\d+)?)\)', match.group(0))
        
        if runtime_match:
            runtime = float(runtime_match.group(1))
        elif wait_match:
            runtime = float(wait_match.group(1))
        else:
            runtime = 1.5  # Default
        
        animations.append({
            "content": anim_content.strip(),
            "comment": comment,
            "runtime": runtime
        })
    
    # Group animations into segments based on comments
    if animations:
        current_segment = {
            "description": "Introduction",
            "animations": [],
            "duration": 0,
            "start_time": 0
        }
        
        current_time = 0
        for anim in animations:
            # If there's a descriptive comment, this might mark a new segment
            if anim["comment"] and len(anim["comment"]) > 5:
                if current_segment["animations"]:
                    segments.append(current_segment)
                current_segment = {
                    "description": anim["comment"],
                    "animations": [],
                    "duration": 0,
                    "start_time": current_time
                }
            
            current_segment["animations"].append(anim["content"])
            current_segment["duration"] += anim["runtime"]
            current_time += anim["runtime"]
        
        # Add the last segment if it has animations
        if current_segment["animations"]:
            segments.append(current_segment)
    
    return segments

def generate_narration_script(client, manim_file, visualization_plan=None):
    """Generate a narration script that matches the animation segments."""
    scene_name, scene_code = extract_scene_code(manim_file)
    if not scene_name:
        print(f"Error: Could not identify main scene class in {manim_file}")
        return None
    
    segments = extract_animation_segments(scene_code)
    
    # Load visualization plan if provided
    viz_plan = None
    if visualization_plan:
        try:
            with open(visualization_plan, 'r') as f:
                viz_plan = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load visualization plan: {e}")
    
    # Generate script for each segment
    scripted_segments = []
    cumulative_time = 0
    
    for i, segment in enumerate(segments):
        # Prepare prompt with segment info and visualization plan context
        animations_text = ""
        if isinstance(segment['animations'], list):
            if all(isinstance(anim, dict) for anim in segment['animations']):
                # Handle the case where animations are a list of dicts
                animations_text = ', '.join([anim.get('description', str(anim)) for anim in segment['animations']])
            else:
                # Handle the case where animations are a list of strings
                animations_text = ', '.join(segment['animations'])
        
        prompt = f"""
You are writing narration for a short educational animation about {scene_name}.

For the segment starting at {segment.get('start_time', cumulative_time):.1f} seconds with duration {segment['duration']:.1f} seconds:
Description: {segment['description']}
Animations: {animations_text}

"""
        if viz_plan:
            prompt += f"""
Overall visualization plan:
{json.dumps(viz_plan, indent=2)}
"""

        prompt += """
Write a concise, engaging narration script for JUST THIS SEGMENT that explains what's happening.
The narration should:
1. Be timed to match the segment duration (aim for about 2-3 words per second)
2. Be natural and conversational in tone
3. Explain the concept being visualized clearly
4. Not describe technical details of the animation itself
5. Be cohesive with surrounding segments

Return ONLY the narration text without any additional formatting.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator who specializes in clear, engaging narration."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            narration_text = response.choices[0].message.content.strip()
            
            scripted_segments.append({
                "start_time": cumulative_time,
                "duration": segment["duration"],
                "description": segment["description"],
                "narration": narration_text
            })
            
            cumulative_time += segment["duration"]
            
        except Exception as e:
            print(f"Error generating narration for segment {i}: {e}")
            scripted_segments.append({
                "start_time": cumulative_time,
                "duration": segment["duration"],
                "description": segment["description"],
                "narration": f"[Error generating narration: {e}]"
            })
            cumulative_time += segment["duration"]
    
    return {
        "scene_name": scene_name,
        "total_duration": cumulative_time,
        "segments": scripted_segments
    }

def save_script(script, output_path):
    """Save the generated script to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(script, f, indent=2)
    print(f"Script saved to {output_path}")
    
    # Also create a text version for easier reading
    txt_path = output_path.replace('.json', '.txt')
    with open(txt_path, 'w') as f:
        f.write(f"Script for: {script['scene_name']}\n")
        f.write(f"Total Duration: {script['total_duration']:.1f} seconds\n\n")
        
        for segment in script['segments']:
            f.write(f"[{segment['start_time']:.1f}s - {segment['start_time'] + segment['duration']:.1f}s] {segment['description']}\n")
            f.write(f"{segment['narration']}\n\n")
    
    print(f"Readable script saved to {txt_path}")
    return txt_path

def main():
    parser = argparse.ArgumentParser(description="Generate a narration script for a Manim animation")
    parser.add_argument("manim_file", help="Path to the Manim Python file")
    parser.add_argument("--viz-plan", "-v", help="Path to JSON file containing the visualization plan")
    parser.add_argument("--output", "-o", help="Output path for the script JSON file")
    
    args = parser.parse_args()
    
    # Check if manim file exists
    if not os.path.exists(args.manim_file):
        print(f"Error: File not found: {args.manim_file}")
        sys.exit(1)
    
    # Set default output path
    if not args.output:
        manim_path = Path(args.manim_file)
        args.output = str(manim_path.parent / f"{manim_path.stem}_script.json")
    
    client = get_client()
    script = generate_narration_script(client, args.manim_file, args.viz_plan)
    
    if script:
        txt_path = save_script(script, args.output)
        print(f"You can now generate audio from this script using:")
        print(f"python generate_tts.py {txt_path}")

if __name__ == "__main__":
    main()