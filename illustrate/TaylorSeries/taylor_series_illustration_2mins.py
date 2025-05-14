from manimlib import *
import numpy as np

class TaylorSeriesDirectorsCut(Scene):
    def construct(self):
        # ---- 1. Cold-open hook ----
        self.cold_open()
        
        # ---- 2. Title card ----
        self.title_card()
        
        # Set up the primary scene elements
        self.setup_world()
        
        # ---- 3-7. Main term-by-term animation with camera transitions ----
        self.animate_taylor_terms()
        
        # ---- 8. Optional real-world application ----
        self.show_application()
        
        # ---- 9. Closing zoom-out & takeaway ----
        self.closing_sequence()
    
    def cold_open(self):
        # Dark screen with a single pulsing dot
        dot = Dot(color=YELLOW).set_opacity(0)
        
        # Voice-over text appears briefly
        question = Text("How can you build a curve out of nothing but straight-line information?")
        question.set_opacity(0.8)
        
        # Animate the dot pulsing
        self.play(
            FadeIn(question),
            FadeIn(dot),
            dot.animate.set_opacity(1).scale(1.3),
            rate_func=there_and_back,
            run_time=2
        )
        self.play(
            dot.animate.set_opacity(1).scale(1.3),
            rate_func=there_and_back,
            run_time=2
        )
        
        # Dot radiates concentric circles
        circles = [Circle(radius=r, color=YELLOW).set_opacity(0.5) 
                  for r in np.linspace(0.2, 3, 5)]
        
        for circle in circles:
            self.play(
                GrowFromCenter(circle),
                run_time=0.4
            )
            self.play(
                FadeOut(circle),
                run_time=0.2
            )
        
        # Fade out question as we transition to main scene
        self.play(FadeOut(question))
        
        return dot
    
    def title_card(self):
        title = Text("Building sin(x), one term at a time", font_size=48)
        subtitle = Text("– the Taylor story", font_size=36)
        subtitle.next_to(title, DOWN)
        title_group = VGroup(title, subtitle)
        
        # Slide in title
        self.play(
            Write(title),
            Write(subtitle),
            run_time=2
        )
        
        # Shrink and move to corner as watermark
        watermark = Text("Taylor Series", font_size=16)
        watermark.to_corner(UR)
        
        self.play(
            ReplacementTransform(title_group, watermark),
            run_time=1
        )
        
        return watermark
    
    def setup_world(self):
        # Set up the main axes that we'll use throughout
        self.axes = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        self.axes.add_coordinate_labels(font_size=24)
        
        # Define the sine function
        self.sin_func = lambda x: np.sin(x)
        
        # Create sine graph
        self.original_graph = self.axes.get_graph(
            self.sin_func,
            color=BLUE,
        )
        
        # Text label for sine function
        self.function_label = Tex("f(x) = \\sin(x)").set_color(BLUE)
        self.function_label.to_corner(UL)
        
        # Add the axis and function to scene
        self.play(
            Write(self.axes),
            ShowCreation(self.original_graph),
            Write(self.function_label)
        )
        
        # Point around which we'll create the Taylor series
        self.x0 = 0
        self.center_point = Dot(self.axes.c2p(self.x0, self.sin_func(self.x0)), color=YELLOW)
        self.point_label = Tex(f"x_0 = {self.x0}").next_to(self.center_point, UR, buff=0.1).set_color(YELLOW)
        
        self.play(
            FadeIn(self.center_point),
            Write(self.point_label)
        )
        
        # Create an area for equations (the "runway")
        self.equation_area = Rectangle(
            width=4, 
            height=FRAME_HEIGHT - 1,
            stroke_opacity=0.2,
            fill_opacity=0.1
        )
        self.equation_area.to_edge(RIGHT)
        self.play(FadeIn(self.equation_area))
        
        # Create a space for derivative information
        self.derivative_area = Rectangle(
            width=2.5,
            height=3,
            stroke_opacity=0.2,
            fill_opacity=0.1
        )
        self.derivative_area.to_corner(DL)
        self.play(FadeIn(self.derivative_area))
        
        # Title for derivative area
        self.derivative_title = Text("Derivatives", font_size=20)
        self.derivative_title.next_to(self.derivative_area, UP, buff=0.1)
        self.play(Write(self.derivative_title))
    
    def get_taylor_term(self, degree, x0=0):
        """Get the partial Taylor polynomial function up to the given degree"""
        if degree == 0:
            return lambda x: np.sin(x0)
        elif degree == 1:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0)
        elif degree == 2:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2
        elif degree == 3:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2 - np.cos(x0)/6*(x-x0)**3
        elif degree == 4:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2 - np.cos(x0)/6*(x-x0)**3 + np.sin(x0)/24*(x-x0)**4
        elif degree == 5:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2 - np.cos(x0)/6*(x-x0)**3 + np.sin(x0)/24*(x-x0)**4 + np.cos(x0)/120*(x-x0)**5
        elif degree == 7:
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2 - np.cos(x0)/6*(x-x0)**3 + np.sin(x0)/24*(x-x0)**4 + np.cos(x0)/120*(x-x0)**5 - np.sin(x0)/720*(x-x0)**6 - np.cos(x0)/5040*(x-x0)**7
        elif degree == 9:
            # Add terms for degree 9
            return lambda x: np.sin(x0) + np.cos(x0)*(x-x0) - np.sin(x0)/2*(x-x0)**2 - np.cos(x0)/6*(x-x0)**3 + np.sin(x0)/24*(x-x0)**4 + np.cos(x0)/120*(x-x0)**5 - np.sin(x0)/720*(x-x0)**6 - np.cos(x0)/5040*(x-x0)**7 + np.sin(x0)/40320*(x-x0)**8 + np.cos(x0)/362880*(x-x0)**9
    
    def get_individual_term(self, degree, x0=0):
        """Get just the individual term function for the given degree"""
        if degree == 0:
            return lambda x: np.sin(x0)
        elif degree == 1:
            return lambda x: np.cos(x0)*(x-x0)
        elif degree == 2:
            return lambda x: -np.sin(x0)/2*(x-x0)**2
        elif degree == 3:
            return lambda x: -np.cos(x0)/6*(x-x0)**3
        elif degree == 4:
            return lambda x: np.sin(x0)/24*(x-x0)**4
        elif degree == 5:
            return lambda x: np.cos(x0)/120*(x-x0)**5
    
    def get_error_function(self, degree, x0=0):
        """Get the error function between the true function and Taylor approximation"""
        taylor_func = self.get_taylor_term(degree, x0)
        return lambda x: np.abs(self.sin_func(x) - taylor_func(x))
    
    def switch_to_microscope(self):
        """Transition to microscope mode - zoomed in on the neighborhood of x0"""
        # Save the current camera state
        original_frame = self.camera.frame.copy()
        
        # Zoom in to the neighborhood of x0
        self.play(
            self.camera.frame.animate.scale(0.3).move_to(self.center_point),
            run_time=1.5
        )
        
        return original_frame
    
    def switch_to_world(self, original_frame=None):
        """Transition back to world mode - full view of the axes"""
        if original_frame:
            self.play(
                self.camera.frame.animate.become(original_frame),
                run_time=1.5
            )
        else:
            self.play(
                self.camera.frame.animate.scale(3.33).center(),
                run_time=1.5
            )
    
    def show_derivative_bars(self, degree):
        """Update the derivative visualization to show which derivatives are matched"""
        # Clear previous bars
        if hasattr(self, 'derivative_bars'):
            self.play(FadeOut(self.derivative_bars))
        
        # Create bars for 0th through 5th derivatives
        bars = VGroup()
        labels = VGroup()
        
        values = [
            np.sin(self.x0),        # 0th derivative
            np.cos(self.x0),        # 1st derivative
            -np.sin(self.x0),       # 2nd derivative
            -np.cos(self.x0),       # 3rd derivative
            np.sin(self.x0),        # 4th derivative
            np.cos(self.x0)         # 5th derivative
        ]
        
        bar_width = 0.3
        spacing = 0.4
        max_height = 1.5
        
        for i in range(6):
            # Normalize value for visual display
            height = max_height * abs(values[i])
            
            # Color based on whether this derivative is matched by current approximation
            color = GREEN if i <= degree else RED_A
            
            bar = Rectangle(
                width=bar_width,
                height=height,
                fill_opacity=0.8,
                color=color
            )
            
            # Position the bar
            bar.next_to(
                self.derivative_area.get_corner(DL) + RIGHT * 0.3 + UP * 0.3,
                RIGHT,
                buff=i * spacing
            )
            bar.align_to(self.derivative_area.get_corner(DL) + UP * 0.3, DOWN)
            
            # Label with derivative order
            label = Tex(f"{i}", font_size=16)
            label.next_to(bar, DOWN, buff=0.1)
            
            bars.add(bar)
            labels.add(label)
        
        self.derivative_bars = VGroup(bars, labels)
        self.play(FadeIn(self.derivative_bars))
    
    def show_error_ribbon(self, degree):
        """Display a ribbon showing the error between true function and approximation"""
        # Remove previous error ribbon if it exists
        if hasattr(self, 'error_ribbon'):
            self.play(FadeOut(self.error_ribbon))
        
        # Create the error function
        error_func = self.get_error_function(degree, self.x0)
        
        # Create ribbon (filled area between x-axis and error function)
        x_min, x_max = -4, 4
        dx = 0.1
        x_range = np.arange(x_min, x_max, dx)
        
        error_points = [self.axes.c2p(x, error_func(x)) for x in x_range]
        x_axis_points = [self.axes.c2p(x, 0) for x in x_range]
        
        # Combine points to form a polygon
        points = error_points + list(reversed(x_axis_points))
        
        # Create the ribbon
        ribbon = Polygon(
            *points,
            fill_opacity=0.3,
            fill_color=RED,
            stroke_width=0
        )
        
        # Add label
        error_label = Text("Error", font_size=16, color=RED)
        error_label.next_to(ribbon, UP, buff=0.2)
        
        self.error_ribbon = VGroup(ribbon, error_label)
        self.play(FadeIn(self.error_ribbon))
    
    def animate_taylor_terms(self):
        # Colors for each term personality
        colors = [RED_C, RED_E, GOLD_E, GREEN_C, TEAL_A, PURPLE_C]
        
        # Character names and commentary for each term
        term_personalities = [
            ("The Flat Friend", "Meet our laziest guess."),
            ("The Tangent Teen", "A straight line that matches the slope exactly."),
            ("The Parabola Plumber", "Notice how the endpoints dip the wrong way."),
            ("The Cubic Climber", "Now we match the familiar S-shape."),
            ("The Fourth-order Phantom", "Symmetry kills this term..."),
            ("The Fifth-order Fixer", "Adding the final polish.")
        ]
        
        # Simplified Taylor series expressions for sin(x) at x=0
        taylor_expressions = [
            "P_0(x) = 0",
            "P_1(x) = x",
            "P_2(x) = x",
            "P_3(x) = x - \\frac{x^3}{6}",
            "P_4(x) = x - \\frac{x^3}{6}",
            "P_5(x) = x - \\frac{x^3}{6} + \\frac{x^5}{120}"
        ]
        
        # Individual term expressions
        terms_tex = [
            "\\sin(0) = 0",
            "\\cos(0)(x-0) = x",
            "-\\frac{\\sin(0)}{2!}(x-0)^2 = 0",
            "-\\frac{\\cos(0)}{3!}(x-0)^3 = -\\frac{x^3}{6}",
            "\\frac{\\sin(0)}{4!}(x-0)^4 = 0",
            "\\frac{\\cos(0)}{5!}(x-0)^5 = \\frac{x^5}{120}"
        ]
        
        self.current_approx = None
        current_formula = None
        
        # For each degree, animate the term's personality
        for degree in range(6):
            # Get the Taylor term and full polynomial
            term_func = self.get_individual_term(degree, self.x0)
            taylor_func = self.get_taylor_term(degree, self.x0)
            
            # Create personality title and comment
            personality, comment = term_personalities[degree]
            personality_title = Text(personality, color=colors[degree], font_size=36)
            personality_title.to_edge(UP)
            comment_text = Text(comment, font_size=24, color=WHITE)
            comment_text.next_to(personality_title, DOWN)
            
            # Show the personality introduction
            self.play(
                Write(personality_title),
                Write(comment_text)
            )
            
            # Switch to microscope mode for detailed view
            original_frame = self.switch_to_microscope()
            
            # Special animations based on the term's "personality"
            if degree == 0:  # The Flat Friend
                flat_line = Line(
                    self.axes.c2p(-1, 0), 
                    self.axes.c2p(1, 0),
                    color=colors[degree]
                )
                
                self.play(
                    GrowFromCenter(flat_line),
                    run_time=1
                )
                
                # Extend the line outward
                extended_line = Line(
                    self.axes.c2p(-3, 0), 
                    self.axes.c2p(3, 0),
                    color=colors[degree]
                )
                
                self.play(
                    Transform(flat_line, extended_line),
                    run_time=1
                )
                
                # Create the actual term graph
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
                self.play(
                    ReplacementTransform(flat_line, term_graph),
                    run_time=0.5
                )
                
            elif degree == 1:  # The Tangent Teen
                # Start with horizontal line
                line = Line(
                    self.axes.c2p(-1, 0), 
                    self.axes.c2p(1, 0),
                    color=colors[degree]
                )
                
                # Pivot the line to match the slope
                pivoted_line = Line(
                    self.axes.c2p(-1, -1), 
                    self.axes.c2p(1, 1),
                    color=colors[degree]
                )
                
                self.play(
                    ReplacementTransform(line, pivoted_line),
                    run_time=1
                )
                
                # Extend the line
                extended_line = Line(
                    self.axes.c2p(-3, -3), 
                    self.axes.c2p(3, 3),
                    color=colors[degree]
                )
                
                self.play(
                    Transform(pivoted_line, extended_line),
                    run_time=1
                )
                
                # Create the actual term graph
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
                self.play(
                    ReplacementTransform(pivoted_line, term_graph),
                    run_time=0.5
                )
                
            elif degree == 2:  # The Parabola Plumber
                # Start with a line
                line = Line(
                    self.axes.c2p(-2, -2), 
                    self.axes.c2p(2, 2),
                    color=colors[degree]
                )
                
                # Control points for the parabola
                control_point = Dot(self.axes.c2p(0, 0), color=YELLOW)
                
                # Create a parabola
                def parabola(x):
                    return 0  # The coefficient is 0 for sin(x) at x=0, degree 2
                
                parabola_graph = self.axes.get_graph(
                    parabola,
                    color=colors[degree]
                )
                
                # Show control point briefly
                self.play(FadeIn(control_point))
                
                # Transform line to parabola
                self.play(
                    ReplacementTransform(line, parabola_graph),
                    FadeOut(control_point),
                    run_time=1.5
                )
                
                # Create the actual term graph (which is 0 in this case)
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
                self.play(
                    ReplacementTransform(parabola_graph, term_graph),
                    run_time=0.5
                )
                
            elif degree == 3:  # The Cubic Climber
                # Start with a line
                line = Line(
                    self.axes.c2p(-2, -2), 
                    self.axes.c2p(2, 2),
                    color=colors[degree]
                )
                
                # Create inflection arrows
                arrow1 = Arrow(
                    self.axes.c2p(-1, 0), 
                    self.axes.c2p(-1, -0.5),
                    color=YELLOW
                )
                
                arrow2 = Arrow(
                    self.axes.c2p(1, 0), 
                    self.axes.c2p(1, -0.5),
                    color=YELLOW
                )
                
                # Create cubic function
                def cubic(x):
                    return x - (x**3)/6
                
                cubic_graph = self.axes.get_graph(
                    cubic,
                    color=colors[degree]
                )
                
                # Show arrows tugging the graph
                self.play(
                    ReplacementTransform(line, cubic_graph),
                    GrowArrow(arrow1),
                    GrowArrow(arrow2),
                    run_time=1.5
                )
                
                self.play(
                    FadeOut(arrow1),
                    FadeOut(arrow2),
                    run_time=0.5
                )
                
                # Create the actual term graph
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
            elif degree == 4:  # The Fourth-order Phantom
                # Just show the equation for this one (since the term is 0)
                term_formula = Tex(terms_tex[degree]).set_color(colors[degree])
                term_formula.next_to(self.equation_area.get_center(), ORIGIN)
                
                self.play(
                    Write(term_formula),
                    run_time=1
                )
                
                # Create the actual term graph (which is 0)
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
                self.play(
                    ShowCreation(term_graph),
                    run_time=0.5
                )
                
                self.play(
                    FadeOut(term_formula),
                    run_time=0.5
                )
                
            elif degree == 5:  # The Fifth-order Fixer
                # Create a small wiggle wave
                def wiggle(x):
                    return (x**5)/120
                
                wiggle_graph = self.axes.get_graph(
                    wiggle,
                    color=colors[degree]
                )
                
                # Show error band shrinking
                error_highlight = self.axes.get_graph(
                    lambda x: np.sin(x) - (x - (x**3)/6),
                    color=RED_A,
                    stroke_opacity=0.5,
                    stroke_width=10
                )
                
                self.play(
                    ShowCreation(wiggle_graph),
                    ShowCreation(error_highlight),
                    run_time=1
                )
                
                self.play(
                    FadeOut(error_highlight),
                    run_time=0.5
                )
                
                # Create the actual term graph
                term_graph = self.axes.get_graph(
                    term_func,
                    color=colors[degree]
                )
                
                self.play(
                    ReplacementTransform(wiggle_graph, term_graph),
                    run_time=0.5
                )
            
            # Switch back to world view
            self.switch_to_world(original_frame)
            
            # Show the formula in the equation area
            equation = Tex(taylor_expressions[degree])
            equation.set_color(colors[degree])
            equation.next_to(self.equation_area.get_center(), ORIGIN)
            
            if current_formula:
                self.play(
                    ReplacementTransform(current_formula, equation),
                    run_time=1
                )
            else:
                self.play(Write(equation), run_time=1)
            
            current_formula = equation
            
            # Update the full approximation graph
            approx_graph = self.axes.get_graph(
                taylor_func,
                color=colors[degree]
            )
            
            if self.current_approx:
                self.play(
                    ReplacementTransform(self.current_approx, approx_graph),
                    run_time=1
                )
            else:
                self.play(ShowCreation(approx_graph), run_time=1)
            
            self.current_approx = approx_graph
            
            # Show derivative bars for this degree
            self.show_derivative_bars(degree)
            
            # Show error ribbon
            self.show_error_ribbon(degree)
            
            # Clean up the personality title and comment
            self.play(
                FadeOut(personality_title),
                FadeOut(comment_text),
                FadeOut(term_graph),
                run_time=0.5
            )
            
            # Pause between terms
            self.wait(0.5)
        
        # Speed-run montage to "infinite" after degree 5
        self.play(
            FadeOut(current_formula),
            run_time=0.5
        )
        
        # Quickly transition to higher degree approximations
        higher_degrees = [7, 9]
        
        for degree in higher_degrees:
            taylor_func = self.get_taylor_term(degree, self.x0)
            
            approx_graph = self.axes.get_graph(
                taylor_func,
                color=GREY,
                stroke_opacity=0.7
            )
            
            # Show the higher degree approximation
            self.play(
                ReplacementTransform(self.current_approx, approx_graph),
                run_time=0.25
            )
            
            # Update error ribbon
            self.show_error_ribbon(degree)
            
            self.current_approx = approx_graph
        
        # Final equation with ellipsis
        self.final_equation = Tex(
            "\\sin(x) = x - \\frac{x^3}{3!} + \\frac{x^5}{5!} - \\frac{x^7}{7!} + \\ldots"
        )
        self.final_equation.set_color(BLUE)
        self.final_equation.next_to(self.equation_area.get_center(), ORIGIN)
        
        self.play(
            Write(self.final_equation),
            run_time=1
        )
        
        # Pause for effect
        self.wait(1)
    
    def show_application(self):
        # Create a split screen effect
        divider = Line(UP * 3, DOWN * 3, stroke_width=2)
        
        # Create a pendulum SVG-like path
        pendulum_dot = Dot(UP * 2, color=YELLOW)
        pendulum_string = Line(ORIGIN, pendulum_dot.get_center(), color=WHITE)
        pendulum = VGroup(pendulum_string, pendulum_dot)
        
        # Position on right side
        pendulum.next_to(divider, RIGHT, buff=1.5)
        
        # Title for the application
        title = Text("Small-angle pendulum", font_size=24)
        title.next_to(pendulum, UP, buff=0.5)
        
        # Formula using the truncated Taylor series
        formula = Tex("T \\approx 2\\pi\\sqrt{\\frac{L}{g}}")
        formula.next_to(pendulum, DOWN, buff=0.5)
        
        engineer_note = Text("Engineers stop here and it works!", font_size=18, color=GREEN)
        engineer_note.next_to(formula, DOWN, buff=0.3)
        
        # Move the original sine graph to the left
        self.play(
            self.original_graph.animate.scale(0.7).shift(LEFT * 3),
            self.current_approx.animate.scale(0.7).shift(LEFT * 3),
            self.axes.animate.scale(0.7).shift(LEFT * 3),
            FadeIn(divider),
            run_time=1
        )
        
        # Show the pendulum
        self.play(
            Write(title),
            ShowCreation(pendulum),
            Write(formula),
            run_time=1
        )
        
        # Animate the pendulum swinging
        self.play(
            Rotating(
                pendulum,
                angle=0.3,
                about_point=ORIGIN,
                run_time=1,
                rate_func=there_and_back
            )
        )
        
        self.play(
            Rotating(
                pendulum,
                angle=-0.3,
                about_point=ORIGIN,
                run_time=1,
                rate_func=there_and_back
            )
        )
        
        # Show engineer note
        self.play(Write(engineer_note))
        
        # Clean up for the closing
        self.play(
            FadeOut(divider),
            FadeOut(pendulum),
            FadeOut(title),
            FadeOut(formula),
            FadeOut(engineer_note),
            FadeOut(self.axes),
            FadeOut(self.original_graph),
            FadeOut(self.current_approx),
            FadeOut(self.error_ribbon),
            FadeOut(self.derivative_bars),
            FadeOut(self.final_equation),
            FadeOut(self.center_point),
            FadeOut(self.point_label),
            FadeOut(self.function_label),
            FadeOut(self.derivative_area),
            FadeOut(self.equation_area),
            FadeOut(self.derivative_title),
            run_time=1.5
        )
    
    def closing_sequence(self):
        # Create the final pulsing dot
        dot = Dot(color=YELLOW)
        
        # Create the circular text
        text = "Big curves, built from small truths."
        text_circle = VGroup()
        
        # Place text characters in a circle
        radius = 2.0
        for i, char in enumerate(text):
            angle = -TAU * i / len(text) + PI/2  # Start from the top
            char_text = Text(char, font_size=24)
            char_text.move_to(radius * np.array([np.cos(angle), np.sin(angle), 0]))
            char_text.rotate(angle + PI/2)  # Orient the text tangent to the circle
            text_circle.add(char_text)
            
        text_circle.set_color(BLUE)
        
        # Show the dot
        self.play(FadeIn(dot))
        
        # Make the dot pulse
        self.play(
            dot.animate.scale(1.3),
            rate_func=there_and_back,
            run_time=1
        )
        
        # Add the circular text
        self.play(Write(text_circle), run_time=2)
        
        # Rotate the circular text
        self.play(
            Rotating(text_circle, angle=TAU/4, run_time=3, about_point=ORIGIN)
        )
        
        # Final pulse and fade out
        self.play(
            dot.animate.scale(1.5).set_opacity(0),
            text_circle.animate.set_opacity(0),
            run_time=2
        ) 