import openai
import os
from openai import OpenAI

# Create output directory if it doesn't exist
os.makedirs("tts_output", exist_ok=True)

# Configure OpenAI client - Note: API key should be set as environment variable
client = OpenAI(
    api_key="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"
)

# Define the script sections
script_sections = [
    # Cold-open
    "Can a smooth curve be born from nothing but straight-line clues? Watch this spark.",
    
    # Title card
    "Building sin x — the Taylor story.",
    "Sit back and enjoy a waltz between curves and polynomials.",
    
    # Setup world
    "First, we raise the stage: a set of axes and the sine curve taking center spotlight.",
    "That yellow dot at x = 0 is our expansion anchor.",
    "On the right, a parking lane for formulas; bottom left, a dashboard that tracks which derivatives we've nailed.",
    
    # Term-by-term showcase - Degree 0
    "Meet the Flat Friend—the laziest guess of all.",
    "Knowing only the function's value, it flattens the world into a zero-height horizon.",
    
    # Degree 1
    "Enter the Tangent Teen! Armed with slope, he tilts that horizon into a daring straight line.",
    "Under the microscope he hugs sin x at the origin, but wander away and the error balloons.",
    
    # Degree 2
    "Third up is the Parabola Plumber. Sadly, for sin x his coefficient is zero—he digs a trench no one can see.",
    
    # Degree 3
    "Here comes the Cubic Climber, carving the familiar S-shape into our approximation.",
    "Notice the inflection arrows tugging the curve into form.",
    
    # Degree 4
    "Next is the Fourth-order Phantom. Math declares this term zero as well—blink and he's gone.",
    
    # Degree 5
    "Finally, the Fifth-order Fixer sprinkles a subtle wave on top.",
    "See that red error ribbon shrink as he works his polish.",
    "Green bars in the dashboard show the derivatives we now match; red ones still wait their turn.",
    
    # Speed-run montage
    "Now, fast-forward.",
    "Seventh, ninth… each extra term slices the error thinner and whispers of infinity.",
    "And so, sin x blossoms from an endless stack of straight-line truths.",
    
    # Real-world application
    "Don't leave yet! On the right-hand lab bench, engineers steal a truncated Taylor to model a small-angle pendulum.",
    "For tiny swings, stopping after the first nonlinear term still nails the period: T ≈ 2 π √(L / g).",
    "Industry signs off here, and the approximation just works.",
    
    # Closing sequence
    "Big curves, built from small truths.",
    "Next time you admire a smooth silhouette—waves, orbits, even sound—remember the quiet choir of ordinary lines beneath it.",
    "Thanks for watching. See you in the next exploration!"
]

# Generate TTS for each section
for i, text in enumerate(script_sections):
    print(f"Generating audio for section {i+1}/{len(script_sections)}: {text[:30]}...")
    
    try:
        # Use the GPT-4o mini TTS capability
        response = client.audio.speech.create(
            model="tts-1-hd",  # Using high-definition quality
            voice="onyx",   # Using Onyx voice which is good for educational content
            input=text
        )
        
        # Save audio file
        filename = f"tts_output/section_{i+1:02d}.mp3"
        response.stream_to_file(filename)
        print(f"Saved to {filename}")
        
    except Exception as e:
        print(f"Error generating audio for section {i+1}: {e}")

print("All audio files generated!")

# Create a file with all the text segments for reference
with open("tts_output/script.txt", "w") as f:
    for i, text in enumerate(script_sections):
        f.write(f"Section {i+1}: {text}\n\n")

print("Script text file saved to tts_output/script.txt") 