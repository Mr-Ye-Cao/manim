from manimlib import *
import numpy as np
ParametricFunction = ParametricCurve  # alias for backward compatibility

class BlackHolePhotonSphere(Scene):
    def construct(self):
        # 0-3s: Cold-open hook: "Where does light take a selfie?"
        photon_sphere_path = Circle(radius=2, color=WHITE).set_opacity(0)
        dot = Dot(color=WHITE).move_to(LEFT * 5)
        traced_path = TracedPath(dot.get_center, stroke_color=WHITE, stroke_width=2)
        self.add(photon_sphere_path, dot, traced_path)
        arc = Arc(radius=2, start_angle=PI, angle=-1.2).set_opacity(0)
        self.play(MoveAlongPath(dot, arc), run_time=3)
        self.wait(0.1)

        # 3-5s: Reveal the black hole & label zones
        event_horizon = Circle(radius=1, fill_color=BLACK, fill_opacity=1)
        photon_ring = Circle(radius=1.5, stroke_color=YELLOW, stroke_width=4)
        photon_ring_layer = GlowDots(points=photon_ring.get_points(), color=YELLOW, radius=0.1)
        accretion_flow = Circle(radius=1.8, stroke_color=RED, stroke_width=6, stroke_opacity=0.3)
        label_photon = Tex("Photon Sphere", font_size=24).next_to(photon_ring, RIGHT, buff=0.2)
        arrow_photon = Arrow(label_photon.get_left(), photon_ring.get_top())
        label_accrete = Tex("Accretion Flow", font_size=24).next_to(accretion_flow, RIGHT, buff=0.2)
        arrow_accrete = Arrow(label_accrete.get_left(), accretion_flow.get_top())
        self.play(
            FadeIn(event_horizon),
            FadeIn(photon_ring),
            GrowFromCenter(photon_ring_layer),
            FadeIn(accretion_flow),
            Write(label_photon),
            Write(arrow_photon),
            Write(label_accrete),
            Write(arrow_accrete),
            run_time=2
        )
        self.wait(0.1)

        # 5-10s: Light-ray playground
        blue_path = ParametricFunction(
            lambda t: np.array([t, 2 * np.tanh(t / 2), 0]),
            t_range=(-5, 5, 0.1),
            color=BLUE,
            stroke_width=2,
            stroke_opacity=0.6,
        )
        blue_dot = Dot(color=BLUE).move_to(blue_path.point_from_proportion(0))
        blue_trace = TracedPath(blue_dot.get_center, stroke_color=BLUE, stroke_width=2, time_traced=np.inf)

        def yellow_func(t):
            if t < 2:
                return np.array([-5 + t * 2.5, 0.5, 0])
            elif t < 8:
                angle = (t - 2) / 6 * TAU * 1.5 + PI
                return 1.5 * np.array([np.cos(angle), np.sin(angle), 0])
            else:
                s = (t - 8) / 2
                return np.array([5 - s * 3, -0.5, 0])

        yellow_path = ParametricFunction(
            yellow_func,
            t_range=(0, 10, 0.1),
            color=YELLOW,
            stroke_width=2,
            stroke_opacity=0.6,
        )
        yellow_dot = Dot(color=YELLOW).move_to(yellow_path.point_from_proportion(0))
        yellow_trace = TracedPath(yellow_dot.get_center, stroke_color=YELLOW, stroke_width=2, time_traced=np.inf)

        red_path = ParametricFunction(
            lambda t: np.array([
                (5 - t) / 5 * 3 * np.cos(t / 2),
                (5 - t) / 5 * 3 * np.sin(t / 2),
                0
            ]),
            t_range=(0, 5, 0.1),
            color=RED,
            stroke_width=2,
            stroke_opacity=0.6,
        )
        red_dot = Dot(color=RED).move_to(red_path.point_from_proportion(0))
        red_trace = TracedPath(red_dot.get_center, stroke_color=RED, stroke_width=2, time_traced=np.inf)

        self.add(
            blue_dot, blue_trace,
            yellow_dot, yellow_trace,
            red_dot, red_trace
        )
        self.play(
            MoveAlongPath(blue_dot, blue_path, rate_func=linear),
            MoveAlongPath(yellow_dot, yellow_path, rate_func=linear),
            MoveAlongPath(red_dot, red_path, rate_func=linear),
            run_time=5
        )
        self.wait(0.1)
        # Freeze traced paths so they do not change during fade animations
        blue_trace.clear_updaters()
        red_trace.clear_updaters()
        yellow_trace.clear_updaters()

        # 10-14s: Build the "shadow"
        critical_ring = yellow_trace.copy().set_stroke(width=8, opacity=1)
        critical_ring.clear_updaters()
        dimmer = FullScreenRectangle(fill_color=BLACK, fill_opacity=0.5)
        self.play(
            FadeOut(blue_trace),
            FadeOut(blue_dot),
            FadeOut(red_trace),
            FadeOut(red_dot),
            FadeIn(dimmer),
            ShowCreation(critical_ring),
            run_time=4
        )
        self.wait(0.1)

        # 14-18s: Camera push-in + photon racetrack
        photon_dots = VGroup(*[
            Dot(color=WHITE, radius=0.05).move_to(1.5 * np.array([np.cos(a), np.sin(a), 0]))
            for a in np.linspace(0, TAU, 30)
        ])
        photon_dots.add_updater(lambda m, dt: m.rotate(2 * dt, about_point=ORIGIN))
        self.add(photon_dots)
        self.play(self.camera.frame.animate.scale(0.6).move_to(ORIGIN), run_time=4)
        self.wait(0.1)

        # 18-24s: Connection to real image - dashed ring placeholder
        eht_overlay = DashedVMobject(Circle(radius=1.5), num_dashes=60)
        self.add(eht_overlay)
        self.wait(6)
        self.remove(eht_overlay)
        self.wait(0.1)

        # 24-30s: Takeaway text & outro spark
        takeaway = Text(
            "The photon sphere:\nlight's last stable orbit,\nsketching every black hole's silhouette.",
            font_size=30
        )
        self.play(Write(takeaway), run_time=2)
        self.wait(1)
        self.play(FadeOut(takeaway), run_time=1)
        logo = ImageMobject("logo/white_with_name.png", height=1)
        self.play(FadeIn(logo), run_time=2)
        self.wait() 