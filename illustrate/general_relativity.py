from manimlib import *
import numpy as np

class GeneralRelativityVisualization(ThreeDScene):
    def construct(self):
        # Introduction text
        title = Text("General Relativity", font_size=60)
        subtitle = Text("Spacetime Curvature & Gravity", font_size=40)
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Set up 3D grid to represent spacetime
        grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-8, 8, 1),
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.6
            },
            axis_config={"stroke_opacity": 0},
        )
        grid.set_opacity(0.5)
        self.play(ShowCreation(grid))
        
        # Explanation of flat spacetime
        flat_text = Text("Flat Spacetime", font_size=36).to_edge(UP)
        self.play(Write(flat_text))
        self.wait()
        
        # Adding a small mass to curve spacetime
        mass_text = Text("Adding Mass...", font_size=36).to_edge(UP)
        self.play(ReplacementTransform(flat_text, mass_text))
        
        # Create a sphere to represent a massive object
        sphere = Sphere(radius=0.8, resolution=(20, 20))
        sphere.set_color(YELLOW)
        sphere.move_to(ORIGIN)
        
        self.play(GrowFromCenter(sphere))
        self.wait()
        
        # Define a function to curve the grid
        def curved_grid_function(point):
            x, y, z = point
            dist = np.sqrt(x**2 + y**2)
            factor = 5 / (1 + dist**2/5)
            return [x, y, -factor]
        
        # Skip the curved grid animation that's causing issues
        # and move directly to the parametric surface
        
        # Create a curved surface to represent curved spacetime
        resolution = 20
        curved_surface = ParametricSurface(
            lambda u, v: np.array([
                u,
                v,
                -2 / (1 + (u**2 + v**2)/3)
            ]),
            u_range=(-5, 5),
            v_range=(-5, 5),
            resolution=(resolution, resolution),
            stroke_width=0.5,
            stroke_opacity=0.5,
        )
        curved_surface.set_color(BLUE_D)
        
        # Add new text explaining spacetime curvature
        curve_text = Text("Spacetime Curves Around Mass", font_size=36).to_edge(UP)
        
        # Set specific camera orientation for 3D scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.02)
        
        self.play(
            ReplacementTransform(mass_text, curve_text),
            FadeOut(grid),
            FadeIn(curved_surface),
            run_time=2
        )
        
        # Add a small sphere to represent a planet or probe
        planet = Sphere(radius=0.2)
        planet.set_color(BLUE)
        planet.move_to([-4, 0, curved_surface.point_from_proportion(0.25)[2]])
        
        # Path of the planet around the central mass
        orbit_path = ParametricFunction(
            lambda t: np.array([
                4 * np.cos(t),
                4 * np.sin(t),
                curved_surface.func(4 * np.cos(t), 4 * np.sin(t))[2]
            ]),
            t_range=(0, 2*PI),
            color=WHITE,
            stroke_width=2,
        )
        
        # Add text explaining orbital paths
        orbit_text = Text("Objects Follow Geodesics in Curved Spacetime", font_size=36).to_edge(UP)
        
        self.play(
            ReplacementTransform(curve_text, orbit_text),
            ShowCreation(orbit_path),
            FadeIn(planet),
        )
        
        # Animate the planet following the orbital path
        self.play(
            MoveAlongPath(planet, orbit_path),
            run_time=6,
            rate_func=linear,
        )
        
        # Add light paths bending around the mass
        light_text = Text("Light Also Follows Curved Paths", font_size=36).to_edge(UP)
        
        # Create light paths that bend around the mass
        light_paths = []
        for offset in [-3, -2, -1, 0, 1, 2, 3]:
            light_path = ParametricFunction(
                lambda t: np.array([
                    t,
                    offset + 0.5 * t**2 / (10 + abs(offset)),
                    curved_surface.func(t, offset + 0.5 * t**2 / (10 + abs(offset)))[2] + 0.1
                ]),
                t_range=(-5, 5),
                color=YELLOW,
                stroke_width=2,
                stroke_opacity=0.8,
            )
            light_paths.append(light_path)
        
        self.play(
            ReplacementTransform(orbit_text, light_text),
            FadeOut(planet),
            FadeOut(orbit_path),
            *[ShowCreation(path) for path in light_paths],
            run_time=3,
        )
        
        self.wait(2)
        
        # Transition to black hole
        blackhole_text = Text("Extreme Curvature: Black Holes", font_size=36).to_edge(UP)
        
        self.play(
            ReplacementTransform(light_text, blackhole_text),
            *[FadeOut(path) for path in light_paths],
            run_time=2
        )
        
        # Create a more extreme curvature surface for black hole
        blackhole_surface = ParametricSurface(
            lambda u, v: np.array([
                u,
                v,
                -6 / (0.2 + (u**2 + v**2)/2)
            ]),
            u_range=(-5, 5),
            v_range=(-5, 5),
            resolution=(resolution, resolution),
            stroke_width=0.5,
            stroke_opacity=0.5,
        )
        blackhole_surface.set_color(BLUE_E)
        
        # Create event horizon circle
        event_horizon = Circle(radius=1.5, color=RED)
        event_horizon.rotate(PI/2, RIGHT)
        event_horizon.move_to([0, 0, -3])
        
        # Black hole sphere (singularity)
        black_sphere = Sphere(radius=0.5)
        black_sphere.set_color(BLACK)
        black_sphere.move_to(ORIGIN)
        
        self.play(
            ReplacementTransform(curved_surface, blackhole_surface),
            ReplacementTransform(sphere, black_sphere),
            ShowCreation(event_horizon),
            run_time=3
        )
        
        # Text for event horizon
        horizon_text = Text("Event Horizon", font_size=30, color=RED)
        horizon_text.next_to(blackhole_text, DOWN, buff=0.5)
        
        self.play(Write(horizon_text))
        
        # Light cannot escape from inside event horizon
        trapped_light_paths = []
        for angle in np.linspace(0, 2*PI, 12, endpoint=False):
            start_radius = 0.8
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            path = ParametricFunction(
                lambda t: np.array([
                    start_x * (1 - t/2),
                    start_y * (1 - t/2),
                    -3 + t/5
                ]),
                t_range=(0, 1.5),
                color=YELLOW,
                stroke_width=2,
                stroke_opacity=0.8,
            )
            trapped_light_paths.append(path)
        
        self.play(
            *[ShowCreation(path) for path in trapped_light_paths],
            run_time=2
        )
        
        self.wait(2)
        
        # Transition to gravitational waves
        wave_text = Text("Gravitational Waves", font_size=36).to_edge(UP)
        
        self.play(
            ReplacementTransform(blackhole_text, wave_text),
            FadeOut(horizon_text),
            *[FadeOut(path) for path in trapped_light_paths],
            FadeOut(event_horizon),
            FadeOut(black_sphere),
            run_time=2
        )
        
        # Create a flat grid again for gravitational waves
        wave_grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-8, 8, 1),
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.6
            },
            axis_config={"stroke_opacity": 0},
        )
        wave_grid.set_opacity(0.5)
        wave_grid.rotate(PI/2, RIGHT)
        
        self.play(
            FadeOut(blackhole_surface),
            FadeIn(wave_grid),
            run_time=2
        )
        
        # Function to create gravitational wave effect
        def wave_function(t):
            def func(point):
                x, y, z = point
                dist = np.sqrt(x**2 + y**2)
                if 2 < dist < 8:
                    # Create an expanding ripple
                    amplitude = 0.2 * np.exp(-0.2 * (dist - 5 - t)**2)
                    return [x, y, amplitude * np.sin(dist - t)]
                return point
            return func
        
        # Simplify the gravitational wave animation to avoid errors
        ripple_grid = wave_grid.copy()
        self.add(ripple_grid)
        
        ripple1 = ripple_grid.copy()
        ripple1.apply_function(wave_function(0))
        
        ripple2 = ripple_grid.copy()
        ripple2.apply_function(wave_function(2))
        
        ripple3 = ripple_grid.copy()
        ripple3.apply_function(wave_function(4))
        
        self.play(
            Transform(ripple_grid, ripple1),
            run_time=2
        )
        
        self.play(
            Transform(ripple_grid, ripple2),
            run_time=2
        )
        
        self.play(
            Transform(ripple_grid, ripple3),
            run_time=2
        )
            
        # Final text
        final_text1 = Text("Spacetime tells matter how to move.", font_size=36)
        final_text2 = Text("Matter tells spacetime how to curve.", font_size=36)
        
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
        
        self.wait(3)
        
        # Stop camera rotation and reset view for final message
        self.stop_ambient_camera_rotation()
        
        quote = Text(
            "— John Wheeler",
            font_size=28
        ).next_to(final_text2, DOWN)
        
        self.play(
            Write(quote),
            run_time=1
        )
        
        self.wait(2) 