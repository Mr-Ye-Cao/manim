from manimlib import *
import numpy as np

class TaylorSeriesIllustration(Scene):
    def construct(self):
        # Set up the axes
        axes = Axes(
            x_range=(-5, 5),
            y_range=(-2, 2),
            axis_config={"include_tip": False},
        )
        axes.add_coordinate_labels()
        self.play(Write(axes))
        
        # Define the function to approximate (sine function)
        def func(x):
            return np.sin(x)
        
        # Create the original function graph
        original_graph = axes.get_graph(
            func,
            color=BLUE,
        )
        function_label = Tex("f(x) = \\sin(x)").set_color(BLUE).to_corner(UL)
        
        self.play(
            ShowCreation(original_graph),
            Write(function_label)
        )
        self.wait()
        
        # Point around which we'll create the Taylor series
        x0 = 0
        point = Dot(axes.c2p(x0, func(x0)), color=YELLOW)
        point_label = Tex(f"x_0 = {x0}").next_to(point, UR, buff=0.1).set_color(YELLOW)
        
        self.play(
            FadeIn(point),
            Write(point_label)
        )
        
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
        
        # Initialize comparison area
        comparison_text = Tex("\\text{Adding Taylor series terms:}").to_edge(UP)
        self.play(Write(comparison_text))
        
        current_approx_graph = None
        current_formula = None
        
        for degree in range(6):
            # Get the Taylor polynomial function
            taylor_func = get_taylor_term(degree, x0)
            
            # Create visualization of just this term being added
            term_func = get_individual_term(degree, x0)
            
            # Create graph of the current term
            term_graph = axes.get_graph(
                term_func,
                color=colors[degree],
            )
            
            # Create the term's formula
            term_formula = Tex(terms_tex[degree]).set_color(colors[degree])
            term_formula.to_corner(UR)
            
            # Show the new term
            self.play(
                ShowCreation(term_graph),
                Write(term_formula)
            )
            self.wait(0.5)
            
            # Create graph of the Taylor polynomial up to this degree
            approx_graph = axes.get_graph(
                taylor_func, 
                color=colors[degree]
            )
            
            # Create the Taylor polynomial formula
            taylor_formula = Tex(taylor_expressions[degree]).set_color(colors[degree])
            taylor_formula.to_edge(DOWN)
            
            # Replace the previous approximation with the new one
            if current_approx_graph:
                self.play(
                    ReplacementTransform(current_approx_graph, approx_graph),
                    ReplacementTransform(current_formula, taylor_formula),
                    FadeOut(term_graph),
                    FadeOut(term_formula)
                )
            else:
                self.play(
                    ShowCreation(approx_graph),
                    Write(taylor_formula),
                    FadeOut(term_graph),
                    FadeOut(term_formula)
                )
            
            current_approx_graph = approx_graph
            current_formula = taylor_formula
            
            # Wait a bit longer for the last approximation
            if degree == 5:
                # Show error message
                error_message = Tex("\\text{Better approximation with more terms!}").set_color(YELLOW)
                error_message.next_to(taylor_formula, DOWN)
                self.play(Write(error_message))
                
            self.wait()
        
        # Final message
        final_message = Tex(
            "\\text{Taylor series for } \\sin(x) \\text{ around } x_0 = 0:",
            "\\sin(x) = x - \\frac{x^3}{3!} + \\frac{x^5}{5!} - \\frac{x^7}{7!} + \\ldots"
        ).arrange(DOWN)
        
        final_message.to_edge(DOWN)
        self.play(
            FadeOut(current_formula),
            FadeOut(error_message),
            Write(final_message)
        )
        
        self.wait(2) 