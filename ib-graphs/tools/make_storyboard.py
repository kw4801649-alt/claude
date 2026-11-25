#!/usr/bin/env python3
"""
tools/make_storyboard.py -- Write docs/02_storyboard.md for "Reading Motion and Momentum Graphs".

Every beat is anchored to the phrase of the narration that triggers it (the same phrases
scene/index.html passes to cue()), so the timecodes come from the real audio in
audio/timings.json. Re-run after tools/tts.py.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TL = json.loads((ROOT / "audio" / "timings.json").read_text("utf-8"))


def cue(sid: str, phrase: str) -> float:
    sc, p = TL["scenes"][sid], phrase.lower()
    for seg in sc["segments"]:
        for s in seg["sentences"]:
            idx = s["text"].lower().find(p)
            if idx >= 0:
                return sc["start"] + s["start"] + idx / len(s["text"]) * (s["end"] - s["start"])
    raise SystemExit(f"cue not found: {sid} {phrase!r}")


def tc(x: float) -> str:
    return f"{int(x // 60)}:{x % 60:04.1f}"


ROWS = [
    ("s01", None, "A zoo of coloured curves draws itself across the sheet behind the title.", "Reading motion & momentum graphs", "Start on panel 1."),
    ("s01", "take the gradient", "The words gradient (amber) and area (cyan) are written large.", "gradient / area", "Hold."),
    ("s01", "Watch a cart", "Title fades; a cart speeds up, cruises, brakes while displacement, velocity and acceleration graphs draw live with a shared time cursor.", "s, v, a graphs; v and a arrows on the cart", "Hold."),
    ("s01", "Gradient takes you down the ladder", "Circles s, v, a appear; arrows run down (gradient) then up (area).", "ladder s -> v -> a", "Hold."),
    ("s01", "Then we'll use the same two moves", "A second ladder p, F appears beside it.", "ladder p -> F", "Swoop to panel 2."),
    ("s02", "rise over run", "A straight s-t line; dashed run and rise legs and a gradient label.", "gradient = Δs/Δt", "Panel 2."),
    ("s02", "The area is the vertical quantity", "A constant v-t line with a shaded rectangle.", "area = v × t", "Hold."),
    ("s02", "read the units", "Units written out under each graph: m/s is velocity, m/s × s is displacement.", "Δs/Δt → m s⁻¹; v × t → m", "Hold."),
    ("s02", "what are the axes", "The rule is handwritten along the bottom.", "gradient = vertical ÷ horizontal · area = vertical × horizontal", "Swoop to panel 3."),
    ("s03", "straight line", "Cart moves at 3, then 1.5, then 0, then -2 m/s; the s-t line draws with each slope labelled.", "v = 3, 1.5, 0, -2", "Panel 3."),
    ("s03", "Underneath", "v-t steps and the flat a-t line draw underneath.", "v-t steps; a = 0", "Hold."),
    ("s03", "The area under it", "Rectangles under the steps fill cyan (positive) and red (negative).", "Δs = vΔt", "Swoop to panel 4."),
    ("s04", "flat line", "Cart accelerates; the a-t flat line draws.", "a-t graph", "Panel 4."),
    ("s04", "the area under it", "The rectangle under a-t fills amber.", "Δv = a t", "Hold."),
    ("s04", "That makes the velocity-time graph", "Cart replays; v-t straight line draws; dashed rise/run triangle.", "a = Δv/Δt", "Hold."),
    ("s04", "And on the displacement-time graph", "Cart replays; s-t parabola draws.", "s-t graph", "Hold."),
    ("s04", "At every moment", "A tangent slides along s-t; a dot on v-t rises with it, joined by a vertical guide.", "slope of s-t = height of v-t", "Swoop to panel 5."),
    ("s05", "Start at the initial velocity", "One big v-t line from u to v; labels u, v, t.", "u, v, t", "Panel 5."),
    ("s05", "The gradient is the acceleration", "A dashed gradient triangle.", "a = (v-u)/t → v = u + at", "Hold."),
    ("s05", "Split it into a rectangle", "Rectangle (cyan) and triangle (green) fill under the line.", "rectangle = ut; triangle = ½t(at)", "Hold."),
    ("s05", "Add them", "A bracket marks 'at'.", "s = ut + ½at²", "Hold."),
    ("s05", "one trapezoid", "Both shapes merge into one outlined trapezoid.", "s = ½(u+v)t", "Hold."),
    ("s05", "eliminate the time", "The last equation writes itself.", "v² = u² + 2as", "Swoop to panel 6."),
    ("s06", "Pick two points", "Two dots on the s-t parabola.", "", "Panel 6."),
    ("s06", "join them", "A chord is drawn with its Δt, Δs triangle and a live gradient readout.", "chord gradient = average velocity", "Hold."),
    ("s06", "Now slide one point", "The second point slides toward the first; the readout falls toward 4.0 m/s.", "", "Hold."),
    ("s06", "becomes the tangent", "The chord swings into the tangent line.", "tangent gradient = instantaneous velocity", "Hold."),
    ("s06", "A common mistake", "Two red points on the curve (✗) slide onto the tangent line (✓) with a dashed triangle.", "two points on the tangent", "Swoop to panel 7."),
    ("s07", "The velocity starts positive", "A ball is thrown up on the right; s-t, v-t and a-t graphs draw live.", "a = -9.81 throughout", "Panel 7."),
    ("s07", "even at the top", "A vertical guide at t = 2 s: v = 0 but a = -9.81; a flat tangent at the top of s-t.", "v = 0, a = -9.81", "Hold."),
    ("s07", "The area above the axis", "Positive triangle (cyan) then negative triangle (red) fill on v-t.", "+19.6 m, -19.6 m", "Hold."),
    ("s07", "displacement is zero", "Displacement and distance lines.", "Δs = 0; distance = 39.2 m", "Swoop to panel 8."),
    ("s08", "Drop a ball into oil", "A ball sinks in a tube with weight and growing drag arrows; v-t levels off; a-t decays.", "terminal velocity line", "Panel 8."),
    ("s08", "counting squares", "A square grid overlays the shaded area.", "area ≈ count squares", "Hold."),
    ("s08", "acceleration is still the gradient", "A tangent slides along v-t while a dot follows on a-t.", "constant-a equations ✗", "Swoop to panel 9."),
    ("s09", "A projectile is two motions at once", "A ball flies a parabola; x-t, vx-t, y-t, vy-t graphs draw in two columns.", "horizontal / vertical", "Panel 9."),
    ("s09", "At the top", "A ghost ball at the apex: vy = 0 on its graph, vx = 10 unchanged.", "v_y = 0, v_x = 10", "Swoop to panel 10."),
    ("s10", "Now forces and momentum", "A 2 kg cart accelerates then brakes; v-t and p-t draw (p = 2 × v).", "p = mv", "Panel 10."),
    ("s10", "So the gradient of a momentum-time graph", "The cart replays; a tangent slides along p-t while F-t draws beneath it.", "F = Δp/Δt", "Hold."),
    ("s10", "A steep line", "Each segment of p-t is highlighted with what it means.", "steep → big force · flat → none · down → opposite", "Swoop to panel 11."),
    ("s11", "the area under a force-time graph", "A constant-force rectangle fills lime; then a curve with a grid for counting squares.", "J = FΔt = Δp; N s = kg m s⁻¹", "Panel 11."),
    ("s11", "Take a triangular pulse", "6000 N, 10 ms triangle.", "J = ½ × 0.010 × 6000 = 30 N s", "Hold."),
    ("s11", "hits a wall", "A negative rectangle fills red while a ball hits a wall and rebounds.", "J = -4.5 N s; F_avg = -450 N", "Swoop to panel 12."),
    ("s12", "Start with a force-time graph", "A push builds, holds, fades.", "F-t graph", "Panel 12."),
    ("s12", "While the force is growing", "The area under F-t accumulates as the p-t curve draws; the cart moves.", "p-t = running total", "Hold."),
    ("s12", "Divide by the mass", "v-t has the same shape as p-t.", "÷ 4 kg", "Hold."),
    ("s12", "Force is to momentum", "Two ladders: p → F and s → v.", "gradient down, area up", "Swoop to panel 13."),
    ("s13", "Drop an egg on concrete", "An egg breaks on concrete (tall, narrow F-t spike).", "concrete: short, tall", "Panel 13."),
    ("s13", "Drop it on a pillow", "An egg sinks into a pillow (low, wide F-t hill).", "same area = same Δp", "Hold."),
    ("s13", "a bounce hits harder", "A stop and a bounce on one F-t graph; the bounce has twice the area.", "Δp = mu, Δp = 2mu", "Swoop to panel 14."),
    ("s14", "Finally, a collision between two carts", "Cart 1 (2 kg) hits cart 2 (1 kg); equal and opposite force arrows; F-t pulses are mirror images.", "mirror images", "Panel 14."),
    ("s14", "equal and opposite", "Areas fill and are labelled.", "J₁ = -J₂", "Hold."),
    ("s14", "Now plot the momentum", "The collision replays; p₁ falls, p₂ rises, the total stays flat.", "p₁ + p₂ = constant", "Swoop to panel 15."),
    ("s15", "gradients go down", "Both ladders, with units.", "s → v → a; p → F", "Panel 15."),
    ("s15", "What are the axes", "Three questions are handwritten.", "1 axes · 2 gradient/area · 3 signs", "Pull back to the whole sheet."),
]

lines = ["# Reading Motion and Momentum Graphs — storyboard", "",
         "_Generated by `tools/make_storyboard.py` from the measured narration; every beat fires on its spoken phrase._", "",
         "**Look:** one long blueprint-style sheet; the camera glides (and swoops out) from graph to graph. "
         "Colour = quantity: displacement cyan, velocity amber, acceleration pink, force coral, momentum lime; shaded areas take the colour of what they produce. "
         "Every curve is drawn live while a cart, ball or projectile moves. Maths typeset with KaTeX; notes handwritten (Caveat). "
         "No interface bars or cards. 16:9, 1920×1080, 30 fps.", "",
         "| # | Time | Anchor (spoken) | Visual / motion | On the page | Camera |", "|---|---|---|---|---|---|"]
for i, (sid, phrase, vis, page, cam) in enumerate(ROWS, 1):
    t = TL["scenes"][sid]["start"] if phrase is None else cue(sid, phrase)
    lines.append(f"| {i} | {tc(t)} | {('“' + phrase + '”') if phrase else sid + ' start'} | {vis} | {page} | {cam} |")
lines += ["", f"**End: {tc(TL['total'])} ({TL['total']:.2f} s).**", ""]
(ROOT / "docs" / "02_storyboard.md").write_text("\n".join(lines), "utf-8")
print("Wrote docs/02_storyboard.md")
