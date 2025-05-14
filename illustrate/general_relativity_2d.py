from manimlib import *
import numpy as np

class GeneralRelativity2D(Scene):
    def construct(self):
        # Introduction text
        title = Text("General Relativity")
        subtitle = Text("Spacetime Curvature & Gravity")
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Set up grid to represent flat spacetime
        grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.6
            }
        )
        
        self.play(ShowCreation(grid))
        
        # Explanation of flat spacetime
        flat_text = Text("Flat Spacetime").to_edge(UP)
        self.play(Write(flat_text))
        self.wait()
        
        # Adding a massive object
        mass_text = Text("Adding Mass...").to_edge(UP)
        self.play(ReplacementTransform(flat_text, mass_text))
        
        # Draw a yellow circle representing a massive object
        massive_object = Circle(radius=0.75, color=YELLOW, fill_opacity=1)
        massive_object.move_to(ORIGIN)
        
        self.play(GrowFromCenter(massive_object))
        self.wait()
        
        # Show curved spacetime representation
        curve_text = Text("Spacetime Curves Around Mass").to_edge(UP)
        self.play(ReplacementTransform(mass_text, curve_text))
        
        # Create distorted grid to represent curved spacetime
        def curve_function(point):
            x, y, z = point
            dist = np.sqrt(x**2 + y**2)
            if dist < 0.5:  # Avoid division by zero near the center
                return point
            factor = 2 / (dist + 0.5)
            return [x, y - factor, z]
        
        curved_grid = grid.copy()
        curved_grid.apply_function(curve_function)
        
        self.play(
            ReplacementTransform(grid, curved_grid),
            run_time=2
        )
        self.wait()
        
        # Show geodesic paths (trajectories in curved spacetime)
        geodesic_text = Text("Objects Follow Curved Paths (Geodesics)").to_edge(UP)
        self.play(ReplacementTransform(curve_text, geodesic_text))
        
        # Create some geodesic paths for objects
        geodesics = []
        colors = [RED, GREEN, BLUE, PURPLE]
        
        for i, (start_x, start_y) in enumerate([(-6, 2), (-6, 1), (-6, 0), (-6, -1)]):
            # Create a path that curves toward the massive object
            path = ParametricFunction(
                lambda t: np.array([
                    start_x + 10 * t,  # Move from left to right
                    start_y - 2 * np.exp(-10 * (t - 0.5)**2) * np.sin(PI * t),  # Curved path
                    0
                ]),
                t_range=(0, 1),
                color=colors[i % len(colors)],
                stroke_width=4
            )
            geodesics.append(path)
        
        # Show geodesics
        for path in geodesics:
            self.play(ShowCreation(path), run_time=1.5)
        
        self.wait()
        
        # Explain light bending
        light_text = Text("Light Also Follows Curved Paths").to_edge(UP)
        self.play(ReplacementTransform(geodesic_text, light_text))
        
        # Create light rays
        light_rays = []
        
        for i, start_y in enumerate(np.linspace(-3, 3, 6)):
            # Create a path representing a light ray
            ray = ParametricFunction(
                lambda t: np.array([
                    -6 + 12 * t,  # Move from left to right
                    start_y - 1.8 * np.exp(-15 * (t - 0.5)**2) * np.sin(PI * t),  # Curved path
                    0
                ]),
                t_range=(0, 1),
                color=YELLOW,
                stroke_width=2,
                stroke_opacity=0.8
            )
            light_rays.append(ray)
        
        # Remove geodesics and show light rays
        self.play(*[FadeOut(path) for path in geodesics])
        
        for ray in light_rays:
            self.play(ShowCreation(ray), run_time=0.75)
        
        self.wait()
        
        # Black hole explanation
        blackhole_text = Text("Extreme Curvature: Black Holes").to_edge(UP)
        self.play(ReplacementTransform(light_text, blackhole_text))
        
        # Remove light rays
        self.play(*[FadeOut(ray) for ray in light_rays])
        
        # Make the mass bigger and black (black hole)
        black_hole = Circle(radius=1.25, color=BLACK, fill_opacity=1)
        black_hole.move_to(ORIGIN)
        
        # Event horizon
        event_horizon = Circle(radius=1.25, color=RED, fill_opacity=0, stroke_width=3)
        event_horizon.move_to(ORIGIN)
        
        self.play(
            ReplacementTransform(massive_object, black_hole),
            ShowCreation(event_horizon)
        )
        
        # Make the grid more extremely curved
        def extreme_curve_function(point):
            x, y, z = point
            dist = np.sqrt(x**2 + y**2)
            if dist < 1.0:  # Inside event horizon
                return point
            factor = 5 / (dist - 0.5)
            return [x, y - factor, z]
        
        extreme_grid = curved_grid.copy()
        extreme_grid.apply_function(extreme_curve_function)
        
        self.play(
            ReplacementTransform(curved_grid, extreme_grid),
            run_time=2
        )
        
        # Text for event horizon
        horizon_text = Text("Event Horizon", color=RED)
        horizon_text.next_to(blackhole_text, DOWN, buff=0.5)
        
        self.play(Write(horizon_text))
        
        # Light rays that get trapped in black hole
        trapped_rays = []
        escaping_rays = []
        
        # Rays that get trapped
        for angle in np.linspace(0, 2*PI, 12, endpoint=False):
            start_radius = 0.75
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            ray = ParametricFunction(
                lambda t: np.array([
                    start_x + 0.5 * t * np.cos(angle),
                    start_y + 0.5 * t * np.sin(angle),
                    0
                ]),
                t_range=(0, 1),
                color=YELLOW,
                stroke_width=2,
                stroke_opacity=0.8
            )
            trapped_rays.append(ray)
        
        # Rays that escape but are bent
        for start_y in np.linspace(-4, 4, 8):
            if abs(start_y) < 2:
                continue  # Skip rays that would go too close to the black hole
                
            ray = ParametricFunction(
                lambda t, start_y=start_y: np.array([
                    -6 + 12 * t,
                    start_y - 4 * np.exp(-8 * (t - 0.5)**2) * np.sin(PI * t),
                    0
                ]),
                t_range=(0, 1),
                color=YELLOW,
                stroke_width=2,
                stroke_opacity=0.8
            )
            escaping_rays.append(ray)
        
        # Show trapped rays
        for ray in trapped_rays:
            self.play(ShowCreation(ray), run_time=0.25)
        
        # Show escaping rays
        for ray in escaping_rays:
            self.play(ShowCreation(ray), run_time=0.5)
        
        self.wait(2)
        
        # Gravitational waves
        wave_text = Text("Gravitational Waves").to_edge(UP)
        
        self.play(
            ReplacementTransform(blackhole_text, wave_text),
            FadeOut(horizon_text),
            *[FadeOut(ray) for ray in trapped_rays + escaping_rays],
            FadeOut(black_hole),
            FadeOut(event_horizon)
        )
        
        # Reset to flat grid for gravitational waves
        flat_grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 5, 1),
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.6
            }
        )
        
        self.play(
            ReplacementTransform(extreme_grid, flat_grid),
            run_time=2
        )
        
        # Create ripple effect
        circles = []
        for radius in np.linspace(0.5, 7, 10):
            circle = Circle(radius=radius, color=BLUE, stroke_opacity=0.7 * (1 - radius/8))
            circle.move_to(ORIGIN)
            circles.append(circle)
        
        self.play(*[ShowCreation(circle) for circle in circles], run_time=2)
        
        # Animate the ripples expanding
        for _ in range(2):
            new_circles = []
            for radius in np.linspace(0.5, 7, 10):
                circle = Circle(radius=radius, color=BLUE, stroke_opacity=0.7 * (1 - radius/8))
                circle.move_to(ORIGIN)
                new_circles.append(circle)
            
            self.play(
                *[Transform(circles[i], new_circles[i]) for i in range(len(circles))],
                run_time=2
            )
        
        self.wait()
        
        # Final text
        final_text1 = Text("Spacetime tells matter how to move.")
        final_text2 = Text("Matter tells spacetime how to curve.")
        
        final_text1.to_edge(UP)
        final_text2.next_to(final_text1, DOWN)
        
        self.play(
            FadeOut(wave_text),
            Write(final_text1),
            run_time=2
        )
        
        self.play(
            Write(final_text2),
            run_time=2
        )
        
        # Attribution to John Wheeler
        quote = Text("— John Wheeler").next_to(final_text2, DOWN)
        
        self.play(Write(quote), run_time=1)
        
        self.wait(2) 