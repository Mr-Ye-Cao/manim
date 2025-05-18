# Manim Educational Video Workflow

This document describes the workflow for generating educational videos using Manim through an autonomous agent pipeline.

## Overview

The workflow consists of several steps:

1. **Idea Generation**: Generate interesting educational ideas around a topic
2. **Visualization Planning**: Create detailed plans for visualizing selected ideas
3. **Manim Implementation**: Convert visualization plans into Manim code
4. **Voice Script Generation**: Create voice scripts based on the animations
5. **Audio Generation**: Generate audio using TTS
6. **Video Production**: Combine animation and audio into final videos

## Step 1-2: Idea Generation & Visualization Planning

The `manim_idea_generator.py` script handles the first two steps of the workflow:

### Prerequisites

- Python 3.7+
- OpenAI API key
- Required packages:
  ```
  pip install openai
  ```

### Environment Setup

To securely set up your environment variables:

1. Run the setup script:
   ```
   ./setup_env.sh
   ```

2. Enter your OpenAI API key when prompted.

3. Load the environment variables:
   ```
   source .env
   ```

Alternatively, you can manually set the environment variable:
```
export OPENAI_API_KEY="your-api-key"
```

**IMPORTANT:** Never hardcode API keys in your code files. Always use environment variables or other secure methods for handling sensitive credentials.

### Usage

```bash
python manim_idea_generator.py [--topic TOPIC] [--num-ideas NUM_IDEAS] [--select SELECT] [--all]
```

Options:
- `--topic TOPIC`: The subject to generate ideas about (e.g., "black holes")
- `--num-ideas NUM_IDEAS`: Number of ideas to generate (default: 5)
- `--select SELECT`: Comma-separated list of idea numbers to visualize (e.g., "1,3,5") 
- `--all`: Select all generated ideas for visualization

If you don't provide a topic, the script will prompt you for one. If you don't provide selection options (--select or --all), the script will prompt you to choose ideas interactively.

### Workflow

1. Run the script and enter a topic (e.g., "black holes")
2. The script will generate a list of interesting educational video ideas
3. Select the ideas you want to develop (by number, comma-separated)
4. The script will create detailed visualization plans for each selected idea
5. Results are saved to the `idea_outputs/` directory as a JSON file

### Output Format

The output file includes:
- The main topic
- Timestamp of creation
- List of selected ideas
- For each idea:
  - Title and description
  - Detailed visualization plan including:
    - Scene-by-scene breakdown with timestamps
    - Manim objects and animations to use
    - Color choices and visual style
    - Text elements and animations
    - Camera movements

Example output file: `idea_outputs/black_holes_20250518_123456.json`

## Next Steps

The output from steps 1-2 will serve as input for step 3 (Manim Implementation), which will be developed next.

### Running a Sample Workflow

```bash
# Generate ideas about black holes with interactive selection
python manim_idea_generator.py --topic "black holes" --num-ideas 5

# Generate ideas and select specific ones non-interactively
python manim_idea_generator.py --topic "black holes" --num-ideas 5 --select "1,3,5"

# Generate ideas and select all of them for visualization
python manim_idea_generator.py --topic "black holes" --num-ideas 3 --all

# View the resulting JSON file in the idea_outputs directory
```

## Step 3: Manim Implementation

The `manim_implementer.py` script handles the third step of the workflow:

### Prerequisites

- Python 3.7+
- OpenAI API key
- Manim installed and configured
- Required packages:
  ```
  pip install openai
  ```

### Environment Setup

Use the same environment setup as in Step 1-2. Make sure your OpenAI API key is set:
```
source .env
```

### Usage

```bash
python manim_implementer.py [--file FILE_PATH] [--ids IDEA_IDS]
```

Options:
- `--file FILE_PATH`: Path to the idea JSON file generated in Step 1-2
- `--ids IDEA_IDS`: Comma-separated list of idea IDs to implement (e.g., "1,3,5")

If you don't provide command-line arguments, the script will run in interactive mode, allowing you to select a file and the ideas to implement.

### Workflow

1. The script loads visualization plans from the JSON file generated in Step 1-2
2. For each selected idea, it:
   - Generates Manim code based on the visualization plan
   - Saves the code to a file in the `manim_code` directory
   - Executes the code to render a video
   - If errors occur, it automatically debugs and fixes the code
   - Repeats the process until successful or maximum attempts reached
3. Finally, it provides a summary of implementation results

### Output

The implementation agent produces:
- Manim code files in the `manim_code` directory
- Rendered videos in the appropriate directory (usually `videos` or `media`)

The agent will attempt to fix errors automatically, making multiple attempts if needed.

### Running a Sample Implementation

```bash
# Interactive mode
python manim_implementer.py

# Non-interactive mode with specific file and ideas
python manim_implementer.py --file idea_outputs/black_holes_20250518_123456.json --ids 1,2
```

## Future Development

The next scripts in the pipeline will be:
- `voice_script_generator.py`: Creates voice scripts based on animations
- `video_production.py`: Manages the entire end-to-end process