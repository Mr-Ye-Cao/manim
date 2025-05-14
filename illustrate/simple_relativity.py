from manimlib import *
import numpy as np

class SimpleRelativityVisualization(Scene):
    def construct(self):
        # Title
        title = Text("General Relativity")
        subtitle = Text("The Curvature of Spacetime")
        VGroup(title, subtitle).arrange(DOWN)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Create a grid to represent spacetime
        grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.6
            }
        )
        
        # Add grid to the scene
        self.play(ShowCreation(grid))
        
        # Text for flat spacetime
        flat_text = Text("Flat Spacetime").to_edge(UP)
        self.play(Write(flat_text))
        self.wait(1)
        
        # Create a massive object (sun)
        mass_text = Text("Adding Mass...").to_edge(UP)
        self.play(ReplacementTransform(flat_text, mass_text))
        
        massive_object = Circle(radius=0.8)
        massive_object.set_fill(YELLOW, opacity=1)
        massive_object.set_stroke(YELLOW, 3)
        massive_object.move_to(ORIGIN)
        
        self.play(GrowFromCenter(massive_object))
        self.wait(1)
        
        # Show curvature text
        curvature_text = Text("Mass Curves Spacetime").to_edge(UP)
        self.play(ReplacementTransform(mass_text, curvature_text))
        
        # Apply distortion to grid to show curvature
        def curve_function(point):
            x, y, z = point
            dist = np.sqrt(x**2 + y**2)
            if dist < 0.5:  # Avoid division by zero
                return point
            factor = 1.5 / (dist + 0.5)  # Adjust for nice curvature
            return [x, y - factor, z]
        
        # Create curved grid
        curved_grid = grid.copy()
        curved_grid.apply_function(curve_function)
        
        # Show the curvature transformation
        self.play(
            ReplacementTransform(grid, curved_grid),
            run_time=2
        )
        self.wait(1)
        
        # Orbit demonstration
        orbit_text = Text("Objects Follow Curved Paths").to_edge(UP)
        self.play(ReplacementTransform(curvature_text, orbit_text))
        
        # Draw orbit path
        orbit = Circle(radius=3, color=WHITE)
        orbit.move_to(ORIGIN)
        
        # Create a small sphere as a planet
        planet = Dot(color=BLUE, radius=0.2)
        planet.move_to(orbit.point_from_proportion(0))
        
        self.play(ShowCreation(orbit))
        self.play(FadeIn(planet))
        
        # Animate the planet orbiting
        self.play(
            MoveAlongPath(planet, orbit),
            run_time=5,
            rate_func=linear
        )
        
        self.wait(1)
        
        # Show gravitational waves
        wave_text = Text("Gravitational Waves").to_edge(UP)
        self.play(ReplacementTransform(orbit_text, wave_text))
        self.play(FadeOut(orbit), FadeOut(planet))
        
        # Create expanding circles for gravitational waves
        waves = VGroup()
        for i in range(5):
            circle = Circle(radius=0.5 + i*0.5, color=BLUE)
            circle.set_stroke(opacity=1 - i*0.2)
            waves.add(circle)
        
        waves.move_to(ORIGIN)
        self.play(ShowCreation(waves))
        
        # Animation of waves expanding
        for _ in range(3):
            new_waves = VGroup()
            for i in range(5):
                circle = Circle(radius=0.5 + i*0.5 + 0.25, color=BLUE)
                circle.set_stroke(opacity=1 - i*0.2)
                new_waves.add(circle)
            
            new_waves.move_to(ORIGIN)
            self.play(
                Transform(waves, new_waves),
                run_time=1
            )
        
        self.wait(1)
        
        # Final quote
        self.play(
            FadeOut(waves),
            FadeOut(wave_text),
            FadeOut(massive_object),
            FadeOut(curved_grid)
        )
        
        quote1 = Text("Spacetime tells matter how to move.")
        quote2 = Text("Matter tells spacetime how to curve.")
        attribution = Text("— John Wheeler", font_size=30)
        
        VGroup(quote1, quote2, attribution).arrange(DOWN, buff=0.5)
        
        self.play(Write(quote1))
        self.play(Write(quote2))
        self.play(Write(attribution))
        
        self.wait(3) 