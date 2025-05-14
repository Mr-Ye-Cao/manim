from manimlib import *

class DerivativeIllustration(Scene):
    def construct(self):
        # Set up the axes
        axes = Axes(
            x_range=(-1, 5),
            y_range=(-1, 5),
            axis_config={"include_tip": False},
        )
        axes.add_coordinate_labels()
        self.play(Write(axes))

        # Create a function graph (we'll use f(x) = x^2)
        def func(x):
            return x**2
            
        graph = axes.get_graph(
            func,
            color=BLUE,
        )
        graph_label = Tex("f(x) = x^2").set_color(BLUE).to_corner(UL)
        
        self.play(
            ShowCreation(graph),
            FadeIn(graph_label)
        )
        
        # Point on the curve
        x = 2
        dot = Dot(axes.c2p(x, func(x)), color=YELLOW)
        dot_label = Tex(f"({x}, {func(x)})").next_to(dot, UR, buff=0.1).set_color(YELLOW)
        
        self.play(
            FadeIn(dot),
            Write(dot_label)
        )
        
        # Tangent line at the point
        def get_tangent_line(x, graph, axes):
            dx = 0.001
            dy = func(x + dx) - func(x)
            slope = dy / dx  # Approximate derivative
            
            tangent = axes.get_graph(
                lambda t: func(x) + slope * (t - x),
                color=GREEN,
                x_range=[x - 2, x + 2]
            )
            return tangent, slope
        
        tangent, slope = get_tangent_line(x, graph, axes)
        tangent_label = Tex(f"\\text{{Slope}} = {2*x}").set_color(GREEN).to_corner(UR)
        
        self.play(
            ShowCreation(tangent),
            Write(tangent_label)
        )
        
        # Show secant lines approaching the tangent line
        def get_secant_line(x1, x2, graph, axes):
            y1 = func(x1)
            y2 = func(x2)
            secant = Line(
                axes.c2p(x1, y1),
                axes.c2p(x2, y2),
                color=RED
            )
            slope = (y2 - y1) / (x2 - x1)
            return secant, slope
        
        # Initialize a secant line at a distance
        x2 = 3.5
        secant, secant_slope = get_secant_line(x, x2, graph, axes)
        secant_label = Tex(f"\\text{{Secant slope}} = {secant_slope:.2f}").set_color(RED)
        secant_label.to_corner(DR)
        
        self.play(
            ShowCreation(secant),
            Write(secant_label)
        )
        
        # Animation to show secant line approaching tangent
        points = [3.5, 3.0, 2.5, 2.25, 2.1, 2.01]
        for new_x2 in points:
            new_secant, new_slope = get_secant_line(x, new_x2, graph, axes)
            new_secant_label = Tex(f"\\text{{Secant slope}} = {new_slope:.2f}").set_color(RED)
            new_secant_label.to_corner(DR)
            
            self.play(
                ReplacementTransform(secant, new_secant),
                ReplacementTransform(secant_label, new_secant_label)
            )
            
            secant = new_secant
            secant_label = new_secant_label
            
        # Final message about the derivative
        derivative_text = Tex(
            "\\text{The derivative } f'(x) \\text{ is the slope of the tangent line}",
            "\\text{In this case, } f'(2) = 4"
        ).arrange(DOWN)
        derivative_text.to_edge(DOWN)
        
        self.play(Write(derivative_text))
        self.wait(2) 