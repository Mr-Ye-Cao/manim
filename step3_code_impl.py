#!/usr/bin/env python3
"""
CLI tool for pipeline step 3: implement ideas as Manim scenes.
1) Read topic, ideas, and plans from step1_and_2_output.json
2) For each idea, generate a Manim Python script via OpenAI
3) Render the scene using Manim (manimlib) in HD, writing output files
4) If rendering errors occur, ask OpenAI to fix the code and retry (up to max retries)
5) Save all rendered video paths and metadata to step3_output.json
"""
import os
import sys
import json
import subprocess
import argparse
import re
from openai import OpenAI


def strip_code(text: str) -> str:
    """Remove Markdown code fences if present"""
    pattern = r"```(?:python)?\n([\s\S]*?)```"
    m = re.search(pattern, text)
    return m.group(1) if m else text


def generate_scene_code(client, class_name: str, plan: str) -> str:
    system_prompt = "You are an expert Manim programmer using the manimlib library."
    user_prompt = (
        f"Write a complete Python script for Manim (using manimlib) that defines a class {class_name}(Scene) "
        f"implementing the following high-level plan:\n\n{plan}\n\n"
        "The script should start with 'from manimlib import *', define the class with a 'construct' method, "
        "and produce a 30-second animation. Do not include any comments or extraneous text, only the full code."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return strip_code(resp.choices[0].message.content)


def fix_scene_code(client, class_name: str, plan: str, error: str) -> str:
    system_prompt = "You are a helpful Python coding assistant specializing in Manim animations."
    user_prompt = (
        f"The following Manim scene class {class_name} is intended to implement this plan:\n\n{plan}\n\n"
        f"However, rendering it produced this error:\n```\n{error}\n```\n"
        "Please provide the complete corrected script code only, without additional commentary."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return strip_code(resp.choices[0].message.content)


def render_scene(script_path: str, class_name: str) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable, "-m", "manimlib",
        script_path, class_name,
        "-w",     # write to file
        "--hd",  # 1080p
        "--quiet",  # suppress logs
        "--file_name", class_name.lower(),
    ]
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    # Self-diagnose and install missing pkg_resources dependency
    try:
        import pkg_resources  # noqa: F401
    except ImportError:
        print("Detected missing pkg_resources; installing setuptools...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "setuptools", "--break-system-packages"],
            check=True
        )
        print("setuptools installed successfully.")
    # Automatically install all project dependencies
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print(f"Installing dependencies from {req_file}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", req_file, "--break-system-packages"
        ], check=True)
        print("Project dependencies installed successfully.")
    parser = argparse.ArgumentParser(
        description="Step 3: Generate and render Manim scenes for ideas."
    )
    parser.add_argument(
        "-i", "--input",
        default="step1_and_2_output.json",
        help="Path to JSON output from step 1 and 2."
    )
    parser.add_argument(
        "-r", "--max-retries",
        type=int,
        default=3,
        help="Maximum retries for auto-correction when errors occur."
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    if not os.path.exists(args.input):
        print(f"Error: input file '{args.input}' not found.")
        sys.exit(1)
    data = json.load(open(args.input))
    topic = data.get("topic")
    items = data.get("items", [])
    os.makedirs("step3_scenes", exist_ok=True)

    results = []
    for item in items:
        idx = item.get("id")
        idea = item.get("idea")
        plan = item.get("plan")
        class_name = f"Idea{idx}Scene"
        script_path = os.path.join("step3_scenes", f"scene_{idx}.py")

        print(f"\n=== Processing Idea {idx}: {idea} ===")
        # 1) Generate initial code
        code = generate_scene_code(client, class_name, plan)
        with open(script_path, "w") as f:
            f.write(code)

        # 2) Attempt to render, auto-correct on error
        last_error = None
        for attempt in range(1, args.max_retries + 1):
            print(f"Attempt {attempt} to render {class_name}...")
            proc = render_scene(script_path, class_name)
            if proc.returncode == 0:
                print(f"{class_name} rendered successfully.")
                video_path = os.path.abspath(os.path.join(
                    "videos", f"{class_name.lower()}.mp4"
                ))
                results.append({
                    "id": idx,
                    "idea": idea,
                    "plan": plan,
                    "scene_file": script_path,
                    "video_path": video_path,
                })
                break
            else:
                error_msg = proc.stderr
                print(f"Error rendering {class_name}: {error_msg}")
                last_error = error_msg
                # Local self-diagnosis: fix wrong import from 'manim' to 'manimlib'
                if "No module named 'manim'" in error_msg and attempt < args.max_retries:
                    print("Detected wrong import. Fixing import statement...")
                    with open(script_path) as f:
                        code_text = f.read()
                    code_text = code_text.replace("from manim import *", "from manimlib import *")
                    with open(script_path, "w") as f:
                        f.write(code_text)
                    continue
                # Local self-diagnosis: add missing color constant import
                if "NameError: name 'BROWN'" in error_msg and attempt < args.max_retries:
                    print("Detected missing color import. Adding import for BROWN...")
                    lines = []
                    with open(script_path) as f:
                        for line in f:
                            lines.append(line)
                            if line.strip() == "from manimlib import *":
                                lines.append("from manimlib.constants import BROWN\n")
                    with open(script_path, "w") as f:
                        f.write("".join(lines))
                    continue
                # Local self-diagnosis: remove invalid camera method calls
                if "has no attribute 'set_background_color'" in error_msg and attempt < args.max_retries:
                    print("Detected invalid camera method; commenting out set_background_color calls...")
                    lines = []
                    with open(script_path) as f:
                        for line in f:
                            if '.set_background_color' in line:
                                lines.append(f"# {line}")
                            else:
                                lines.append(line)
                    with open(script_path, "w") as f:
                        f.write("".join(lines))
                    continue
                # Local self-diagnosis: remove missing asset references
                if "not Found" in error_msg and attempt < args.max_retries:
                    # Match the OSError line to extract the missing asset filename
                    m = re.search(r'OSError: ([^\s]+\.(?:jpg|jpeg|png|gif)) not Found', error_msg)
                    if m:
                        asset = m.group(1)
                        print(f"Detected missing asset {asset}; removing its usage...")
                        lines = []
                        with open(script_path) as f:
                            for line in f:
                                if asset in line and 'ImageMobject' in line:
                                    # comment out image usage and add placeholder
                                    lines.append(f"# {line}")
                                    lines.append("    # Placeholder for missing image asset\n    placeholder = Dot()\n    self.add(placeholder)\n")
                                else:
                                    lines.append(line)
                        with open(script_path, "w") as f:
                            f.write("".join(lines))
                        continue
                if attempt < args.max_retries:
                    print("Requesting code fix from OpenAI...")
                    code = fix_scene_code(client, class_name, plan, error_msg)
                    with open(script_path, "w") as f:
                        f.write(code)
                else:
                    print(f"Failed to render {class_name} after {args.max_retries} attempts.")
        # end attempts

    # end items loop

    output = {"topic": topic, "results": results}
    out_file = "step3_output.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nAll done. Summary saved to {out_file}.")


if __name__ == '__main__':
    main() 