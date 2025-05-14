from manimlib import *
import numpy as np

class EnhancedRelativityVisualization(Scene):
    def construct(self):
        # Title sequence
        title = Text("General Relativity", font_size=60)
        subtitle = Text("Einstein's Revolutionary Theory of Gravity", font_size=36)
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(subtitle))
        self.wait(2)
        
        # Einstein's image
        einstein_quote = Text("\"Gravity is not a force...\nit is a consequence of spacetime curvature\"", 
                            font_size=32)
        einstein_quote.to_edge(DOWN, buff=1)
        self.play(Write(einstein_quote))
        self.wait(2)
        
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(einstein_quote))
        
        # Part 1: Newtonian Gravity vs General Relativity
        section_title = Text("Part 1: From Newton to Einstein", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        # Newtonian explanation
        newton_title = Text("Newtonian Gravity", font_size=40)
        newton_title.to_edge(UP)
        self.play(Write(newton_title))
        
        # Create objects for Newtonian gravity demonstration
        sun = Circle(radius=0.8)
        sun.set_fill(YELLOW, opacity=1)
        sun.set_stroke(YELLOW, 3)
        sun.move_to(ORIGIN)
        
        earth = Circle(radius=0.3)
        earth.set_fill(BLUE, opacity=1)
        earth.set_stroke(BLUE_E, 2)
        earth.move_to([3, 0, 0])
        
        # Force arrow
        arrow = Arrow(earth.get_center(), sun.get_center(), buff=0.3, color=RED)
        force_text = Text("Gravitational Force", font_size=24, color=RED)
        force_text.next_to(arrow, UP)
        
        self.play(FadeIn(sun))
        self.play(FadeIn(earth))
        self.play(GrowArrow(arrow), Write(force_text))
        
        newton_eq = Tex("F = G\\frac{m_1 m_2}{r^2}", font_size=36)
        newton_eq.to_corner(UR)
        self.play(Write(newton_eq))
        
        newton_explain = Text("Newton: Objects attract each other with\na force proportional to their masses\nand inversely proportional to distance squared.", 
                             font_size=24).to_edge(DOWN)
        self.play(Write(newton_explain))
        
        self.wait(2)
        
        # Transition to Einstein
        self.play(
            FadeOut(newton_explain), 
            FadeOut(arrow), 
            FadeOut(force_text),
            FadeOut(newton_eq),
            FadeOut(earth)
        )
        
        einstein_title = Text("Einstein's Revolution", font_size=40)
        self.play(ReplacementTransform(newton_title, einstein_title))
        
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
        
        self.play(ShowCreation(grid))
        
        einstein_explain = Text("Einstein: Mass and energy curve spacetime.\nObjects follow the straightest possible path\nthrough curved spacetime.", 
                              font_size=24).to_edge(DOWN)
        self.play(Write(einstein_explain))
        
        # Show the sun curving spacetime
        self.wait(1)
        
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
        
        # Field equations
        field_eq = Tex("G_{\\mu\\nu} = \\frac{8\\pi G}{c^4}T_{\\mu\\nu}", font_size=36)
        field_eq.to_corner(UR)
        field_eq_text = Text("Einstein's Field Equations", font_size=20)
        field_eq_text.next_to(field_eq, DOWN)
        self.play(Write(field_eq), Write(field_eq_text))
        
        self.wait(2)
        
        # Clear for next section
        self.play(
            FadeOut(einstein_explain),
            FadeOut(field_eq),
            FadeOut(field_eq_text),
            FadeOut(einstein_title)
        )
        
        # Part 2: Spacetime Curvature
        section_title = Text("Part 2: Spacetime Curvature", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        # Text for spacetime explanation
        spacetime_text = Text("Spacetime: Unified 4D fabric of space and time", font_size=36).to_edge(UP)
        self.play(Write(spacetime_text))
        
        # Text explaining flat vs curved spacetime
        flat_text = Text("In the absence of mass, spacetime is flat", font_size=28)
        flat_text.next_to(spacetime_text, DOWN)
        self.play(Write(flat_text))
        
        self.wait(1.5)
        
        # Reset to flat grid
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
            ReplacementTransform(curved_grid, flat_grid),
            FadeOut(sun),
            run_time=1.5
        )
        
        # Show some straight-line paths on flat spacetime
        paths = VGroup()
        for i, start_y in enumerate([-3, -1, 1, 3]):
            path = Line([-6, start_y, 0], [6, start_y, 0], color=GREEN)
            paths.add(path)
            
        self.play(ShowCreation(paths), run_time=1.5)
        
        # Text explaining straight paths
        straight_text = Text("Objects move in straight lines through flat spacetime", font_size=24)
        straight_text.to_edge(DOWN)
        self.play(Write(straight_text))
        
        self.wait(2)
        
        # Now show curved spacetime
        curved_text = Text("Mass curves spacetime", font_size=28)
        self.play(
            ReplacementTransform(flat_text, curved_text),
            FadeOut(straight_text),
            FadeOut(paths)
        )
        
        # Add back the massive object
        massive_object = Circle(radius=0.8)
        massive_object.set_fill(YELLOW, opacity=1)
        massive_object.set_stroke(YELLOW, 3)
        massive_object.move_to(ORIGIN)
        
        self.play(GrowFromCenter(massive_object))
        
        # Show the curvature transformation again
        curved_grid = flat_grid.copy()
        curved_grid.apply_function(curve_function)
        
        self.play(
            ReplacementTransform(flat_grid, curved_grid),
            run_time=2
        )
        
        # Text explaining curved spacetime
        curved_explain = Text("Objects follow geodesics (shortest paths) through curved spacetime", font_size=24)
        curved_explain.to_edge(DOWN)
        self.play(Write(curved_explain))
        
        self.wait(2)
        
        # Part 3: Orbital Motion
        self.play(
            FadeOut(curved_explain),
            FadeOut(spacetime_text),
            FadeOut(curved_text)
        )
        
        section_title = Text("Part 3: Orbital Motion & Geodesics", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        # Text for orbital motion
        orbital_text = Text("Planets orbit due to spacetime curvature", font_size=36).to_edge(UP)
        self.play(Write(orbital_text))
        
        # Create circular orbit
        orbit = Circle(radius=3, color=WHITE)
        orbit.move_to(ORIGIN)
        
        # Create a planet
        planet = Dot(color=BLUE, radius=0.2)
        planet.move_to(orbit.point_from_proportion(0))
        
        self.play(ShowCreation(orbit))
        self.play(FadeIn(planet))
        
        # Animate the planet orbiting
        self.play(
            MoveAlongPath(planet, orbit),
            run_time=6,
            rate_func=linear
        )
        
        # Explanation of orbits as geodesics
        geodesic_text = Text("Orbits are simply objects following the straightest possible paths\nthrough curved spacetime", 
                           font_size=24).to_edge(DOWN)
        self.play(Write(geodesic_text))
        
        self.wait(2)
        
        # Part 4: Mercury's Orbit - Precession
        self.play(
            FadeOut(geodesic_text),
            FadeOut(orbital_text)
        )
        
        # Keep planet, orbit, curved_grid, and massive_object
        
        mercury_title = Text("Mercury's Orbit: General Relativity's First Triumph", font_size=34).to_edge(UP)
        self.play(Write(mercury_title))
        
        # Create an elliptical orbit with precession
        def elliptical_orbit(t):
            a, b = 3, 2.5  # Semi-major and semi-minor axes
            precession_rate = 0.2  # Degrees of precession per orbit (exaggerated)
            angle = t * 2 * PI
            precession_angle = t * precession_rate
            x = a * np.cos(angle) * np.cos(precession_angle) - b * np.sin(angle) * np.sin(precession_angle)
            y = a * np.cos(angle) * np.sin(precession_angle) + b * np.sin(angle) * np.cos(precession_angle)
            return np.array([x, y, 0])
        
        # Create the precessing elliptical orbit
        t_range = np.linspace(0, 4*PI, 1000)
        ellipse_points = [elliptical_orbit(t) for t in np.linspace(0, 1, 100)]
        elliptical_path = VMobject(color=WHITE)
        elliptical_path.set_points_smoothly(ellipse_points)
        
        # Create Mercury
        mercury = Dot(color=GOLD_E, radius=0.15)
        mercury.move_to(elliptical_path.point_from_proportion(0))
        
        # Replace the circular orbit with elliptical one
        self.play(
            ReplacementTransform(orbit, elliptical_path),
            ReplacementTransform(planet, mercury)
        )
        
        # Show several orbits with precession
        for i in range(2):
            new_ellipse_points = [elliptical_orbit(t + (i+1)) for t in np.linspace(0, 1, 100)]
            new_path = VMobject(color=WHITE)
            new_path.set_points_smoothly(new_ellipse_points)
            
            self.play(
                MoveAlongPath(mercury, new_path),
                run_time=6,
                rate_func=linear
            )
            
            # Update the path to show precession
            self.play(ReplacementTransform(elliptical_path, new_path))
            elliptical_path = new_path
        
        # Explanation of Mercury's precession
        mercury_text = Text("Mercury's orbit precesses slightly each cycle.\nThis was unexplained by Newton, but predicted by Einstein.", 
                          font_size=24).to_edge(DOWN)
        self.play(Write(mercury_text))
        
        self.wait(2)
        
        # Clear for next section
        self.play(
            FadeOut(mercury_text),
            FadeOut(mercury_title),
            FadeOut(mercury),
            FadeOut(elliptical_path)
        )
        
        # Part 5: Light Bending
        section_title = Text("Part 5: Light Bending", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        light_title = Text("Light follows curved paths in spacetime", font_size=36).to_edge(UP)
        self.play(Write(light_title))
        
        # Create light rays
        light_rays = []
        for i, start_y in enumerate(np.linspace(-4, 4, 9)):
            # Skip paths that would go through the sun
            if abs(start_y) < 1:
                continue
                
            # Create a path that bends more the closer it is to the sun
            bend_factor = 2.0 / abs(start_y)  # More bending for closer rays
            ray = VGroup()
            
            points = []
            for x in np.linspace(-6, 6, 100):
                # Calculate bending - more pronounced near the sun
                dist = np.sqrt(x**2 + start_y**2)
                bend = bend_factor * np.exp(-0.2 * dist) * np.sign(start_y)
                points.append([x, start_y - bend, 0])
            
            # Create the ray as a smooth curve
            curve = VMobject(color=YELLOW, stroke_opacity=0.8)
            curve.set_points_smoothly(points)
            light_rays.append(curve)
        
        # Show light rays one by one
        for ray in light_rays:
            self.play(ShowCreation(ray), run_time=0.75)
        
        # Explanation of light bending
        light_text = Text("Light follows null geodesics - the paths of shortest distance\nthrough curved spacetime", 
                         font_size=24).to_edge(DOWN)
        self.play(Write(light_text))
        
        # Famous solar eclipse observation mention
        eclipse_text = Text("Confirmed during the 1919 solar eclipse", font_size=20)
        eclipse_text.next_to(light_text, DOWN)
        self.play(Write(eclipse_text))
        
        self.wait(2)
        
        # Part 6: Gravitational Lensing
        self.play(
            FadeOut(light_text),
            FadeOut(eclipse_text)
        )
        
        lensing_title = Text("Gravitational Lensing", font_size=36)
        self.play(ReplacementTransform(light_title, lensing_title))
        
        # Create a distant galaxy (source of light)
        galaxy = VGroup()
        for angle in np.linspace(0, 2*PI, 8, endpoint=False):
            arm = VGroup()
            for r in np.linspace(0, 0.5, 20):
                dot = Dot([r * np.cos(angle + r*3), r * np.sin(angle + r*3), 0], radius=0.02)
                dot.set_color(BLUE)
                arm.add(dot)
            galaxy.add(arm)
        
        galaxy.move_to([-5, 3, 0])
        self.play(FadeIn(galaxy))
        
        # Multiple images of the galaxy due to lensing
        lensed_images = VGroup()
        
        # Create several distorted images of the galaxy
        # Positions for lensed images - arranged in an Einstein ring-like formation
        image_positions = [
            [3, 1.5, 0],   # Upper right
            [3, -1.5, 0],  # Lower right
            [1.5, 0, 0],   # Middle right (more distorted)
            [-1.5, 0, 0],  # Middle left (more distorted)
        ]
        
        for pos in image_positions:
            # Create a distorted copy of the galaxy
            image = galaxy.copy()
            
            # Distort the image based on position relative to the lens
            vec_to_lens = np.array(ORIGIN) - np.array(pos)
            dist_to_lens = np.linalg.norm(vec_to_lens)
            stretch_direction = vec_to_lens / dist_to_lens
            
            # Apply different stretching/distortion to each image
            stretch_factor = 2.5 / (dist_to_lens + 0.5)
            scale_factor = 0.5 * (1 + 0.3 / (dist_to_lens + 0.5))
            
            # Apply transformations
            image.scale(scale_factor)
            image.move_to(pos)
            image.stretch(1 + stretch_factor, direction=stretch_direction)
            
            lensed_images.add(image)
        
        # Show the lensed images appearing
        for image in lensed_images:
            self.play(FadeIn(image), run_time=0.75)
        
        # Explanation of gravitational lensing
        lensing_text = Text("Massive objects can create multiple, distorted images\nof distant light sources", 
                          font_size=24).to_edge(DOWN)
        self.play(Write(lensing_text))
        
        # Draw lines showing light paths
        light_paths = VGroup()
        for image in lensed_images:
            path = VMobject(color=YELLOW, stroke_opacity=0.3)
            
            # Create curved path from galaxy to lensed image
            start_point = galaxy.get_center()
            end_point = image.get_center()
            
            # Find vector to the lens
            mid_point = ORIGIN
            
            # Create a quadratic Bezier curve
            points = []
            for t in np.linspace(0, 1, 50):
                # Quadratic Bezier formula
                p = (1-t)**2 * start_point + 2*(1-t)*t * mid_point + t**2 * end_point
                points.append(p)
            
            path.set_points_smoothly(points)
            light_paths.add(path)
        
        self.play(ShowCreation(light_paths), run_time=2)
        
        self.wait(2)
        
        # Part 7: Black Holes
        self.play(
            FadeOut(lensing_text),
            FadeOut(light_paths),
            FadeOut(lensed_images),
            FadeOut(galaxy),
            FadeOut(light_rays)
        )
        
        blackhole_title = Text("Black Holes: Extreme Spacetime Curvature", font_size=36)
        self.play(ReplacementTransform(lensing_title, blackhole_title))
        
        # Transform sun into black hole
        blackhole = Circle(radius=0.5)
        blackhole.set_fill(BLACK, opacity=1)
        blackhole.set_stroke(BLACK, 0)
        blackhole.move_to(ORIGIN)
        
        # Event horizon
        event_horizon = Circle(radius=0.5, color=RED)
        event_horizon.move_to(ORIGIN)
        
        self.play(
            ReplacementTransform(massive_object, blackhole),
            FadeIn(event_horizon)
        )
        
        # Make the spacetime curvature more extreme
        def extreme_curve_function(point):
            x, y, z = point
            dist = np.sqrt(x**2 + y**2)
            if dist < 0.5:  # Inside event horizon
                return point
            factor = 3.5 / (dist + 0.1)  # More extreme curvature
            return [x, y - factor, z]
        
        extreme_curved_grid = curved_grid.copy()
        extreme_curved_grid.apply_function(extreme_curve_function)
        
        self.play(
            ReplacementTransform(curved_grid, extreme_curved_grid),
            run_time=2
        )
        
        # Text explaining black holes
        blackhole_text = Text("Black holes have such extreme curvature that\nnothing, not even light, can escape past the event horizon", 
                            font_size=24).to_edge(DOWN)
        self.play(Write(blackhole_text))
        
        # Light rays that get trapped
        trapped_rays = []
        for angle in np.linspace(0, 2*PI, 16, endpoint=False):
            start_radius = 0.3
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            points = []
            # Rays spiral inward
            for t in np.linspace(0, 1, 50):
                r = start_radius * (1 - 0.8*t)  # Decreasing radius
                spiral_angle = angle + 4*PI*t    # Spiraling
                x = r * np.cos(spiral_angle)
                y = r * np.sin(spiral_angle)
                points.append([x, y, 0])
            
            ray = VMobject(color=YELLOW, stroke_opacity=0.8)
            ray.set_points_smoothly(points)
            trapped_rays.append(ray)
        
        # Show trapped rays
        for ray in trapped_rays:
            self.play(ShowCreation(ray), run_time=0.5)
        
        self.wait(2)
        
        # Part 8: Gravitational Waves
        self.play(
            FadeOut(blackhole_text),
            FadeOut(blackhole_title),
            FadeOut(blackhole),
            FadeOut(event_horizon),
            *[FadeOut(ray) for ray in trapped_rays]
        )
        
        section_title = Text("Part 8: Gravitational Waves", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        # Reset to a flat grid
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
            ReplacementTransform(extreme_curved_grid, flat_grid),
            run_time=1.5
        )
        
        wave_title = Text("Gravitational Waves: Ripples in Spacetime", font_size=36).to_edge(UP)
        self.play(Write(wave_title))
        
        # Create binary system
        star1 = Circle(radius=0.4)
        star1.set_fill(BLUE, opacity=1)
        star1.set_stroke(BLUE_E, 2)
        
        star2 = Circle(radius=0.4)
        star2.set_fill(RED, opacity=1)
        star2.set_stroke(RED_E, 2)
        
        # Position stars in orbit around each other
        binary_center = ORIGIN
        orbital_radius = 1.0
        star1.move_to([binary_center[0] + orbital_radius, binary_center[1], 0])
        star2.move_to([binary_center[0] - orbital_radius, binary_center[1], 0])
        
        self.play(FadeIn(star1), FadeIn(star2))
        
        # Binary orbit animation
        orbital_period = 5  # Seconds for one orbit
        self.orbital_t = 0
        
        def update_stars(stars, dt):
            self.orbital_t += dt
            angle = self.orbital_t * (2*PI / orbital_period)
            star1, star2 = stars
            star1.move_to([binary_center[0] + orbital_radius * np.cos(angle), 
                           binary_center[1] + orbital_radius * np.sin(angle), 0])
            star2.move_to([binary_center[0] - orbital_radius * np.cos(angle), 
                           binary_center[1] - orbital_radius * np.sin(angle), 0])
            return stars
        
        binary_system = VGroup(star1, star2)
        binary_system.add_updater(update_stars)
        self.add(binary_system)
        
        # Create expanding gravitational wave ripples
        ripples = VGroup()
        
        def make_ripple(t):
            circle = Circle(radius=t * 5, color=BLUE)
            # Oscillation pattern
            amplitude = 0.1 * np.exp(-0.5 * t)  # Decreasing amplitude
            width_factor = 1 + amplitude * np.sin(t * 12)  # Wave pattern
            
            circle.stretch(width_factor, 0)  # Stretch horizontally
            circle.stretch(1/width_factor, 1)  # Compensate vertically
            circle.set_stroke(opacity=max(0, 0.5 - 0.5*t))  # Fade out with distance
            return circle
        
        # Initial ripples
        for t in np.linspace(0.1, 1.5, 8):
            ripple = make_ripple(t)
            ripples.add(ripple)
        
        self.play(ShowCreation(ripples))
        
        # Animate ripples expanding
        for i in range(3):
            new_ripples = VGroup()
            for t in np.linspace(0.1, 1.5, 8):
                ripple = make_ripple(t + 0.2 * (i+1))
                new_ripples.add(ripple)
            
            self.play(
                Transform(ripples, new_ripples),
                run_time=1.5
            )
        
        binary_system.clear_updaters()
        
        # Text explaining gravitational waves
        wave_text = Text("Accelerating masses create ripples in spacetime\nthat propagate at the speed of light", 
                       font_size=24).to_edge(DOWN)
        self.play(Write(wave_text))
        
        # LIGO detection note
        ligo_text = Text("First directly detected by LIGO in 2015", font_size=20)
        ligo_text.next_to(wave_text, DOWN)
        self.play(Write(ligo_text))
        
        self.wait(2)
        
        # Part 9: Applications and Implications
        self.play(
            FadeOut(wave_text),
            FadeOut(ligo_text),
            FadeOut(wave_title),
            FadeOut(ripples),
            FadeOut(binary_system),
            FadeOut(flat_grid)
        )
        
        section_title = Text("Part 9: Applications & Implications", font_size=48)
        self.play(Write(section_title))
        self.wait(1.5)
        self.play(FadeOut(section_title))
        
        # GPS satellite application
        gps_title = Text("Real-world Applications: GPS", font_size=36).to_edge(UP)
        self.play(Write(gps_title))
        
        # Earth
        earth = Circle(radius=1.5)
        earth.set_fill(BLUE, opacity=0.8)
        earth.set_stroke(GREEN_E, 2)
        earth.move_to(ORIGIN)
        
        # GPS satellite
        satellite = VGroup()
        satellite_body = Rectangle(height=0.2, width=0.5, color=LIGHT_GRAY)
        satellite_panels = VGroup(
            Rectangle(height=0.1, width=1.0, color=GOLD).next_to(satellite_body, LEFT, buff=0),
            Rectangle(height=0.1, width=1.0, color=GOLD).next_to(satellite_body, RIGHT, buff=0)
        )
        satellite.add(satellite_body, satellite_panels)
        
        orbit_radius = 3
        satellite.move_to([orbit_radius, 0, 0])
        
        # Orbit path
        orbit = Circle(radius=orbit_radius)
        orbit.set_stroke(WHITE, opacity=0.5)
        orbit.move_to(ORIGIN)
        
        self.play(FadeIn(earth), ShowCreation(orbit))
        self.play(FadeIn(satellite))
        
        # Time dilation explanation
        time_text1 = Text("GPS satellites experience less gravity than on Earth", font_size=24)
        time_text1.to_edge(DOWN, buff=1.5)
        
        time_text2 = Text("Resulting in time running slightly faster", font_size=24)
        time_text2.next_to(time_text1, DOWN)
        
        time_text3 = Text("Without relativistic corrections, GPS would accumulate\nerrors of ~10km per day!", font_size=24)
        time_text3.next_to(time_text2, DOWN)
        
        self.play(Write(time_text1))
        self.play(Write(time_text2))
        self.wait(1)
        self.play(Write(time_text3))
        
        # Animation of satellite orbiting
        self.play(
            MoveAlongPath(satellite, orbit),
            run_time=6,
            rate_func=linear
        )
        
        self.wait(2)
        
        # Conclusion
        self.play(
            FadeOut(time_text1),
            FadeOut(time_text2),
            FadeOut(time_text3),
            FadeOut(satellite),
            FadeOut(orbit),
            FadeOut(earth),
            FadeOut(gps_title)
        )
        
        # Final quote
        quote1 = Text("Spacetime tells matter how to move.", font_size=40)
        quote2 = Text("Matter tells spacetime how to curve.", font_size=40)
        attribution = Text("— John Wheeler", font_size=30)
        
        VGroup(quote1, quote2, attribution).arrange(DOWN, buff=0.5)
        
        self.play(Write(quote1))
        self.wait(0.5)
        self.play(Write(quote2))
        self.wait(0.5)
        self.play(Write(attribution))
        
        self.wait(3)
        
        # Credits
        credits = Text("Created with Manim - Mathematical Animation Engine", font_size=24)
        credits.to_edge(DOWN)
        
        self.play(
            FadeOut(quote1, run_time=1.5),
            FadeOut(quote2, run_time=1.5),
            FadeOut(attribution, run_time=1.5),
            Write(credits)
        )
        
        self.wait(2) 