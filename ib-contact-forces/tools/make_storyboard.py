#!/usr/bin/env python3
"""
tools/make_storyboard.py -- Write docs/02_storyboard.md for "Contact Forces, Derived".

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
    ("s01", None, "Hand-lettered title writes itself on graph paper; a slope and block are pen-drawn.", "—", "Panel 1."),
    ("s01", "draw the forces", "The weight arrow mg grows from the block.", "mg", "Hold."),
    ("s01", "where does mg sin θ", "Two dashed component arrows appear with question marks.", "mg sin θ ?  mg cos θ ?", "Hold."),
    ("s01", "the normal force", "Five small icons draw in, one per spoken force: normal, friction, tension, buoyancy, drag.", "handwritten names", "Hold."),
    ("s01", "No springs", "“no springs / no circles / no kinematics” written and struck through in red.", "—", "Glide to panel ①."),
    ("s02", "A force is an arrow", "A blue force F at angle θ; dashed perpendicular components appear.", "hypotenuse", "Panel ①."),
    ("s02", "Cosine is adjacent", "Labels turn into F cos θ and F sin θ as the equations write themselves.", "cos θ = adj/hyp ⇒ adj = F cos θ; sin θ = opp/hyp ⇒ opp = F sin θ", "Hold."),
    ("s02", "Swing the angle", "θ swings between ~10° and ~60°; components grow and shrink live, with a running readout.", "(F cos θ)² + (F sin θ)² = F²; θ, cos θ, sin θ readout", "Hold."),
    ("s02", "The rule to remember", "The rule is handwritten across the bottom.", "cos → the side touching θ · sin → the side across", "Glide to ②."),
    ("s03", "a block resting", "Block on a table; mg down, F_N up; right-angle mark shows ‘normal’ = perpendicular.", "ΣF_y = 0 → F_N − mg = 0 → F_N = mg", "Panel ②."),
    ("s03", "not a Newton's third law pair", "Red note; the Earth appears below with the true partner force (block pulls Earth up).", "✗ not a 3rd-law pair · both act ON the block", "Hold."),
    ("s04", "Now pull the block", "A rope pulls at θ; F splits into F cos θ and F sin θ.", "F cos θ, F sin θ", "Panel ③."),
    ("s04", "the normal force plus F sin θ", "F_N shrinks visibly as the pull grows.", "F_N + F sin θ = mg → F_N = mg − F sin θ", "Hold."),
    ("s04", "Push down at the same angle", "The force swaps to a push from above; F_N grows.", "F_N = mg + F sin θ", "Hold."),
    ("s04", "Since friction is proportional", "A friction arrow ∝ F_N; the diagram toggles pull ↔ push and friction shrinks / grows.", "F_f = μF_N; pull up ⇒ F_N↓ ⇒ friction↓; push down ⇒ F_N↑ ⇒ friction↑", "Glide to ④."),
    ("s05", "what you feel", "A lift cabin with ‘you’ on bathroom scales; the cabin moves; F_N stretches and shrinks; the scale reads 686 → 826 → 546 N.", "a (not a force); F_N − mg = ma → F_N = m(g + a); F_N = m(g − a)", "Panel ④."),
    ("s06", "a block on a slope", "Pen-drawn incline; mg straight down; F_N perpendicular to the slope.", "mg, F_N", "Panel ⑤."),
    ("s06", "So tilt your point of view", "The whole sheet rotates by θ so the slope is level; axes x∥ and y⊥ are drawn.", "x∥, y⊥", "Camera rotates the paper by 30°, then back."),
    ("s06", "Start with the slope flat", "The slope flattens to 0°: its perpendicular lies exactly along mg. Then it tilts back to θ and the perpendicular tilts with it, opening an angle θ against mg.", "perpendicular lies along mg; tilt the slope by θ → its perpendicular tilts by θ", "Hold."),
    ("s06", "Read the triangle", "Dashed components mg cos θ (into slope) and mg sin θ (down slope); the triangle lifts off the page and turns upright beside the diagram.", "upright triangle: hyp mg, adj mg cos θ, opp mg sin θ; F∥ = mg sin θ; F_N = mg cos θ", "Hold."),
    ("s06", "Check the extremes", "The slope animates to 0° then ~90° (a wall); components update live.", "θ, sin θ, cos θ readout", "Glide to ⑥."),
    ("s07", "Add friction", "Friction up the slope, with a red tick marking its maximum μs F_N.", "F_f ≤ μs F_N; F_f = mg sin θ (static)", "Panel ⑥."),
    ("s07", "Raise the angle", "The slope steepens; a graph draws mg sin θ rising and μs mg cos θ falling; a dot tracks the angle.", "graph: mg sin θ vs μs mg cos θ", "Hold."),
    ("s07", "Set them equal", "The curves cross; mg cancels with strike-throughs.", "mg sin θ = μs mg cos θ → μs = sin θ/cos θ = tan θ; tan θ_c = μs", "Hold."),
    ("s07", "Once it slides", "The block slips down the slope; friction drops to μd F_N.", "F_net = mg sin θ − μd mg cos θ", "Glide to ⑦."),
    ("s08", "horizontal push F", "Horizontal F on a smooth slope; it is split too; the angle between F and the slope is shown to be θ.", "F cos θ (up slope), F sin θ (into slope)", "Panel ⑦."),
    ("s08", "F cos θ balances mg sin θ", "Weight components fade in; F_N grows to balance both.", "F cos θ = mg sin θ → F = mg tan θ; F_N = mg cos θ + F sin θ = mg / cos θ > mg", "Glide to ⑧."),
    ("s09", "Hang a mass from a single string", "Single string: T up, mg down.", "T = mg", "Panel ⑧."),
    ("s09", "Now hang a lamp", "A lamp on two strings at α; each tension splits into T cos α and T sin α.", "2T sin α = mg → T = mg / (2 sin α)", "Hold."),
    ("s09", "Flatten the strings", "α shrinks to 8°: the lamp rises and the tension arrows shoot out; a readout shows T ≈ 3.6 mg.", "α → 0 ⇒ T → ∞", "Hold."),
    ("s09", "With unequal angles", "Asymmetric strings (30°, 60°); then copies of the three forces slide nose to tail into a closed triangle.", "T₁ cos α₁ = T₂ cos α₂; T₁ sin α₁ + T₂ sin α₂ = mg", "Glide to ⑨."),
    ("s10", "Tie a block", "Block M on a table, string over a pulley to mass m; the system moves; the same T acts on both.", "same T, new direction; mg − T = ma; T = Ma; ⇒ T = M/(M+m)·mg < mg", "Panel ⑨."),
    ("s11", "put a block", "A block in a tank; pressure arrows grow with depth; side arrows cancel; F_b appears.", "F_b = p_bottom A − p_top A = (ρgh)A = ρ(hA)g = ρVg", "Panel ⑩."),
    ("s11", "A floating object", "A lighter block rises and floats; the submerged volume is hatched; F_b balances mg.", "ρ V_sub g = mg", "Glide to ⑪."),
    ("s12", "Stokes' law gives the drag", "A ball bearing in oil with its radius marked.", "F_d = 6πηrv; small · slow · smooth (laminar)", "Panel ⑪."),
    ("s12", "Drop a ball bearing", "It sinks; F_d grows with speed until F_b + F_d reaches the mg line: terminal speed.", "mg = F_b + 6πηr v_t → … → v_t = 2r²g(ρs − ρf)/9η", "Hold."),
    ("s13", "Every contact force", "The camera pulls back over the whole worksheet; a four-step recipe is written across it.", "isolate · axes · split · balance", "Zoom out to the full sheet."),
    ("s13", "So mg sin θ isn't", "Dive back into the incline; the mg sin θ side glows.", "just one side of a triangle", "Zoom into panel ⑤; fade to paper."),
]

lines = ["# Contact Forces, Derived — storyboard", "",
         "_Generated by `tools/make_storyboard.py` from the measured narration; every beat fires on its spoken phrase._", "",
         "**Look:** one long sheet of graph paper; the camera glides from diagram to diagram (and once turns the paper). "
         "Pen-drawn vectors with a fixed colour code: weight orange, normal teal, friction raspberry, tension green, "
         "applied force blue, buoyancy sky-blue, drag violet; components dashed; acceleration grey dashed (never a force). "
         "Maths typeset with KaTeX; notes handwritten (Caveat). No interface bars or cards. 16:9, 1920×1080, 30 fps.", "",
         "| # | Time | Anchor (spoken) | Visual / motion | On the page | Camera |", "|---|---|---|---|---|---|"]
for i, (sid, phrase, vis, page, cam) in enumerate(ROWS, 1):
    t = TL["scenes"][sid]["start"] if phrase is None else cue(sid, phrase)
    lines.append(f"| {i} | {tc(t)} | {('“' + phrase + '”') if phrase else sid + ' start'} | {vis} | {page} | {cam} |")
lines += ["", f"**End: {tc(TL['total'])} ({TL['total']:.2f} s).**", ""]
(ROOT / "docs" / "02_storyboard.md").write_text("\n".join(lines), "utf-8")
print("Wrote docs/02_storyboard.md")
