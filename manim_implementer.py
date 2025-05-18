#!/usr/bin/env python3
"""
Manim Implementation Agent

This tool takes visualization plans from the idea generation phase and converts them
into executable Manim code. It can:

1. Read visualization plans from JSON files
2. Generate Manim code for each plan
3. Execute the code to produce videos
4. Iteratively debug and fix any errors until the video renders successfully

The implementation agent serves as step 3 in the Manim educational video pipeline.
"""

import os
import sys
import json
import argparse
import subprocess
import time
import re
import tempfile
from pathlib import Path
from datetime import datetime
import textwrap
import traceback

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI Python module not installed. Install it with:")
    print("pip install openai")
    sys.exit(1)

# Set up constants
INPUT_DIR = Path("idea_outputs")
OUTPUT_DIR = Path("manim_outputs")
CODE_DIR = Path("manim_code")
OPENAI_MODEL = "gpt-4o"
MANIM_COMMAND = "manimgl"  # Command to run manim

class ManimImplementer:
    """
    Main class for implementing Manim code from visualization plans.
    """
    
    def __init__(self, api_key=None):
        """Initialize the implementer with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Error: OpenAI API key not provided and not found in environment.")
            print("Please set the OPENAI_API_KEY environment variable.")
            sys.exit(1)
            
        self.client = OpenAI(api_key=self.api_key)
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        OUTPUT_DIR.mkdir(exist_ok=True)
        CODE_DIR.mkdir(exist_ok=True)
        
    def load_idea_file(self, filepath):
        """
        Load a JSON file containing ideas and visualization plans.
        
        Args:
            filepath (str): Path to the JSON file
            
        Returns:
            dict: The loaded data
        """
        if not os.path.exists(filepath):
            print(f"Error: File {filepath} not found.")
            return None
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Error: Could not parse JSON file {filepath}.")
            return None
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return None
    
    def list_idea_files(self):
        """
        List all available idea files in the input directory.
        
        Returns:
            list: List of file paths
        """
        if not INPUT_DIR.exists():
            print(f"Error: Input directory {INPUT_DIR} not found.")
            return []
            
        return sorted(INPUT_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    
    def generate_code(self, idea):
        """
        Generate Manim code for a given idea and visualization plan.
        
        Args:
            idea (dict): Dictionary containing idea details and visualization plan
            
        Returns:
            str: Generated Manim code
        """
        print(f"\nGenerating Manim code for: {idea['title']}")
        
        # Sanitize idea ID to be a valid Python class name
        class_name = ''.join(word.capitalize() for word in re.findall(r'\w+', idea['title']))
        if not class_name:
            class_name = f"Scene{idea['id']}"
        elif not class_name[0].isalpha():
            class_name = "Scene" + class_name
            
        prompt = f"""
        You are an expert Manim programmer tasked with creating educational animations.
        
        Please convert the following visualization plan into executable Manim code:
        
        IDEA: {idea['title']}
        DESCRIPTION: {idea['description']}
        
        VISUALIZATION PLAN:
        {idea['visualization_plan']}
        
        Create a complete Python file with the following requirements:
        
        1. Import from manimlib, not manim: use "from manimlib import *"
        2. Create a Scene class named {class_name}
        3. Implement the construct method according to the visualization plan
        4. Use precise timestamps as specified in the plan
        5. Include detailed comments explaining each section
        6. Ensure all Manim objects and animations are properly defined
        7. Pay special attention to color choices as specified in the plan
        8. Implement camera movements if mentioned in the plan
        9. Use ManimGL syntax - specifically:
           - Use ShowCreation instead of Create
           - Use FadeOut/FadeIn instead of FadeIn/FadeOut with scale parameter
           - Use self.play(Transform()) instead of self.play(x.animate)
           - Use ApplyMethod for attribute changes
        10. Make sure all animations have appropriate run_time values to match the timing in the plan
        
        The animation should be exactly 30 seconds long, matching the timestamps in the visualization plan.
        
        Return only the complete Python code, with no explanations before or after.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Manim programmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            code = response.choices[0].message.content
            
            # Extract code if wrapped in backticks
            code_pattern = re.compile(r'```python\n(.*?)```', re.DOTALL)
            matches = code_pattern.findall(code)
            if matches:
                code = matches[0]
            else:
                # Another common pattern
                code_pattern = re.compile(r'```\n(.*?)```', re.DOTALL)
                matches = code_pattern.findall(code)
                if matches:
                    code = matches[0]
            
            return code
        except Exception as e:
            print(f"Error generating code: {e}")
            return None
    
    def save_code(self, code, idea, version=1):
        """
        Save generated code to a file.
        
        Args:
            code (str): The generated code
            idea (dict): The idea dictionary
            version (int): Version number for iterative improvements
            
        Returns:
            str: Path to the saved file
        """
        # Create a filename based on the idea title
        safe_title = re.sub(r'[^\w\s-]', '', idea['title']).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        if not safe_title:
            safe_title = f"scene_{idea['id']}"
            
        filename = f"{safe_title}_v{version}.py"
        filepath = CODE_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write(code)
            
        print(f"Code saved to: {filepath}")
        return str(filepath)
    
    def execute_code(self, filepath):
        """
        Execute the Manim code to generate a video.
        
        Args:
            filepath (str): Path to the Python file
            
        Returns:
            tuple: (success, output, error_message)
        """
        # Extract class name from file
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Find class definition with 'Scene' in the inheritance
            class_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', content)
            if class_match:
                class_name = class_match.group(1)
            else:
                print("Error: Could not find Scene class in the code.")
                return False, "", "Could not find Scene class in the code."
                
            # Run Manim with the scene class
            command = [MANIM_COMMAND, filepath, class_name, "-w"]  # -w to write file
            
            print(f"\nExecuting: {' '.join(command)}")
            
            # Capture both stdout and stderr
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get output and errors
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            if exit_code == 0:
                print("\nVideo generated successfully!")
                return True, stdout, ""
            else:
                print(f"\nError running Manim (exit code {exit_code}):")
                print(stderr)
                return False, stdout, stderr
                
        except Exception as e:
            print(f"Exception during code execution: {e}")
            return False, "", str(e)
    
    def debug_and_fix(self, code, error_message, idea, attempt=1):
        """
        Debug and fix issues in the code based on error messages.
        
        Args:
            code (str): The original code
            error_message (str): Error message from Manim execution
            idea (dict): The idea dictionary
            attempt (int): The current debugging attempt number
            
        Returns:
            str: Improved code
        """
        print(f"\nDebug attempt #{attempt}: Analyzing errors and fixing code...")
        
        # First, perform some automatic detection and fixes for common ManimGL compatibility issues
        common_issues_found = []
        
        # Check for import issues
        if "from manim import" in code:
            code = code.replace("from manim import", "from manimlib import")
            common_issues_found.append("Fixed import statement from 'manim' to 'manimlib'")
            
        # Check for Create vs ShowCreation
        if "Create(" in code:
            code = code.replace("Create(", "ShowCreation(")
            common_issues_found.append("Changed 'Create' animations to 'ShowCreation'")
            
        # Check for scale parameter in FadeIn
        fade_in_scale_pattern = re.compile(r'FadeIn\s*\(\s*[\w\d_\.]+\s*,\s*scale\s*=')
        if fade_in_scale_pattern.search(code):
            code = re.sub(r'FadeIn\s*\(\s*([\w\d_\.]+)\s*,\s*scale\s*=\s*[\d\.]+\s*\)', r'FadeIn(\1)', code)
            common_issues_found.append("Removed 'scale' parameter from FadeIn animations")
            
        # Check for .animate syntax
        animate_pattern = re.compile(r'\.animate\.')
        if animate_pattern.search(code):
            common_issues_found.append("Found '.animate' syntax which needs replacement with 'ApplyMethod' or 'Transform'")
            # This is more complex to automatically fix, will let the LLM handle it
        
        # Check for specific ApplyMethod parameter passing issues
        apply_method_pattern = re.compile(r'ApplyMethod\s*\(\s*[\w\d_\.]+\.set_[\w\d_]+\s*,\s*[\w\d_=\s]+\)')
        if apply_method_pattern.search(code):
            common_issues_found.append("Found potential issues with ApplyMethod parameter passing")
            # This is more complex to automatically fix, will let the LLM handle it
        
        # Report on any fixes made
        if common_issues_found:
            print("Automatic fixes applied:")
            for issue in common_issues_found:
                print(f"- {issue}")
        
        # For more complex issues or if automatic fixes were not sufficient, use the LLM
        prompt = f"""
        You are an expert Manim programmer tasked with fixing errors in code.
        
        The following Manim code was generated to implement this animation:
        
        IDEA: {idea['title']}
        
        CODE:
        ```python
        {code}
        ```
        
        When executed, the code produced the following error:
        ```
        {error_message}
        ```
        
        Please fix the code to resolve the error. You need to understand the error message and fix compatibility issues with ManimGL.
        
        You are a debugging agent for a code generation pipeline, so you need to DIAGNOSE THE EXACT ISSUE.
        Explain your diagnosis and reasoning step by step, and then provide the fixed code.
        
        Common issues to look for:
        
        1. Import statement: MUST use "from manimlib import *" not "from manim import *"
        
        2. Animation compatibility:
           - ManimGL uses ShowCreation instead of Create
           - FadeIn/FadeOut in ManimGL doesn't accept scale parameter
           - ManimGL doesn't support the ".animate" syntax; use Transform or ApplyMethod instead
        
        3. ApplyMethod syntax:
           - Incorrect: ApplyMethod(obj.set_stroke, width=6)
           - Correct: Use Transform with an explicit copy: 
             ```python
             new_obj = obj.copy().set_stroke(width=6)
             self.play(Transform(obj, new_obj))
             ```
        
        4. For camera movement:
           - Incorrect: self.play(self.camera.frame.animate.scale(0.8))
           - Correct: self.play(ApplyMethod(self.camera.frame.scale, 0.8))
        
        Your diagnosis and fix should be comprehensive. Address ALL issues, not just the first one you find.
        
        Format your response as:
        
        DIAGNOSIS:
        Explanation of what went wrong and why...
        
        SOLUTION:
        Explanation of the changes made...
        
        FIXED CODE:
        ```python
        # Complete fixed code here
        ```
        """
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Manim programmer specializing in debugging."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            
            # Extract diagnosis and explanation
            diagnosis_match = re.search(r'DIAGNOSIS:(.*?)(?:SOLUTION:|FIXED CODE:)', result, re.DOTALL)
            if diagnosis_match:
                diagnosis = diagnosis_match.group(1).strip()
                print("\nDiagnosis:")
                print(textwrap.fill(diagnosis, width=80))
            
            solution_match = re.search(r'SOLUTION:(.*?)(?:FIXED CODE:)', result, re.DOTALL)
            if solution_match:
                solution = solution_match.group(1).strip()
                print("\nSolution:")
                print(textwrap.fill(solution, width=80))
            
            # Extract code
            code_pattern = re.compile(r'```python\n(.*?)```', re.DOTALL)
            matches = code_pattern.findall(result)
            if matches:
                fixed_code = matches[0]
                print("\nFixed code extracted.")
                return fixed_code
            else:
                # Try another common pattern
                code_pattern = re.compile(r'FIXED CODE:\s*```(?:python)?\n(.*?)```', re.DOTALL)
                matches = code_pattern.findall(result)
                if matches:
                    fixed_code = matches[0]
                    print("\nFixed code extracted.")
                    return fixed_code
                else:
                    print("Could not extract fixed code. Using original code with automatic fixes.")
                    return code
        except Exception as e:
            print(f"Error fixing code: {e}")
            return code  # Return original code if fixing fails
    
    def implement_idea(self, idea, max_attempts=5):
        """
        Implement a single idea: generate code, execute, debug if needed.
        
        Args:
            idea (dict): The idea to implement
            max_attempts (int): Maximum number of debug attempts
            
        Returns:
            tuple: (success, code_file_path, video_file_path)
        """
        # Generate initial code
        code = self.generate_code(idea)
        if not code:
            return False, None, None
            
        # Save initial code
        code_path = self.save_code(code, idea, version=1)
        
        # Execute code
        success, output, error = self.execute_code(code_path)
        
        # If successful, we're done
        if success:
            # Extract the output video path from manim output
            video_path_match = re.search(r'File ready at (.*?)(\.mp4|\.mov)', output)
            video_path = video_path_match.group(0) if video_path_match else None
            return True, code_path, video_path
            
        # If not successful, attempt to debug and fix
        attempt = 1
        while not success and attempt < max_attempts:
            attempt += 1
            
            # Debug and fix code
            fixed_code = self.debug_and_fix(code, error, idea, attempt)
            
            # If the code didn't change, no point in trying again
            if fixed_code == code:
                print("No improvements made to the code. Stopping debug attempts.")
                break
                
            code = fixed_code
            code_path = self.save_code(code, idea, version=attempt)
            
            # Execute fixed code
            success, output, error = self.execute_code(code_path)
            
            if success:
                # Extract the output video path
                video_path_match = re.search(r'File ready at (.*?)(\.mp4|\.mov)', output)
                video_path = video_path_match.group(0) if video_path_match else None
                return True, code_path, video_path
        
        # If we reached the maximum attempts without success
        if not success:
            print(f"\nFailed to implement {idea['title']} after {max_attempts} attempts.")
            
        return success, code_path, None
        
    def implement_ideas_from_file(self, filepath, selected_ids=None):
        """
        Implement all or selected ideas from a file.
        
        Args:
            filepath (str): Path to the JSON file
            selected_ids (list): List of idea IDs to implement, or None for all
            
        Returns:
            dict: Results of implementation
        """
        # Load the file
        data = self.load_idea_file(filepath)
        if not data:
            return None
            
        ideas = data.get('ideas', [])
        if not ideas:
            print("No ideas found in the file.")
            return None
            
        # Filter ideas if specific IDs are provided
        if selected_ids:
            ideas = [idea for idea in ideas if idea.get('id') in selected_ids]
            if not ideas:
                print(f"No ideas found with IDs: {', '.join(selected_ids)}")
                return None
                
        # Implement each idea
        results = []
        for idea in ideas:
            print(f"\n{'='*40}")
            print(f"Implementing idea: {idea['title']}")
            print(f"{'='*40}")
            
            success, code_path, video_path = self.implement_idea(idea)
            
            results.append({
                'id': idea['id'],
                'title': idea['title'],
                'success': success,
                'code_path': code_path,
                'video_path': video_path
            })
            
        # Create a summary
        success_count = sum(1 for r in results if r['success'])
        print(f"\n{'='*40}")
        print(f"Implementation complete: {success_count}/{len(results)} ideas successfully implemented")
        print(f"{'='*40}")
        
        # Print detailed results
        for r in results:
            status = "SUCCESS" if r['success'] else "FAILED"
            print(f"{r['id']}. {r['title']} - {status}")
            if r['code_path']:
                print(f"   Code: {r['code_path']}")
            if r['video_path']:
                print(f"   Video: {r['video_path']}")
                
        return {
            'topic': data.get('topic', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'results': results
        }


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(description='Implement Manim animations from visualization plans.')
    parser.add_argument('--file', type=str, help='Path to the idea JSON file')
    parser.add_argument('--ids', type=str, help='Comma-separated list of idea IDs to implement')
    
    args = parser.parse_args()
    
    # Initialize implementer
    implementer = ManimImplementer()
    
    if args.file:
        # Implement from specified file
        filepath = args.file
        selected_ids = args.ids.split(',') if args.ids else None
    else:
        # Interactive mode: list available files and let user choose
        files = implementer.list_idea_files()
        
        if not files:
            print("No idea files found. Please run the idea generator first.")
            return
            
        print("\nAvailable idea files:")
        for i, f in enumerate(files, 1):
            print(f"{i}. {f.name}")
            
        while True:
            try:
                selection = input("\nSelect a file number: ")
                file_idx = int(selection) - 1
                
                if 0 <= file_idx < len(files):
                    filepath = str(files[file_idx])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(files)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Load the selected file and show ideas
        data = implementer.load_idea_file(filepath)
        if not data or 'ideas' not in data:
            print("Invalid idea file.")
            return
            
        print("\nIdeas in this file:")
        for idea in data['ideas']:
            print(f"{idea['id']}. {idea['title']}")
            
        while True:
            try:
                selection = input("\nEnter the IDs of ideas to implement (comma-separated), or 'all' for all ideas: ")
                
                if selection.lower() == 'all':
                    selected_ids = None
                    break
                else:
                    selected_ids = [s.strip() for s in selection.split(',')]
                    break
            except ValueError:
                print("Invalid input. Please enter comma-separated IDs or 'all'.")
    
    # Implement the selected ideas
    implementer.implement_ideas_from_file(filepath, selected_ids)


if __name__ == "__main__":
    main()