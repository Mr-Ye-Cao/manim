#!/usr/bin/env python3
"""
Manim Idea Generator

This tool helps generate educational video ideas and visualization plans using 
a two-step process:
1. Generate interesting ideas around a given topic
2. Create detailed visualization plans for selected ideas using Manim

The output is saved to a formatted file for use in later stages of the video pipeline.
"""

import os
import json
import argparse
import sys
from datetime import datetime
import textwrap
from pathlib import Path

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI Python module not installed. Install it with:")
    print("pip install openai")
    sys.exit(1)

# Set up constants
OUTPUT_DIR = Path("idea_outputs")
OPENAI_MODEL = "gpt-4o"
MAX_IDEAS = 10  # Maximum number of ideas to generate

def setup_openai_client():
    """Initialize the OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key using:")
        print("  export OPENAI_API_KEY=\"your-api-key\"")
        sys.exit(1)
    
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Make sure your API key is correct and properly formatted.")
        sys.exit(1)

def generate_ideas(client, topic, num_ideas=5):
    """
    Generate interesting educational ideas about a topic.
    
    Args:
        client: OpenAI client
        topic (str): The subject to generate ideas about
        num_ideas (int): Number of ideas to generate
        
    Returns:
        list: List of idea dictionaries {id, title, description}
    """
    prompt = f"""
    You are an expert educational content creator specialized in creating engaging 
    short-form videos (30 seconds) that help people understand complex topics.
    
    Generate {num_ideas} interesting, novel ideas for educational videos about {topic}.
    
    For each idea:
    1. Focus on a specific, concrete, and intellectually fascinating aspect of {topic}
    2. Make it visually compelling (something that benefits from animation)
    3. Ensure it can be explained in 30 seconds
    4. Target a curious, intelligent audience with basic knowledge of the subject
    5. Aim for ideas that create "aha!" moments through visualization
    
    Important: Each ID must be unique (1, 2, 3, etc.)
    
    Present each idea in JSON format like this:
    
    {{
      "id": "1",
      "title": "Clear Concise Title",
      "description": "Detailed description of the concept"
    }}
    
    Return exactly {num_ideas} ideas, each in this JSON format.
    """
    
    print(f"\nGenerating {num_ideas} educational video ideas about '{topic}'...")
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert educational content creator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    # Extract and parse the response
    ideas_text = response.choices[0].message.content
    
    # Try to parse the JSON directly
    ideas = []
    
    try:
        # Look for JSON array in the response
        import re
        import json
        
        # Try to extract a full JSON array if present
        json_array_match = re.search(r'\[\s*\{.*?\}\s*\]', ideas_text, re.DOTALL)
        if json_array_match:
            try:
                ideas = json.loads(json_array_match.group(0))
                # Validate the ideas
                valid_ideas = []
                for idea in ideas:
                    if isinstance(idea, dict) and "id" in idea and "title" in idea:
                        valid_ideas.append(idea)
                if valid_ideas:
                    ideas = valid_ideas
            except Exception as e:
                print(f"Warning: Could not parse JSON array: {e}")
        
        # If we didn't find a valid JSON array, try to find individual JSON objects
        json_matches = re.findall(r'\{[^{}]*"id"[^{}]*"title"[^{}]*"description"[^{}]*\}', ideas_text, re.DOTALL)
        
        for json_str in json_matches:
            try:
                idea = json.loads(json_str)
                if "id" in idea and "title" in idea and "description" in idea:
                    ideas.append(idea)
            except Exception as e:
                print(f"Warning: Could not parse JSON object: {e}")
    except Exception as e:
        print(f"Warning: Error parsing JSON format: {e}")
        
    # If JSON parsing failed, try to extract from text format
    if not ideas:
        print("Attempting to parse ideas from text format...")
        # Regex pattern to match numbered list items
        import re
        list_pattern = re.compile(r'(\d+)\.\s+(.*?):\s+(.*?)(?=\n\d+\.|\Z)', re.DOTALL)
        matches = list_pattern.findall(ideas_text)
        
        if matches:
            for match in matches:
                id_num = match[0]
                title = match[1].strip()
                description = match[2].strip()
                
                ideas.append({
                    "id": id_num,
                    "title": title,
                    "description": description
                })
        else:
            # Fallback to line-by-line parsing if regex doesn't work
            for line in ideas_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('- ')):
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        id_part = parts[0].strip()
                        # Extract just the number
                        id_num = ''.join(filter(str.isdigit, id_part))
                        title_part = parts[1].strip()
                        
                        # Handle cases where description is on the next line
                        description = ""
                        if ' - ' in title_part:
                            title_parts = title_part.split(' - ', 1)
                            title = title_parts[0].strip()
                            description = title_parts[1].strip()
                        else:
                            title = title_part
                        
                        ideas.append({
                            "id": id_num,
                            "title": title,
                            "description": description
                        })
    
    # If parsing didn't work well, fallback to generating structured content
    if not ideas:
        print("Reprocessing ideas into structured format...")
        
        structured_prompt = f"""
        Based on the following educational video ideas about {topic}, 
        create a structured list with id, title, and description for each idea.
        
        Original ideas:
        {ideas_text}
        
        Format each idea as:
        {{
            "id": "1",
            "title": "Clear concise title",
            "description": "Brief description of the concept and why it's interesting"
        }}
        
        Provide {num_ideas} ideas in this format.
        """
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator."},
                {"role": "user", "content": structured_prompt}
            ],
            temperature=0.5
        )
        
        try:
            result = response.choices[0].message.content
            # Extract the JSON part from the response
            start_idx = result.find('[')
            end_idx = result.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                ideas = json.loads(json_str)
            else:
                # Try to extract individual JSON objects
                import re
                json_objects = re.findall(r'{\s*"id".*?}', result, re.DOTALL)
                ideas = []
                for obj in json_objects:
                    try:
                        ideas.append(json.loads(obj))
                    except:
                        pass
        except Exception as e:
            print(f"Warning: Could not parse structured format. Using simplified approach: {e}")
            # Create simplified structure
            lines = ideas_text.split('\n')
            ideas = []
            current_id = 0
            for line in lines:
                if line.strip():
                    current_id += 1
                    ideas.append({
                        "id": str(current_id),
                        "title": line.strip(),
                        "description": ""
                    })
                    if len(ideas) >= num_ideas:
                        break
    
    return ideas

def create_visualization_plan(client, topic, selected_ideas):
    """
    Create detailed visualization plans for selected ideas.
    
    Args:
        client: OpenAI client
        topic (str): The main topic
        selected_ideas (list): List of selected idea dictionaries
        
    Returns:
        list: List of dictionaries containing ideas with visualization plans
    """
    results = []
    # Track idea IDs we've already seen
    processed_ids = set()
    
    for idea in selected_ideas:
        # Skip duplicate ideas
        if idea['id'] in processed_ids:
            continue
            
        processed_ids.add(idea['id'])
        print(f"\nDeveloping visualization plan for: {idea['title']}...")
        
        prompt = f"""
        You are a creative director for educational animations using Manim, 
        an animation engine for explanatory math videos.
        
        Create a detailed 30-second visualization plan for this educational video idea:
        
        Topic: {topic}
        Idea: {idea['title']}
        Description: {idea['description']}
        
        Your visualization plan should include:
        
        1. A scene-by-scene breakdown with timestamps (e.g., 0-3s, 3-7s, etc.)
        2. Specific Manim objects, animations, and transformations to use
        3. Color choices and visual style recommendations
        4. Text elements and how they should appear/disappear
        5. Camera movements or zooms if applicable
        6. Tips for maintaining visual clarity and engagement
        
        Create a plan that's detailed enough for a Manim programmer to implement
        but focus on creative direction rather than exact code.
        The entire animation must fit in 30 seconds and clearly communicate the concept.
        """
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a creative director for educational animations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        visualization_plan = response.choices[0].message.content
        
        # Add the visualization plan to the idea
        idea_with_plan = {
            "id": idea["id"],
            "title": idea["title"],
            "description": idea["description"],
            "visualization_plan": visualization_plan
        }
        
        results.append(idea_with_plan)
    
    return results

def display_ideas(ideas):
    """Display generated ideas in a readable format."""
    print("\n=== Generated Ideas ===\n")
    
    # Deduplicate ideas by title
    deduplicated_ideas = []
    seen_titles = set()
    
    for idea in ideas:
        if idea['title'] not in seen_titles:
            seen_titles.add(idea['title'])
            deduplicated_ideas.append(idea)
    
    # Replace the original ideas list with the deduplicated one
    ideas.clear()
    ideas.extend(deduplicated_ideas)
    
    # Ensure each idea has a unique display ID starting from 1
    for i, idea in enumerate(ideas, 1):
        # Set ID sequentially to avoid duplicates
        idea['id'] = str(i)
        
        print(f"{i}. {idea['title']}")
        if idea.get('description'):
            wrapped_desc = textwrap.fill(idea['description'], width=80, initial_indent='   ', subsequent_indent='   ')
            print(wrapped_desc)
        print()

def save_results(topic, results):
    """
    Save the visualization plans to a JSON file.
    
    Args:
        topic (str): The main topic
        results (list): List of ideas with visualization plans
        
    Returns:
        str: Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create filename based on topic and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_topic = topic.lower().replace(' ', '_')
    filename = f"{sanitized_topic}_{timestamp}.json"
    filepath = OUTPUT_DIR / filename
    
    # Save to JSON file
    output = {
        "topic": topic,
        "created_at": datetime.now().isoformat(),
        "ideas": results
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {filepath}")
    return str(filepath)

def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(description='Generate educational video ideas and visualization plans.')
    parser.add_argument('--topic', type=str, help='Topic to generate ideas about')
    parser.add_argument('--num-ideas', type=int, default=5, help=f'Number of ideas to generate (max {MAX_IDEAS})')
    parser.add_argument('--select', type=str, help='Comma-separated list of idea numbers to visualize (e.g., "1,3,5")')
    parser.add_argument('--all', action='store_true', help='Select all generated ideas for visualization')
    
    args = parser.parse_args()
    
    # Initialize OpenAI client
    client = setup_openai_client()
    
    # Ask for topic if not provided
    topic = args.topic
    if not topic:
        topic = input("Enter a topic to generate ideas about: ")
    
    # Validate number of ideas
    num_ideas = min(args.num_ideas, MAX_IDEAS)
    
    # Step 1: Generate ideas
    ideas = generate_ideas(client, topic, num_ideas)
    display_ideas(ideas)
    
    # Step 2: Select ideas for visualization planning
    selected_ideas = []
    
    # If --all flag is used, select all ideas
    if args.all:
        selected_ideas = ideas
        print(f"\nSelected all {len(selected_ideas)} ideas for visualization planning.")
    # If --select is provided, use those selections
    elif args.select:
        selected_ids = [s.strip() for s in args.select.split(',')]
        # Use a seen set to avoid duplicate selections
        seen = set()
        for idea_id in selected_ids:
            for idea in ideas:
                if idea['id'] == idea_id and idea_id not in seen:
                    selected_ideas.append(idea)
                    seen.add(idea_id)
                    break
        
        if not selected_ideas:
            print("No valid ideas selected. Please check your selection.")
            sys.exit(1)
            
        print(f"\nSelected {len(selected_ideas)} ideas for visualization planning.")
    # Otherwise, prompt for input
    else:
        while True:
            try:
                selection = input(f"\nEnter the numbers of ideas you want to visualize (comma-separated, e.g., 1,3,5): ")
                
                selected_ids = [s.strip() for s in selection.split(',')]
                # Use a seen set to avoid duplicate selections
                seen = set()
                for idea_id in selected_ids:
                    for idea in ideas:
                        if idea['id'] == idea_id and idea_id not in seen:
                            selected_ideas.append(idea)
                            seen.add(idea_id)
                            break
                
                if not selected_ideas:
                    print("No valid ideas selected. Please try again.")
                    continue
                    
                print(f"\nSelected {len(selected_ideas)} ideas for visualization planning.")
                break
            except ValueError:
                print("Invalid input. Please enter comma-separated numbers.")
            except EOFError:
                # Fallback to selecting the first idea if running in non-interactive environment
                selected_ideas = [ideas[0]]
                print(f"\nAutomatic selection: Selected idea #{selected_ideas[0]['id']} for visualization planning.")
                break
    
    # Step 3: Create visualization plans
    results = create_visualization_plan(client, topic, selected_ideas)
    
    # Step 4: Save results
    filepath = save_results(topic, results)
    
    print("\nIdea generation and visualization planning complete!")
    print(f"Results saved to: {filepath}")
    print("\nNext step: Use this output file as input for the Manim implementation stage.")

if __name__ == "__main__":
    main()