#!/usr/bin/env python3
"""
CLI tool for pipeline steps 1 and 2:
1) Prompt user for a topic
2) Generate 5 educational visualization ideas via OpenAI
3) Let user select ideas
4) Generate a high-level director plan for each selected idea
5) Save topic, ideas, and plans to a JSON file for later steps
"""
import os
import sys
import json
import re
from openai import OpenAI


def main():
    # Configure API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    # Step 1: Topic input
    topic = input("Enter a topic to generate ideas for: ").strip()
    if not topic:
        print("Error: topic cannot be empty.")
        sys.exit(1)

    # Generate 5 visualization ideas
    system_prompt = (
        "You are an assistant that suggests concise, novel, and engaging educational video ideas "
        "for teaching a topic through visualization. Given a topic, output 5 distinct ideas, each numbered."
    )
    user_prompt = (
        f"Generate 5 short, novel, and interesting ideas for educational videos about '{topic}'. "
        "Each idea should be 1-2 sentences and clearly distinct. Number them 1 to 5."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        ideas_text = response.choices[0].message.content
    except Exception as e:
        print(f"Error generating ideas: {e}")
        sys.exit(1)

    print("\nGenerated Ideas:\n")
    print(ideas_text)

    # Parse ideas into a dict
    ideas = {}
    for line in ideas_text.splitlines():
        m = re.match(r"^\s*(\d+)[\)\.\-]\s*(.+)", line)
        if m:
            idx = int(m.group(1))
            ideas[idx] = m.group(2).strip()

    if not ideas:
        print("Failed to parse ideas. Exiting.")
        sys.exit(1)

    # User selects ideas
    sel = input("\nEnter idea numbers to select (e.g. 1,3): ").strip()
    selected = []
    for part in sel.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part)
            if idx in ideas:
                selected.append(idx)
    if not selected:
        print("No valid selection. Exiting.")
        sys.exit(1)

    # Step 2: Director plan for each selected idea
    results = []
    for idx in selected:
        idea_text = ideas[idx]
        print(f"\nGenerating plan for idea {idx}: {idea_text}\n")
        plan_prompt = (
            f"You are a talented animation director. Create a concise, high-level plan to "
            f"illustrate the following idea visually in a 30-second educational video: '{idea_text}'. "
            "Use bullet points or numbered steps."
        )
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a talented animation director."},
                    {"role": "user", "content": plan_prompt},
                ],
                temperature=0.7,
            )
            plan_text = resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating plan for idea {idx}: {e}")
            sys.exit(1)

        print(f"Plan for idea {idx}:\n{plan_text}\n")
        results.append({"id": idx, "idea": idea_text, "plan": plan_text})

    # Save all results
    output = {"topic": topic, "items": results}
    out_file = "step1_and_2_output.json"
    try:
        with open(out_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved ideas and plans to {out_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 