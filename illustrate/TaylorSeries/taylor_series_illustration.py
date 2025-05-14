from manimlib import *
import numpy as np

class TaylorSeriesIllustration(Scene):
    def construct(self):
        # Create main scene elements
        axes, original_graph, function_label, point, point_label = self.setup_main_scene()
        
        # Show derivative concept visually before Taylor series
        self.show_derivative_concept(axes, original_graph, point)
        
        # Initialize the Taylor series visualization
        self.visualize_taylor_series(axes, original_graph, function_label, point, point_label)
        
        # Final reveal and conclusion
        self.final_reveal(axes, original_graph)

    def setup_main_scene(self):
        # Opening title
        title = Text("The Power of Taylor Series", font_size=60)
        subtitle = Text("Approximating complex functions with polynomials", font_size=36)
        subtitle.next_to(title, DOWN, buff=0.5)
        title_group = VGroup(title, subtitle)
        
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(1)
        self.play(FadeOut(title_group))
        
        # Set up the axes with a dramatic reveal
        axes = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        axes.add_coordinate_labels()
        
        # Axes appear dramatically
        self.play(
            ShowCreation(axes.x_axis),
            run_time=1
        )
        self.play(
            ShowCreation(axes.y_axis),
            Write(axes.coordinate_labels),
            run_time=1
        )
        
        # Define the function to approximate (sine function)
        def func(x):
            return np.sin(x)
        
        # Create the original function graph with dramatic drawing
        original_graph = axes.get_graph(
            func,
            color=BLUE,
        )
        function_label = Tex("f(x) = \\sin(x)").set_color(BLUE).to_corner(UL)
        
        # Draw sine wave with trailing effect
        self.play(
            ShowCreation(original_graph),
            run_time=2
        )
        self.play(Write(function_label))
        self.wait(0.5)
        
        # Create a thought bubble with question
        question = Text("How can we approximate this curve\nusing simple polynomials?", font_size=32)
        question_box = SurroundingRectangle(question, color=WHITE, buff=0.5)
        question_group = VGroup(question_box, question)
        question_group.to_corner(UR)
        
        self.play(
            Write(question),
            ShowCreation(question_box),
            run_time=1.5
        )
        self.wait(1)
        self.play(FadeOut(question_group))
        
        # Point around which we'll create the Taylor series
        x0 = 0
        point = Dot(axes.c2p(x0, func(x0)), color=YELLOW, radius=0.1)
        point_label = Tex(f"x_0 = {x0}").next_to(point, UR, buff=0.1).set_color(YELLOW)
        
        # Add the point with emphasis
        self.play(
            FadeIn(point, scale=1.5),
            run_time=1
        )
        self.play(Write(point_label))
        
        return axes, original_graph, function_label, point, point_label
    
    def show_derivative_concept(self, axes, original_graph, point):
        # Create tangent line at x=0
        def func(x):
            return np.sin(x)
            
        x0 = 0
        derivative_at_x0 = np.cos(x0)  # First derivative of sin(x) at x=0 is cos(0) = 1
        
        # Create tangent line - using Line instead of TangentLine for simplicity
        point_at_x0 = axes.c2p(x0, func(x0))
        dx = 0.01
        x1 = x0 + dx
        slope = (func(x1) - func(x0)) / dx  # Approximate the derivative
        
        # Create a tangent line manually
        tangent_line = Line(
            axes.c2p(x0 - 2, func(x0) - 2 * slope),
            axes.c2p(x0 + 2, func(x0) + 2 * slope),
            color=GREEN
        )
        
        derivative_label = Tex(f"f'({x0}) = {derivative_at_x0}").set_color(GREEN)
        derivative_label.next_to(tangent_line.get_end(), UL, buff=0.5)
        
        # Show concept of derivatives
        deriv_concept = Tex("Derivatives tell us how to build\nthe approximation step by step").scale(0.8)
        deriv_concept.to_edge(UP)
        
        # Animate appearance of tangent line
        self.play(
            ShowCreation(tangent_line),
            Write(derivative_label),
            run_time=1.5
        )
        self.play(Write(deriv_concept))
        self.wait(1)
        
        # Create multiple tangent lines
        tangent_lines = VGroup()
        x_values = np.linspace(-3, 3, 10)
        
        for x in x_values:
            if abs(x - x0) > 0.2:  # Skip points too close to the origin
                # Calculate the derivative at point x
                dx = 0.01
                x1 = x + dx
                slope = (func(x1) - func(x)) / dx
                
                # Create a line with the right slope
                line = Line(
                    axes.c2p(x - 1, func(x) - 1 * slope),
                    axes.c2p(x + 1, func(x) + 1 * slope),
                    color=GREEN_C,
                    stroke_opacity=0.6
                )
                tangent_lines.add(line)
        
        # Show multiple tangent lines to visually suggest derivatives everywhere
        self.play(
            LaggedStartMap(ShowCreation, tangent_lines),
            run_time=2
        )
        self.wait(1)
        
        # Transition out
        self.play(
            FadeOut(tangent_lines),
            FadeOut(tangent_line), 
            FadeOut(derivative_label),
            FadeOut(deriv_concept),
            run_time=1
        )
        
    def visualize_taylor_series(self, axes, original_graph, function_label, point, point_label):
        x0 = 0
        
        # Create Taylor polynomial approximations
        def get_taylor_term(degree, x0=0):
            # Taylor series coefficients for sin(x) around x0
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
        
        # Terms to display separately for the animation
        def get_individual_term(degree, x0=0):
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
                
        # Error function (difference between original and approximation)
        def get_error_func(approx_func):
            return lambda x: np.sin(x) - approx_func(x)
        
        # Taylor series term tex expressions
        terms_tex = [
            "\\sin(0) = 0",
            "\\cos(0)(x-0) = x",
            "-\\frac{\\sin(0)}{2!}(x-0)^2 = 0",
            "-\\frac{\\cos(0)}{3!}(x-0)^3 = -\\frac{x^3}{6}",
            "\\frac{\\sin(0)}{4!}(x-0)^4 = 0",
            "\\frac{\\cos(0)}{5!}(x-0)^5 = \\frac{x^5}{120}"
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
        
        # Set colors for Taylor polynomials of different degrees
        colors = [RED_A, RED_C, RED_E, GREEN_C, GREEN_E, PURPLE_C]
        
        # Create title for this section
        title = Text("Building a Taylor Series Approximation", font_size=42)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(0.5)
        
        # Create degree tracker (slider visual)
        degree_tracker = ValueTracker(0)
        degree_text = Integer(0)
        degree_text.add_updater(lambda d: d.set_value(degree_tracker.get_value()))
        
        degree_label = Text("Degree: ", font_size=36)
        degree_group = VGroup(degree_label, degree_text).arrange(RIGHT)
        degree_group.to_corner(UL)
        
        self.play(
            FadeIn(degree_group),
            run_time=1
        )
        
        # Split screen setup
        left_axes = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        left_axes.add_coordinate_labels()
        
        right_axes = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        right_axes.add_coordinate_labels()
        
        # Set up split screen
        split_screen = VGroup(left_axes, right_axes).arrange(RIGHT, buff=1)
        split_screen.scale(0.7).to_edge(DOWN)
        
        left_original = left_axes.get_graph(lambda x: np.sin(x), color=BLUE)
        right_original = right_axes.get_graph(lambda x: np.sin(x), color=BLUE)
        
        left_title = Text("Individual Term", font_size=24).next_to(left_axes, UP)
        right_title = Text("Full Approximation", font_size=24).next_to(right_axes, UP)
        
        self.play(
            FadeOut(axes),
            ShowCreation(left_axes),
            ShowCreation(right_axes),
            ShowCreation(left_original),
            ShowCreation(right_original),
            Write(left_title),
            Write(right_title),
            run_time=2
        )
        
        # Set up for convergence radius visualization
        convergence_circle = Circle(radius=0).set_stroke(YELLOW, opacity=0.3)
        convergence_circle.move_to(right_axes.c2p(0, 0))
        
        # Initialize tracker for animation
        current_approx_graph = None
        current_formula = None
        
        # Add building blocks visual
        building_blocks = VGroup()
        building_blocks.to_edge(RIGHT).shift(UP)
        
        for degree in range(6):
            # Update degree tracker
            self.play(
                degree_tracker.animate.set_value(degree),
                run_time=0.5
            )
            
            # Get the Taylor polynomial function
            taylor_func = get_taylor_term(degree, x0)
            
            # Create visualization of just this term being added
            term_func = get_individual_term(degree, x0)
            
            # Create graph of the current term on left side
            term_graph = left_axes.get_graph(
                term_func,
                color=colors[degree],
            )
            
            # Create the term's formula
            term_formula = Tex(terms_tex[degree]).set_color(colors[degree])
            term_formula.scale(0.8).next_to(left_axes, DOWN)
            
            # Show the new term with dramatic effect
            self.play(
                ShowCreation(term_graph),
                Write(term_formula),
                run_time=1.5
            )
            
            # Create "building block" representation
            block = Rectangle(height=0.5, width=1).set_fill(colors[degree], opacity=0.8)
            block.set_stroke(WHITE, width=1)
            if len(building_blocks) > 0:
                block.next_to(building_blocks[-1], DOWN, buff=0.1)
            else:
                block.move_to(building_blocks.get_center())
            
            block_label = Tex(f"Term {degree}").scale(0.6).next_to(block, RIGHT)
            block_group = VGroup(block, block_label)
            building_blocks.add(block_group)
            
            # Add building block with pulsing effect
            self.play(
                FadeIn(block_group),
                run_time=0.7
            )
            
            # Create graph of the Taylor polynomial on right side
            approx_graph = right_axes.get_graph(
                taylor_func, 
                color=colors[degree]
            )
            
            # Create the Taylor polynomial formula
            taylor_formula = Tex(taylor_expressions[degree]).set_color(colors[degree])
            taylor_formula.scale(0.8).next_to(right_axes, DOWN)
            
            # Update convergence radius - grows with higher degrees
            new_radius = min(0.2 + degree*0.5, 3)  # Limit to reasonable size
            new_circle = Circle(radius=new_radius).set_stroke(YELLOW, opacity=0.3)
            new_circle.move_to(right_axes.c2p(0, 0))
            
            # Error region visualization
            if current_approx_graph and degree >= 3:  # Show error for interesting cases
                error_func = get_error_func(get_taylor_term(degree-1, x0))
                error_graph = right_axes.get_graph(
                    error_func,
                    color=RED_A,
                    stroke_opacity=0.8,
                )
                
                self.play(
                    ShowCreation(error_graph),
                    run_time=1
                )
                
                # Show improvement with new term
                self.wait(0.5)
                self.play(
                    FadeOut(error_graph),
                    run_time=0.7
                )
            
            # Replace the previous approximation with the new one
            if current_approx_graph:
                # Animation of term "fixing" the approximation
                self.play(
                    ReplacementTransform(current_approx_graph, approx_graph),
                    ReplacementTransform(current_formula, taylor_formula),
                    Transform(convergence_circle, new_circle),
                    run_time=1.5
                )
            else:
                self.play(
                    ShowCreation(approx_graph),
                    Write(taylor_formula),
                    FadeIn(convergence_circle),
                    run_time=1.5
                )
            
            current_approx_graph = approx_graph
            current_formula = taylor_formula
            
            # Show term attacking specific parts of the error
            term_right = right_axes.get_graph(
                term_func,
                color=colors[degree],
            )
            
            self.play(
                FadeIn(term_right),
                run_time=0.7
            )
            self.wait(0.3)
            self.play(
                FadeOut(term_right),
                run_time=0.5
            )
            
            # Fade out left term to prepare for next one
            self.play(
                FadeOut(term_graph),
                FadeOut(term_formula),
                run_time=0.7
            )
            
            # Add emotional indicators for each degree
            emotion_text = ""
            if degree == 0:
                emotion_text = "We begin our approximation journey..."
            elif degree == 1:
                emotion_text = "Linear approximation - a good start!"
            elif degree == 2:
                emotion_text = "Adding quadratic term..."
            elif degree == 3:
                emotion_text = "Cubic term makes a big difference!"
            elif degree == 4:
                emotion_text = "Getting even more accurate..."
            elif degree == 5:
                emotion_text = "Impressive accuracy with 5 terms!"
                
            emotion = Text(emotion_text, font_size=24, color=YELLOW)
            emotion.next_to(title, DOWN)
            
            self.play(FadeIn(emotion))
            self.wait(0.5)
            self.play(FadeOut(emotion))
            
        # Final dramatic pause
        self.wait(1)
        
        # Cleanup for final reveal
        self.play(
            FadeOut(left_title),
            FadeOut(right_title),
            FadeOut(left_original),
            FadeOut(right_original),
            FadeOut(left_axes),
            FadeOut(right_axes),
            FadeOut(current_formula),
            FadeOut(convergence_circle),
            FadeOut(building_blocks),
            FadeOut(title),
            FadeOut(degree_group),
            run_time=1.5
        )
            
    def final_reveal(self, axes, original_graph):
        # Restore original setup
        axes_new = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        axes_new.add_coordinate_labels()
        
        self.play(
            FadeIn(axes_new),
            run_time=1
        )
        
        # Show the final comparison
        final_function = axes_new.get_graph(lambda x: np.sin(x), color=BLUE)
        
        # Define the 5th degree Taylor polynomial
        def taylor_5(x):
            return x - (x**3)/6 + (x**5)/120
            
        final_approx = axes_new.get_graph(taylor_5, color=PURPLE_C)
        
        # Show both graphs
        self.play(
            ShowCreation(final_function),
            run_time=1.5
        )
        self.play(
            ShowCreation(final_approx),
            run_time=1.5
        )
        
        # Error visualization
        error_func = lambda x: np.sin(x) - taylor_5(x)
        error_graph = axes_new.get_graph(error_func, color=RED_E, stroke_width=2)
        
        # Highlight the tiny error
        self.play(
            ShowCreation(error_graph),
            run_time=1
        )
        
        # Show the error decreasing as we zoom out
        error_label = Text("Error decreases as we add more terms", font_size=36, color=YELLOW)
        error_label.to_edge(UP)
        
        self.play(Write(error_label))
        self.wait(1)
        
        # Final message with dramatic reveal
        final_message = Tex(
            "\\text{Taylor series for } \\sin(x) \\text{ around } x_0 = 0:",
            "\\sin(x) = x - \\frac{x^3}{3!} + \\frac{x^5}{5!} - \\frac{x^7}{7!} + \\ldots"
        ).arrange(DOWN)
        
        final_message.scale(1.2)
        
        # Add a background for better readability
        background = Rectangle(
            width=final_message.get_width() + 1,
            height=final_message.get_height() + 0.5,
            fill_color=BLACK,
            fill_opacity=0.8,
            stroke_width=0
        )
        background.move_to(final_message)
        
        final_group = VGroup(background, final_message)
        final_group.to_edge(DOWN)
        
        self.play(
            FadeIn(background),
            Write(final_message),
            run_time=2
        )
        
        # Add a final thought
        final_thought = Text("Infinite precision with infinite terms", font_size=32, color=YELLOW)
        final_thought.next_to(final_message, DOWN)
        
        self.play(
            Write(final_thought),
            run_time=1.5
        )
        
        # Final dramatic pause
        self.wait(2) 