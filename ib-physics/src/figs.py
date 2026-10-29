"""Redraw every figure of the IB Physics SL Kinematics guide with matplotlib.

Style follows the reference textbook chapters: Computer Modern (CMU Serif)
text, italic math variables, boxed axes with inward ticks, thin black lines
and a few restrained accent colours. All curves are computed from the
physics (SUVAT, or numerical integration with quadratic drag), never drawn
by hand.
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, FancyBboxPatch, Arc, Polygon

OUT = sys.argv[1]

# CMU Serif Bold is flagged "expanded", which stops matplotlib matching it for weight="bold"
from matplotlib import font_manager as _fm
import dataclasses as _dc
_fm.fontManager.ttflist = [_dc.replace(_f, stretch="normal") if _f.name == "CMU Serif" else _f
                           for _f in _fm.fontManager.ttflist]
_fm.fontManager._findfont_cached.cache_clear()
G = 9.81

plt.rcParams.update({
    "font.family": "CMU Serif",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "axes.labelsize": 10.5,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.minor.size": 2.5,
    "ytick.minor.size": 2.5,
    "lines.linewidth": 1.3,
    "axes.unicode_minus": True,
    "legend.frameon": True,
    "legend.edgecolor": "black",
    "legend.fancybox": False,
    "legend.framealpha": 1.0,
    "savefig.dpi": 300,
})

BLUE = "#1f3f99"
RED = "#b3202a"
GREEN = "#1d7a3a"
ORANGE = "#c46a00"
GREY = "0.45"
EARTH = "#6b5536"
EARTHFILL = "#e9e1d3"

sizes = {}


def save(fig, name, width):
    """Save at the size it will be printed so the fonts come out at true size."""
    fig.savefig(f"{OUT}/{name}.png", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    sizes[name] = width


def arrow(ax, x0, y0, x1, y1, color="black", lw=1.4, ms=10, style="-|>", ls="-", z=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0, zorder=z))


def dimline(ax, x0, y0, x1, y1, color=GREY, lw=0.8):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="<|-|>", mutation_scale=7,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=3))


def plain_axes(ax):
    """Axes for schematic diagrams: no box, no ticks."""
    ax.set_axis_off()


def ground(ax, x0, x1, y=0.0):
    ax.plot([x0, x1], [y, y], color=EARTH, lw=1.6, zorder=2)


# ---------------------------------------------------------------- Figure 1.1
def fig_concept():
    w = 5.9
    fig, ax = plt.subplots(figsize=(w, 4.1))
    ax.set_xlim(-0.1, 12.2)
    ax.set_ylim(0.4, 8.3)
    plain_axes(ax)

    def box(cx, cy, bw, bh, title, sub=None, ec="black", fc="white"):
        ax.add_patch(FancyBboxPatch((cx - bw / 2, cy - bh / 2), bw, bh,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    ec=ec, fc=fc, lw=1.0, zorder=2))
        if sub:
            ax.text(cx, cy + 0.19, title, ha="center", va="center", fontsize=9.5, weight="bold", zorder=3)
            ax.text(cx, cy - 0.22, sub, ha="center", va="center", fontsize=8.5, zorder=3)
        else:
            ax.text(cx, cy, title, ha="center", va="center", fontsize=9.5, zorder=3)

    y0 = 7.45
    box(1.45, y0, 2.6, 1.05, r"Position  $s$", "(where is it?)")
    box(5.95, y0, 3.5, 1.05, r"Velocity  $v$", "(how fast, which way?)")
    box(10.3, y0, 3.2, 1.05, r"Acceleration  $a$", r"(how is $v$ changing?)")
    for xa, xb in [(2.75, 4.2), (7.7, 8.7)]:
        arrow(ax, xa, y0 + 0.22, xb, y0 + 0.22, color=BLUE, lw=1.3)
        arrow(ax, xb, y0 - 0.22, xa, y0 - 0.22, color=RED, lw=1.3)
        ax.text((xa + xb) / 2, y0 + 0.55, "gradient", color=BLUE, ha="center", va="bottom", fontsize=9, style="italic")
        ax.text((xa + xb) / 2, y0 - 0.55, "area", color=RED, ha="center", va="top", fontsize=9, style="italic")
    ax.text(0.1, 6.05, "Blue arrows: read the slope of a graph.\nRed arrows: find the area under a graph.",
            fontsize=8, color="0.25", va="center")

    box(10.25, 5.2, 3.7, 0.95, r"If $a$ is CONSTANT", None)
    ax.text(10.2, 5.0, r"$\rightarrow$ SUVAT equations", ha="center", va="center", fontsize=9.5, zorder=3)
    ax.texts[-2].set_position((10.2, 5.4))
    ax.texts[-2].set_weight("bold")
    arrow(ax, 10.3, y0 - 0.5, 10.3, 5.68, color=GREEN)

    box(2.55, 3.2, 5.2, 0.95, "Free fall", None)
    ax.text(2.6, 3.0, r"$a=-g$  (always: up, top, down)", ha="center", va="center", fontsize=9, zorder=3)
    ax.texts[-2].set_position((2.6, 3.4))
    ax.texts[-2].set_weight("bold")
    box(8.6, 3.2, 6.6, 0.95, "Projectile", None)
    ax.text(8.65, 3.0, r"horizontal $a=0$   and   vertical $a=-g$", ha="center", va="center", fontsize=9, zorder=3)
    ax.texts[-2].set_position((8.65, 3.4))
    ax.texts[-2].set_weight("bold")
    ax.add_patch(FancyArrowPatch((8.75, 5.05), (3.4, 3.7), connectionstyle="arc3,rad=0.25",
                                 arrowstyle="-|>", mutation_scale=10, color=GREEN, lw=1.3))
    arrow(ax, 9.9, 4.72, 9.4, 3.7, color=GREEN)

    box(6.0, 1.0, 12.1, 0.8, "", None)
    ax.text(6.0, 1.0, r"Fluid resistance:  $a$ changes with $v$  $\rightarrow$  no SUVAT  $\rightarrow$  terminal speed",
            ha="center", va="center", fontsize=8.6, weight="bold", zorder=3)
    arrow(ax, 2.9, 2.72, 3.9, 1.42, color=ORANGE)
    arrow(ax, 8.2, 2.72, 7.2, 1.42, color=ORANGE)
    save(fig, "f_concept", w)


# ---------------------------------------------------------------- Figure 1.2
def fig_walk():
    w = 5.7
    fig, ax = plt.subplots(figsize=(w, 2.5))
    ax.set_xlim(-3, 46)
    ax.set_ylim(-3.2, 4.6)
    plain_axes(ax)
    arrow(ax, -2, 0, 45, 0, lw=0.9, ms=9)
    for x in range(0, 41, 10):
        ax.plot([x, x], [-0.18, 0.18], color="black", lw=0.9)
        ax.text(x, -0.45, f"{x}", ha="center", va="top", fontsize=9.5)
    ax.text(45, 0.3, r"$x$ (m)  $\rightarrow$ East", ha="right", va="bottom", fontsize=9.5)
    ax.plot(0, 0, "o", color="black", ms=6, zorder=5)
    ax.plot(30, 0, "s", color=GREEN, ms=6, zorder=5)
    ax.text(0, 0.35, "start", ha="center", va="bottom", fontsize=9.5)
    ax.text(30, 0.35, "finish", ha="center", va="bottom", fontsize=9.5)
    arrow(ax, 0, 1.6, 40, 1.6, color=BLUE, lw=1.8)
    ax.text(20, 1.85, "leg 1: 40 m east", color=BLUE, ha="center", va="bottom", fontsize=10)
    arrow(ax, 40, 2.9, 30, 2.9, color=RED, lw=1.8)
    ax.text(35, 3.15, "leg 2: 10 m west", color=RED, ha="center", va="bottom", fontsize=10)
    ax.plot([40, 40], [1.6, 2.9], color="0.6", lw=0.7, ls=":")
    arrow(ax, 0, -1.6, 30, -1.6, color=GREEN, lw=1.8)
    ax.text(15, -1.95, r"displacement $= +30$ m  (start $\rightarrow$ finish)", color=GREEN,
            ha="center", va="top", fontsize=10, weight="bold")
    ax.text(-2.5, 4.4, r"distance travelled $= 40 + 10 = 50$ m", ha="left", va="top", fontsize=10,
            bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="black", lw=0.7))
    save(fig, "f_walk", w)


# ---------------------------------------------------------------- Figure 1.3
def fig_chord_tangent():
    w = 4.9
    fig, ax = plt.subplots(figsize=(w, 3.3))
    t = np.linspace(0, 5, 300)
    ax.plot(t, t ** 2, color="black", lw=1.5)
    ax.plot([1, 4], [1, 16], ls="--", color=BLUE, lw=1.4)
    tt = np.linspace(2.0, 4.25, 10)
    ax.plot(tt, 9 + 6 * (tt - 3), color=RED, lw=1.4)
    ax.plot([1, 4], [1, 1], ls=":", color=GREY, lw=0.9)
    ax.plot([4, 4], [1, 16], ls=":", color=GREY, lw=0.9)
    ax.plot([1, 4], [1, 16], "o", color=BLUE, ms=5, zorder=5)
    ax.plot(3, 9, "o", color=RED, ms=5, zorder=5)
    ax.text(2.5, 1.4, r"$\Delta t = 3$ s", ha="center", va="bottom", fontsize=9, color="0.3")
    ax.text(4.08, 10.0, r"$\Delta s = 15$ m", ha="left", va="center", fontsize=9, color="0.3")
    ax.text(0.2, 17.0, "chord (dashed)\naverage velocity $= 15/3 = 5$ m s$^{-1}$", color=BLUE, fontsize=9.5, va="bottom")
    ax.text(4.12, 1.4, "tangent at $t = 3$ s\ninstantaneous velocity\n$=$ its gradient $= 6$ m s$^{-1}$",
            color=RED, fontsize=9.5, va="bottom", ha="left")
    ax.text(0.15, 23.2, r"$s = t^2$  (example motion)", fontsize=9.5)
    ax.set_xlim(0, 6.8)
    ax.set_ylim(0, 26)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"displacement $s$ (m)")
    save(fig, "f_chord", w)


# ---------------------------------------------------------------- Figure 1.4
def fig_motion_diagrams():
    w = 5.6
    fig, ax = plt.subplots(figsize=(w, 3.9))
    ax.set_xlim(-0.4, 8.9)
    ax.set_ylim(-0.5, 8.6)
    plain_axes(ax)
    n = np.arange(5)
    k = 0.45  # dot spacing grows as n^2 for constant acceleration
    speed_up = k * n ** 2
    rows = [
        (r"1. $v\rightarrow(+)$ and $a\rightarrow(+)$:  speeding up", speed_up, +1),
        (r"2. $v\rightarrow(+)$ and $a\leftarrow(-)$:  slowing down", (k * 16 - speed_up)[::-1], -1),
        (r"3. $v\leftarrow(-)$ and $a\leftarrow(-)$:  speeding up", k * 16 - speed_up, -1),
        (r"4. $v\leftarrow(-)$ and $a\rightarrow(+)$:  slowing down", speed_up[::-1], +1),
    ]
    for i, (label, xs, adir) in enumerate(rows):
        y = 7.6 - i * 2.15
        ax.text(-0.3, y + 0.55, label, fontsize=9.5, weight="bold", va="center")
        ax.plot([-0.3, 7.6], [y, y], color="0.75", lw=0.7, zorder=1)
        ax.plot(xs, np.full(5, y), "o", color="black", ms=5, zorder=4)
        for a_, b_ in zip(xs[:-1], xs[1:]):
            gap = b_ - a_
            if abs(gap) < 1e-9:
                continue
            pad = 0.07 * np.sign(gap)
            arrow(ax, a_ + pad, y - 0.42, b_ - pad, y - 0.42, color=BLUE, lw=1.1, ms=7)
        ax.text(8.25, y + 0.5, r"$a$", color=RED, ha="center", va="bottom", fontsize=10)
        if adir > 0:
            arrow(ax, 7.75, y + 0.35, 8.75, y + 0.35, color=RED, lw=1.6)
        else:
            arrow(ax, 8.75, y + 0.35, 7.75, y + 0.35, color=RED, lw=1.6)
    ax.text(4.2, -0.35, "blue arrows = velocity between dots (equal time gaps)     red arrow = direction of acceleration",
            ha="center", fontsize=8.5, color="0.25")
    save(fig, "f_motiondiag", w)


# ---------------------------------------------------------------- Figure 1.5
def journey():
    t = np.linspace(0, 14, 1401)
    a = np.where(t < 4, 2.0, np.where(t < 8, 0.0, -2.0))
    v = np.where(t < 4, 2 * t, np.where(t < 8, 8.0, 8 - 2 * (t - 8)))
    s = np.where(t < 4, t ** 2, np.where(t < 8, 16 + 8 * (t - 4), 48 + 8 * (t - 8) - (t - 8) ** 2))
    return t, s, v, a


def stage_marks(ax, top=False):
    for x in (4, 8):
        ax.axvline(x, color="0.6", lw=0.7, ls=":", zorder=0)


def fig_three_graphs():
    w = 5.3
    t, s, v, a = journey()
    fig, axs = plt.subplots(3, 1, figsize=(w, 6.3), sharex=True, gridspec_kw=dict(hspace=0.12))
    ax = axs[0]
    ax.plot(t, s, color="black", lw=1.5)
    ax.plot(12, 64, "o", color=RED, ms=5, zorder=5)
    ax.annotate("turning point:\n$v = 0$, $s$ is a maximum", xy=(12, 64), xytext=(11.4, 40),
                ha="center", fontsize=8.5, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.text(1.7, 18, "curve gets\nsteeper", fontsize=8.5, color="0.35", ha="center")
    ax.text(6.6, 14, "straight line:\nsteady slope", fontsize=8.5, color="0.35", ha="center")
    ax.set_ylabel(r"displacement $s$ (m)")
    ax.set_ylim(-3, 75)
    for x0, x1, lab in [(0, 4, "A: speeding up\n($a = +2$)"), (4, 8, "B: constant velocity\n($a = 0$)"),
                        (8, 14, "C: slowing, stopping,\nthen reversing ($a = -2$)")]:
        ax.text((x0 + x1) / 2, 77, lab, ha="center", va="bottom", fontsize=8.5, weight="bold")
    ax = axs[1]
    ax.plot(t, v, color="black", lw=1.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.plot(12, 0, "o", color=RED, ms=5, zorder=5)
    ax.fill_between(t, 0, v, where=(t <= 4), color=GREEN, alpha=0.18, lw=0)
    ax.text(0.25, 8.9, "area under\n$v$–$t$ $= \\Delta s$", fontsize=8.5, color=GREEN)
    ax.text(6.0, 9.0, "flat: $v = 8$ m s$^{-1}$", fontsize=8.5, color="0.35", ha="center")
    ax.text(2.4, 1.0, "slope $= +2$", fontsize=8.5, color="0.35")
    ax.text(10.6, 5.2, "slope $= -2$\n(zero at 12 s)", fontsize=8.5, color="0.35")
    ax.text(12.4, -4.6, "$v < 0$:\nmoving back", fontsize=8.5, color="0.35", ha="right")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    ax.set_ylim(-6, 13)
    ax = axs[2]
    ax.plot(t, a, color="black", lw=1.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel(r"acceleration $a$ (m s$^{-2}$)")
    ax.set_ylim(-3.2, 3.2)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(0, 14)
    ax.set_xticks(range(0, 15, 2))
    for ax in axs:
        stage_marks(ax)
    fig.align_ylabels(axs)
    save(fig, "f_threegraphs", w)


# --------------------------------------------------- NEW: realistic car journey
def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def fig_real_car():
    """A town drive between two sets of traffic lights.

    Acceleration is built from smooth pieces (with short dips at the gear
    changes) so it never jumps; velocity and distance are integrated from it.
    """
    w = 5.3
    dt = 0.01
    t = np.arange(0, 34 + dt, dt)
    rng = np.random.default_rng(7)
    # pulling away: peak about 2.6 m/s^2, fading as speed builds, gear-change dips at 2.3 s and 5.6 s
    a = 2.7 * smoothstep(t / 0.6) * np.exp(-np.clip(t, 0, None) / 6.0)
    for tg in (2.3, 5.6):
        a *= 1 - 0.85 * np.exp(-((t - tg) / 0.22) ** 2)
    a = a * (1 - smoothstep((t - 7.5) / 1.5))
    # cruising: small throttle corrections
    cruise = (t > 9) & (t < 25.5)
    wobble = 0.12 * np.sin(2 * np.pi * t / 5.3) + 0.06 * np.sin(2 * np.pi * t / 2.1 + 1)
    a = a + np.where(cruise, wobble * smoothstep((t - 9) / 1.5) * (1 - smoothstep((t - 24.5) / 1.0)), 0)
    v = np.cumsum(a) * dt
    v_cruise = v[np.searchsorted(t, 24.0)]
    # braking: jerk-limited, to rest at the lights
    t_b0, t_stop = 26.0, 32.0
    brake_shape = smoothstep((t - t_b0) / 1.5) * (1 - smoothstep((t - (t_stop - 1.2)) / 1.2))
    # scale braking so the car stops exactly at t_stop
    v_before = np.interp(t_b0, t, v)
    area = np.trapezoid(brake_shape, t)
    a_brake = -brake_shape * v_before / area
    a_total = np.where(t < t_b0, a, a_brake)
    v = np.cumsum(a_total) * dt
    v = np.where(t > t_stop, 0, np.clip(v, 0, None))
    s_real = np.cumsum(v) * dt
    # GPS-style samples every 0.5 s with small noise
    ts = np.arange(0, 34.01, 0.5)
    vs = np.interp(ts, t, v) + rng.normal(0, 0.12, ts.size)
    vs = np.where(np.interp(ts, t, v) < 0.05, 0, vs)
    # straight-line exam model with the same top speed and the same total distance
    vtop = float(np.max(v))
    t1 = 8.0
    # choose the cruise end so that the trapezium has the same area as the real trace
    total = s_real[-1]
    # area = vtop * ((t2 - t1) + (t1 + (t_stop - t2)) / 2)  -> solve for t2
    t2 = (total / vtop - t1 / 2 - t_stop / 2) * 2 + t1
    t2 = (2 * total / vtop - t_stop + t1)
    tm = np.array([0, t1, t2, t_stop, 34])
    vm = np.array([0, vtop, vtop, 0, 0])
    fig, axs = plt.subplots(2, 1, figsize=(w, 4.6), sharex=True, gridspec_kw=dict(hspace=0.1, height_ratios=[1.35, 1]))
    ax = axs[0]
    ax.plot(tm, vm, ls="--", color=GREY, lw=1.1, label="straight-line model")
    ax.plot(t, v, color=BLUE, lw=1.5, label="real car")
    ax.plot(ts, vs, "o", ms=2.6, color="black", label="GPS readings (every 0.5 s)", zorder=5)
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    ax.set_ylim(-0.8, 17)
    ax.legend(loc="upper right", fontsize=8.2)
    ax.annotate("gear changes", xy=(5.6, np.interp(5.6, t, v)), xytext=(6.6, 5.0), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.7, color="0.3"))
    ax.annotate("", xy=(2.3, np.interp(2.3, t, v)), xytext=(6.5, 5.3),
                arrowprops=dict(arrowstyle="-", lw=0.7, color="0.3"))
    ax = axs[1]
    ax.plot(t, a_total * (t <= t_stop), color=RED, lw=1.3, label="real car")
    am = np.where(t < t1, vtop / t1, np.where(t < t2, 0, np.where(t < t_stop, -vtop / (t_stop - t2), 0)))
    ax.plot(t, am, ls="--", color=GREY, lw=1.1, label="model")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel(r"acceleration $a$ (m s$^{-2}$)")
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(0, 34)
    ax.set_ylim(-4.6, 3.4)
    ax.legend(loc="lower left", fontsize=8.2)
    fig.align_ylabels(axs)
    save(fig, "f_realcar", w)
    return dict(vtop=vtop, s_real=float(s_real[-1]), s_model=float(np.trapezoid(vm, tm)), t2=float(t2))


# ---------------------------------------------------------------- Figure 1.6
def fig_suvat_area():
    w = 4.6
    fig, ax = plt.subplots(figsize=(w, 3.2))
    u, v, T = 1.0, 3.0, 4.0
    ax.add_patch(Rectangle((0, 0), T, u, fc="#cfdcf3", ec="none"))
    ax.add_patch(Polygon([(0, u), (T, v), (T, u)], closed=True, fc="#f3d3d3", ec="none"))
    ax.plot([0, T], [u, v], color="black", lw=1.8)
    ax.plot([0, 0], [0, u], color="black", lw=1.0)
    ax.plot([T, T], [0, v], color="black", lw=1.0)
    ax.plot([T, T + 0.6], [v, v], ls=":", color=GREY, lw=1.2)
    ax.text(T + 0.08, v - 0.18, r"$v = u + at$", color="0.35", fontsize=9.5, va="top")
    ax.text(T / 2, u / 2, r"rectangle: $u \times t$", color=BLUE, ha="center", va="center", fontsize=10)
    ax.text(T * 0.76, (u + v) / 2 - 0.3, "triangle:\n" + r"$\frac{1}{2} \times t \times (v-u)$" + "\n" + r"$= \frac{1}{2}at^2$",
            color=RED, ha="center", va="center", fontsize=9.5)
    ax.text(T * 0.42, v - 0.05, r"gradient $= a = (v-u)/t$", ha="center", va="bottom", fontsize=10)
    dimline(ax, T + 0.75, u, T + 0.75, v)
    ax.text(T + 0.82, (u + v) / 2, r"$v-u$", fontsize=9.5, va="center", color="0.35")
    ax.set_xlim(-0.4, T + 1.5)
    ax.set_ylim(0, 3.7)
    ax.set_xticks([0, T])
    ax.set_xticklabels(["0", r"$t$"])
    ax.set_yticks([u, v])
    ax.set_yticklabels([r"$u$", r"$v$"])
    ax.minorticks_off()
    ax.tick_params(top=False, right=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel("time")
    ax.set_ylabel("velocity")
    save(fig, "f_suvatarea", w)


# ---------------------------------------------------------------- Figure 1.7
def fig_throw_up():
    w = 5.0
    u = 19.6
    T = 2 * u / G
    t = np.linspace(0, T, 400)
    fig, axs = plt.subplots(3, 1, figsize=(w, 5.4), sharex=True, gridspec_kw=dict(hspace=0.12))
    ax = axs[0]
    ax.plot(t, u * t - 0.5 * G * t ** 2, color="black", lw=1.5)
    ax.plot(T / 2, u ** 2 / (2 * G), "o", color=RED, ms=5, zorder=5)
    ax.text(T / 2 + 0.08, u ** 2 / (2 * G) + 0.6, r"top: $H = u^2/2g = 19.6$ m", color=RED, fontsize=9, va="bottom")
    ax.text(T / 2, 2.0, r"launch and landing at $y = 0$,  $T = 2u/g = 4.0$ s", color="0.35", fontsize=9, ha="center")
    ax.set_ylabel(r"height $y$ (m)")
    ax.set_ylim(0, 24.5)
    ax = axs[1]
    ax.plot(t, u - G * t, color="black", lw=1.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.plot(T / 2, 0, "o", color=RED, ms=5, zorder=5)
    ax.text(T / 2 + 0.1, 2.0, "$v = 0$ at the top", color=RED, fontsize=9)
    ax.text(0.35, 21.5, "starts at $+19.6$ m s$^{-1}$ (up)", color="0.35", fontsize=9, va="center")
    ax.text(3.0, -21.0, "ends at $-19.6$ m s$^{-1}$ (down)", color="0.35", fontsize=9, ha="right", va="center")
    ax.text(0.95, -12.5, "gradient $= -g$\n(the SAME all the way)", color="0.35", fontsize=9, ha="center")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    ax.set_ylim(-25, 25)
    ax = axs[2]
    ax.plot(t, np.full_like(t, -G), color="black", lw=1.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.text(T / 2 + 0.1, -8.6, "$a = -9.81$ m s$^{-2}$ even at the top", color=RED, fontsize=9)
    ax.set_ylabel(r"acceleration $a$ (m s$^{-2}$)")
    ax.set_ylim(-13, 3)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(-0.1, 4.1)
    for ax in axs:
        ax.axvline(T / 2, color="0.6", lw=0.7, ls=":", zorder=0)
    fig.align_ylabels(axs)
    save(fig, "f_throwup", w)


# ---------------------------------------------- NEW: motion-sensor data for a toss
def fig_sensor_toss():
    """Simulated ultrasonic motion-sensor readings (20 Hz) for a ball tossed
    upward and caught. The hand pushes for ~0.15 s, then free flight, then catch."""
    w = 5.3
    rng = np.random.default_rng(3)
    dt = 1e-3
    t = np.arange(0, 1.45, dt)
    t_rel, t_catch = 0.30, 1.13
    a = np.zeros_like(t)
    push = (t > 0.12) & (t < t_rel)
    a[push] = 50.0 * np.sin(np.pi * (t[push] - 0.12) / (t_rel - 0.12)) - G
    a[(t >= t_rel) & (t < t_catch)] = -G
    v = np.cumsum(a) * dt
    # catch: hand brings the ball to rest in about 0.2 s
    i_c = np.searchsorted(t, t_catch)
    v_c = v[i_c]
    span = 0.22
    for i in range(i_c, t.size):
        f = min((t[i] - t_catch) / span, 1)
        v[i] = v_c * (1 - smoothstep(f))
    y = 0.45 + np.cumsum(v) * dt
    ts = np.arange(0, 1.45, 0.05)
    ys = np.interp(ts, t, y) + rng.normal(0, 0.003, ts.size)
    vs = np.gradient(ys, ts)
    free = (ts > t_rel + 0.03) & (ts < t_catch - 0.03)
    m, c = np.polyfit(ts[free], vs[free], 1)
    fig, axs = plt.subplots(2, 1, figsize=(w, 4.6), sharex=True, gridspec_kw=dict(hspace=0.1))
    ax = axs[0]
    ax.plot(ts, ys, "o", ms=3.2, color="black", zorder=4)
    ax.plot(t, y, color=BLUE, lw=0.9, alpha=0.7)
    ax.set_ylabel(r"height $y$ (m)")
    ax.set_ylim(0.15, 2.0)
    ax = axs[1]
    ax.plot(ts, vs, "o", ms=3.2, color="black", zorder=4)
    tf = np.linspace(t_rel, t_catch, 10)
    ax.plot(tf, m * tf + c, color=RED, lw=1.3)
    ax.axhline(0, color="black", lw=0.6)
    ax.text(0.73, 2.2, f"best-fit line (free flight only):\ngradient $= {m:.2f}$ m s$^{{-2}}$",
            color=RED, fontsize=9, va="bottom")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(0, 1.43)
    ax.set_ylim(-5.5, 5.5)
    for ax in axs:
        for x in (t_rel, t_catch):
            ax.axvline(x, color="0.6", lw=0.7, ls=":", zorder=0)
    axs[0].text(t_rel / 2 + 0.04, 1.94, "hand\npushes", ha="center", va="top", fontsize=8.5, color="0.3")
    axs[0].text((t_rel + t_catch) / 2, 1.94, "free fall: only gravity acts", ha="center", va="top", fontsize=8.5, color="0.3")
    axs[0].text((t_catch + 1.43) / 2, 1.94, "caught", ha="center", va="top", fontsize=8.5, color="0.3")
    fig.align_ylabels(axs)
    save(fig, "f_sensortoss", w)
    return dict(gradient=float(m))


# ---------------------------------------------------------------- Figure 1.8
def fig_components():
    w = 3.9
    fig, ax = plt.subplots(figsize=(w, 2.5))
    th = np.radians(35)
    L = 4.0
    vx, vy = L * np.cos(th), L * np.sin(th)
    ax.set_xlim(-0.3, 5.3)
    ax.set_ylim(-0.75, 2.75)
    ax.set_aspect("equal")
    plain_axes(ax)
    ax.plot([0, 4.6], [0, 0], color="0.75", lw=0.7)
    arrow(ax, 0, 0, vx, 0, color=BLUE, lw=1.8, ms=10)
    arrow(ax, vx, 0, vx, vy, color=RED, lw=1.8, ms=10)
    arrow(ax, 0, 0, vx, vy, color="black", lw=2.0, ms=12)
    ax.plot([vx - 0.18, vx - 0.18, vx], [0, 0.18, 0.18], color="0.4", lw=0.7)
    ax.add_patch(Arc((0, 0), 1.6, 1.6, theta1=0, theta2=35, lw=0.9))
    ax.text(0.95, 0.24, r"$\theta$", fontsize=11, va="center")
    ax.text(vx / 2 - 0.25, vy / 2 + 0.25, r"$\mathbf{v}$", fontsize=13, ha="right")
    ax.text(vx / 2, -0.18, r"horizontal component  $v\cos\theta$", color=BLUE, ha="center", va="top", fontsize=10)
    ax.text(vx + 0.12, vy / 2, "vertical\ncomponent\n" + r"$v\sin\theta$", color=RED, ha="left", va="center", fontsize=10)
    save(fig, "f_components", w)


# ---------------------------------------------------------------- Figure 1.9
def fig_drop_vs_throw():
    w = 4.6
    fig, ax = plt.subplots(figsize=(w, 3.4))
    ts = np.arange(0, 1.51, 0.25)
    fall = 0.5 * G * ts ** 2
    xs = 6.0 * ts
    tt = np.linspace(0, 1.5, 200)
    ax.plot(6 * tt, 0.5 * G * tt ** 2, ls=":", color=BLUE, lw=0.9)
    for x, y, tk in zip(xs, fall, ts):
        ax.plot([0, x], [y, y], color="0.7", lw=0.7, zorder=1)
        if tk > 0:
            ax.text(x + 0.35, y - 0.2, f"{tk:.2f} s", fontsize=8, color="0.35", va="bottom")
    ax.plot(np.zeros_like(fall), fall, "o", color=RED, ms=6, zorder=4, label="dropped from rest")
    ax.plot(xs, fall, "o", color=BLUE, ms=6, zorder=5, label=r"thrown sideways at 6.0 m s$^{-1}$")
    ax.text(9.3, 5.6, "Same height at every\ninstant: vertical motion\nis not affected by the\nsideways motion",
            fontsize=8.5, va="center")
    ax.set_xlim(-1, 15)
    ax.set_ylim(12.4, -0.8)
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel("distance fallen (m)")
    ax.legend(loc="upper right", fontsize=8.2)
    save(fig, "f_dropthrow", w)


# --------------------------------------------------------------- Figure 1.10
def fig_projectile_vectors():
    w = 5.9
    u, th = 20.0, np.radians(50)
    ux, uy = u * np.cos(th), u * np.sin(th)
    T = 2 * uy / G
    R = ux * T
    t = np.linspace(0, T, 300)
    fig, ax = plt.subplots(figsize=(w, 3.4))
    ax.plot(ux * t, uy * t - 0.5 * G * t ** 2, ls="--", color="black", lw=1.0)
    ground(ax, -3, R + 10)
    k = 0.38  # metres of drawing per m/s, the same for every arrow
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        tk = frac * T
        x, y = ux * tk, uy * tk - 0.5 * G * tk ** 2
        vy = uy - G * tk
        arrow(ax, x, y, x + k * ux, y, color=BLUE, lw=1.4, ms=8, z=5)
        if abs(vy) > 0.1:
            arrow(ax, x, y, x, y + k * vy, color=RED, lw=1.4, ms=8, z=5)
        arrow(ax, x, y, x + k * ux, y + k * vy, color=GREEN, lw=1.6, ms=9, z=6)
        ax.plot(x, y, "o", color="black", ms=3.5, zorder=7)
    ax.plot([], [], color=BLUE, lw=1.6, label="horizontal component (constant)")
    ax.plot([], [], color=RED, lw=1.6, label=r"vertical component (changes by 9.81 m s$^{-1}$ every s)")
    ax.plot([], [], color=GREEN, lw=1.6, label="resultant velocity")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, fontsize=8)
    H = uy ** 2 / (2 * G)
    ax.text(R / 2, H + 1.3, r"top: $v_y = 0$, speed is a minimum ($= v_x$)", ha="center", fontsize=9)
    ax.text(-2.0, -5.5, r"launch:  $v_x = 12.9$,  $v_y = +15.3$ m s$^{-1}$", fontsize=9, va="center")
    ax.text(R + 9.5, 9.5, "landing:\n$v_x = 12.9$\n$v_y = -15.3$\n(m s$^{-1}$)", fontsize=9, ha="right", va="center")
    ax.set_xlim(-3, R + 10)
    ax.set_ylim(-7, 17)
    ax.set_aspect("equal")
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel(r"height $y$ (m)")
    save(fig, "f_projvectors", w)


# --------------------------------------------------------------- Figure 1.11
def fig_angles():
    w = 5.6
    u = 20.0
    fig, ax = plt.subplots(figsize=(w, 3.2))
    styles = {15: (ORANGE, "-"), 30: (GREEN, "-"), 45: ("black", "-"), 60: (BLUE, "-"), 75: (RED, "-")}
    for ang, (c, ls) in styles.items():
        th = np.radians(ang)
        T = 2 * u * np.sin(th) / G
        t = np.linspace(0, T, 300)
        lab = f"{ang}°" + ("  (max range)" if ang == 45 else "")
        ax.plot(u * np.cos(th) * t, u * np.sin(th) * t - 0.5 * G * t ** 2, color=c, ls=ls,
                lw=1.8 if ang == 45 else 1.2, label=lab)
    r30 = u ** 2 * np.sin(np.radians(60)) / G
    r15 = u ** 2 * np.sin(np.radians(30)) / G
    ax.annotate("15° and 75° land\nat the same place", xy=(r15, 0.1), xytext=(21.5, 17.8), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.annotate("30° and 60° land\nat the same place", xy=(r30, 0.1), xytext=(37.5, 6.5), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.legend(title="launch angle", loc="upper right", fontsize=8.2, title_fontsize=8.5)
    ax.set_xlim(0, 48)
    ax.set_ylim(0, 21)
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel(r"height $y$ (m)")
    save(fig, "f_angles", w)


def cliff_scene(ax, H, u, ang, xmax, show_numbers):
    th = np.radians(ang)
    ux, uy = u * np.cos(th), u * np.sin(th)
    tl = (uy + np.sqrt(uy ** 2 + 2 * G * H)) / G
    R = ux * tl
    t = np.linspace(0, tl, 300)
    ax.add_patch(Rectangle((-9, 0), 9, H, fc=EARTHFILL, ec="none", zorder=1))
    ax.plot([-9, 0, 0], [H, H, 0], color=EARTH, lw=1.6, zorder=2)
    ground(ax, -9, xmax)
    ax.plot(ux * t, H + uy * t - 0.5 * G * t ** 2, ls="--", color="black", lw=1.1)
    ax.plot([0, xmax], [H, H], ls=":", color=GREY, lw=0.8)
    arrow(ax, 0, H, 0.22 * ux, H + 0.22 * uy, color=BLUE, lw=1.6, ms=9, z=6)
    ax.add_patch(Arc((0, H), 9, 9, theta1=0, theta2=ang, lw=0.8, zorder=4))
    ax.plot(0, H, "o", color="black", ms=4, zorder=7)
    ax.plot(R, 0, "o", color="black", ms=4, zorder=7)
    return R, tl, ux, uy


# --------------------------------------------------------------- Figure 1.12
def fig_cliff_general():
    w = 5.2
    fig, ax = plt.subplots(figsize=(w, 3.3))
    H, u, ang = 20.0, 15.0, 30
    R, tl, ux, uy = cliff_scene(ax, H, u, ang, 52, False)
    ax.text(4.9, H + 0.6, r"$\theta$", fontsize=10)
    ax.text(-3.2, H + 3.6, r"$\mathbf{u}$", color=BLUE, fontsize=12)
    ax.text(-8.6, H - 2.0, "cliff top", fontsize=8.5, color="0.3")
    ax.text(19, 26.5, "path rises and falls back to launch level\n(symmetric part)", ha="center", fontsize=8.5)
    ax.text(15, 9.5, "...then keeps falling $h$ more\nbefore reaching the ground", ha="center", fontsize=8.5)
    dimline(ax, R + 4, 0, R + 4, H, color=RED)
    ax.text(R + 5, H / 2, r"$s_y = -h$", color=RED, fontsize=10, va="center")
    ax.text(R, -1.4, "lands here", ha="center", va="top", fontsize=8.5)
    ax.set_xlim(-9, 52)
    ax.set_ylim(-4, 31)
    ax.set_aspect("equal")
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel("height above ground (m)")
    save(fig, "f_cliffgeneral", w)


# --------------------------------------------------------------- Figure 1.13
def fig_forces():
    w = 5.6
    fig, ax = plt.subplots(figsize=(w, 2.9))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.6, 6.4)
    plain_axes(ax)
    Wlen = 2.0
    stages = [("1. just released", r"$a = g$", 0.0, r"$v = 0 \rightarrow$ drag $= 0$"),
              ("2. speeding up", r"$a < g$ (smaller)", 0.5, "drag < weight"),
              ("3. terminal speed", r"$a = 0$, $v$ constant", 1.0, "drag = weight")]
    for i, (title, acc, frac, foot) in enumerate(stages):
        cx, cy = 2 + 4 * i, 2.55
        ax.text(cx, 6.2, title, ha="center", va="top", fontsize=10, weight="bold")
        ax.text(cx, 5.65, acc, ha="center", va="top", fontsize=10, color=GREEN)
        ax.add_patch(Circle((cx, cy), 0.38, fc="#d9d9d9", ec="black", lw=0.9, zorder=3))
        arrow(ax, cx, cy - 0.38, cx, cy - 0.38 - Wlen, color=RED, lw=1.8, ms=10)
        ax.text(cx + 0.12, cy - 0.38 - Wlen + 0.1, "weight $mg$", color=RED, fontsize=9, va="bottom")
        if frac > 0:
            arrow(ax, cx, cy + 0.38, cx, cy + 0.38 + Wlen * frac, color=BLUE, lw=1.8, ms=10)
            ax.text(cx + 0.12, cy + 0.38 + Wlen * frac - 0.15, "drag $D$", color=BLUE, fontsize=9, va="top")
        arrow(ax, cx - 1.25, cy + 0.6, cx - 1.25, cy - 0.6, color="0.5", lw=0.9, ms=7)
        ax.text(cx - 1.35, cy, "$v$", color="0.4", fontsize=9, ha="right", va="center")
        ax.text(cx, -0.45, foot, ha="center", va="bottom", fontsize=9)
    save(fig, "f_forces", w)


# --------------------------------------------------------------- Figure 1.14
def integrate_fall(k_of_t, t_end, dt=1e-3, v0=0.0):
    t = np.arange(0, t_end + dt, dt)
    v = np.empty_like(t)
    v[0] = v0
    for i in range(1, t.size):
        # RK2 for dv/dt = g - k v|v|
        k = k_of_t(t[i - 1])
        f1 = G - k * v[i - 1] * abs(v[i - 1])
        vm = v[i - 1] + 0.5 * dt * f1
        f2 = G - k_of_t(t[i - 1] + 0.5 * dt) * vm * abs(vm)
        v[i] = v[i - 1] + dt * f2
    return t, v


def fig_terminal():
    w = 6.0
    fig, axs = plt.subplots(1, 2, figsize=(w, 2.75), gridspec_kw=dict(wspace=0.32))
    vt = 40.0
    t = np.linspace(0, 20, 400)
    v = vt * np.tanh(G * t / vt)
    ax = axs[0]
    ax.plot(t, v, color="black", lw=1.5)
    ax.axhline(vt, ls="--", color=GREY, lw=0.8)
    ax.text(19.6, vt + 1, "terminal speed", ha="right", va="bottom", fontsize=8.5, color="0.35")
    tt = np.linspace(0, 5.3, 10)
    ax.plot(tt, G * tt, ls=":", color=RED, lw=1.1)
    ax.text(6.0, 53, "dotted: gradient\nat $t = 0$ is $g$", color=RED, fontsize=8.2, va="top")
    ax.text(8.0, 14, "gradient $\\rightarrow 0$\nas drag $\\rightarrow$\nweight", fontsize=8.2)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 55)
    ax.set_title("Object falling from rest", fontsize=9.5)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"speed (m s$^{-1}$)")

    # skydiver: 80 kg, terminal 55 m/s spread-eagled, 5 m/s under canopy,
    # canopy takes 2.5 s to inflate after opening at 15 s
    v1, v2, t_open, t_fill = 55.0, 5.0, 15.0, 2.5
    k1, k2 = G / v1 ** 2, G / v2 ** 2

    def k_of_t(tq):
        f = smoothstep((tq - t_open) / t_fill)
        return k1 * (k2 / k1) ** f

    ts, vs = integrate_fall(k_of_t, 50.0)
    ax = axs[1]
    ax.plot(ts, vs, color="black", lw=1.5)
    ax.axhline(v1, ls="--", color=GREY, lw=0.8, xmax=0.42)
    ax.axhline(v2, ls="--", color=GREY, lw=0.8)
    ax.axvline(t_open, ls=":", color="0.5", lw=0.8)
    ax.text(0.8, v1 + 1.2, "1st terminal speed", fontsize=8, color="0.35", va="bottom")
    ax.text(49, v2 + 1.2, "2nd terminal speed", fontsize=8, color="0.35", ha="right", va="bottom")
    ax.text(t_open + 4.5, 18, "parachute\nopens at\n$t = 15$ s", fontsize=8, color="0.35")
    ax.text(22, 40, "speed drops\nfast while\ndrag > weight", fontsize=8)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 66)
    ax.set_title("Skydiver with parachute", fontsize=9.5)
    ax.set_xlabel(r"time $t$ (s)")
    peak_decel = float(np.max(-np.gradient(vs, ts)) / G)
    save(fig, "f_terminal", w)
    return dict(peak_decel_g=peak_decel)


# ------------------------------------------- NEW: real objects falling through air
def fig_real_falls():
    w = 5.0
    rho = 1.2
    objs = [
        ("steel ball (2.0 cm diameter)", 7850 * 4 / 3 * np.pi * 0.010 ** 3, 0.020, 0.47, BLUE),
        ("tennis ball", 0.057, 0.067, 0.55, GREEN),
        ("table-tennis ball", 0.0027, 0.040, 0.50, RED),
    ]
    fig, ax = plt.subplots(figsize=(w, 3.2))
    t = np.linspace(0, 6, 300)
    ax.plot(t, G * t, ls="--", color="black", lw=1.1, label="no air (free fall)")
    info = {}
    for name, m, d, cd, c in objs:
        A = np.pi * d ** 2 / 4
        k = 0.5 * rho * cd * A / m
        vt = np.sqrt(G / k)
        v = vt * np.tanh(G * t / vt)
        ax.plot(t, v, color=c, lw=1.5, label=f"{name}: $v_T \\approx$ {vt:.0f} m s$^{{-1}}$")
        info[name] = float(vt)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 60)
    ax.set_xlabel(r"time after release $t$ (s)")
    ax.set_ylabel(r"speed $v$ (m s$^{-1}$)")
    ax.legend(loc="upper left", fontsize=8.2)
    save(fig, "f_realfalls", w)
    return info


# --------------------------------------------------------------- Figure 1.15
def fly(u, ang, k, dt=1e-3):
    th = np.radians(ang)
    x, y, vx, vy = 0.0, 0.0, u * np.cos(th), u * np.sin(th)
    xs, ys = [x], [y]
    while True:
        sp = np.hypot(vx, vy)
        ax_, ay_ = -k * sp * vx, -G - k * sp * vy
        x += vx * dt
        y += vy * dt
        vx += ax_ * dt
        vy += ay_ * dt
        if y < 0:
            break
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys), np.hypot(vx, vy), np.degrees(np.arctan2(-vy, vx))


def fig_drag_projectile():
    w = 5.6
    u, ang = 40.0, 45
    # football: m = 0.43 kg, d = 0.22 m, Cd = 0.25 -> k = rho Cd A / 2m
    k = 0.5 * 1.2 * 0.25 * (np.pi * 0.22 ** 2 / 4) / 0.43
    xi, yi, _, _ = fly(u, ang, 0.0)
    xd, yd, vland, aland = fly(u, ang, k)
    fig, ax = plt.subplots(figsize=(w, 3.3))
    ax.plot(xi, yi, ls="--", color="black", lw=1.3, label="no air resistance (ideal)")
    ax.plot(xd, yd, color=RED, lw=1.6, label="with air resistance")
    i = np.argmax(yd)
    ax.annotate("with drag: steeper descent,\nshorter range, lower peak", xy=(xd[i] - 5, yd[i] + 0.3),
                xytext=(5, 39.5), fontsize=8.5, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=0.7))
    ax.text(xi[-1] - 3, 2.0, "ideal path: symmetric", ha="right", fontsize=8.5, color="0.3")
    ax.legend(loc="upper right", fontsize=8.2)
    ax.set_xlim(0, 172)
    ax.set_ylim(0, 47)
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel(r"height $y$ (m)")
    save(fig, "f_dragproj", w)
    return dict(k=k, range=float(xd[-1]), H=float(yd.max()), vland=float(vland), aland=float(aland))


# --------------------------------------------------------------- Figure 1.16
def fig_g_graph():
    w = 4.9
    s = np.array([0.20, 0.40, 0.60, 0.80, 1.00])
    t2 = np.array([0.0400, 0.0841, 0.1225, 0.1600, 0.2025])
    e = np.array([0.0040, 0.0058, 0.0070, 0.0080, 0.0090])
    m, c = np.polyfit(t2, s, 1)
    # steepest / shallowest lines through the ends of the first and last error bars
    m_hi = (s[-1] - s[0]) / ((t2[-1] - e[-1]) - (t2[0] + e[0]))
    c_hi = s[0] - m_hi * (t2[0] + e[0])
    m_lo = (s[-1] - s[0]) / ((t2[-1] + e[-1]) - (t2[0] - e[0]))
    c_lo = s[0] - m_lo * (t2[0] - e[0])
    fig, ax = plt.subplots(figsize=(w, 3.3))
    x = np.linspace(0, 0.23, 10)
    ax.plot(x, m * x + c, color=BLUE, lw=1.4, label=f"best fit: gradient {m:.2f} m s$^{{-2}}$")
    ax.plot(x, m_hi * x + c_hi, ls="--", color=RED, lw=1.0, label=f"steepest: {m_hi:.2f}")
    ax.plot(x, m_lo * x + c_lo, ls="--", color=GREEN, lw=1.0, label=f"shallowest: {m_lo:.2f}")
    ax.errorbar(t2, s, xerr=e, fmt="o", ms=3.5, color="black", ecolor="black", elinewidth=0.9, capsize=2.5, zorder=5)
    ax.set_xlim(0, 0.23)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel(r"$t^2$ (s$^2$)")
    ax.set_ylabel(r"height fallen $s$ (m)")
    ax.legend(loc="lower right", fontsize=8.2)
    save(fig, "f_ggraph", w)
    return dict(m=m, m_hi=m_hi, m_lo=m_lo)


# --------------------------------------------------------------- Figure 1.17
def fig_boat():
    w = 5.2
    fig, ax = plt.subplots(figsize=(w, 3.3))
    ax.set_xlim(-0.2, 10.4)
    ax.set_ylim(-0.4, 7.4)
    plain_axes(ax)
    k = 1.2  # drawing units per m/s, the same for every arrow
    x0 = 4.6
    ax.text(0, 7.2, "UPSTREAM", fontsize=10, weight="bold", va="top")
    arrow(ax, x0, 6.3, x0 - 3.0 * k, 6.3, color=BLUE, lw=1.7)
    ax.text(x0 - 1.5 * k, 6.45, r"boat relative to water: $-3.0$ m s$^{-1}$", color=BLUE, ha="center", va="bottom", fontsize=9)
    arrow(ax, x0 - 3.0 * k, 5.55, x0 - 3.0 * k + 1.2 * k, 5.55, color=GREEN, lw=1.7)
    ax.text(x0 - 3.0 * k - 0.1, 5.55, r"water relative to ground: $+1.2$", color=GREEN, ha="right", va="center", fontsize=9)
    arrow(ax, x0, 4.75, x0 - 1.8 * k, 4.75, color="black", lw=1.9)
    ax.text(x0 + 0.15, 4.75, r"boat relative to ground $= -1.8$ m s$^{-1}$ (upstream)", ha="left", va="center", fontsize=9)
    ax.text(0, 3.75, "DOWNSTREAM", fontsize=10, weight="bold", va="top")
    arrow(ax, x0, 2.85, x0 + 3.0 * k, 2.85, color=BLUE, lw=1.7)
    ax.text(x0 + 1.5 * k, 3.0, r"boat relative to water: $+3.0$ m s$^{-1}$ (downstream)", color=BLUE, ha="center", va="bottom", fontsize=9)
    arrow(ax, x0 + 3.0 * k, 2.1, x0 + 4.2 * k, 2.1, color=GREEN, lw=1.7)
    ax.text(x0 + 3.0 * k - 0.1, 2.1, r"water: $+1.2$", color=GREEN, ha="right", va="center", fontsize=9)
    arrow(ax, x0, 1.3, x0 + 4.2 * k, 1.3, color="black", lw=1.9)
    ax.text(x0 - 0.15, 1.3, r"boat relative to ground $= +4.2$ m s$^{-1}$", ha="right", va="center", fontsize=9)
    for y in (6.3, 2.85):
        ax.plot([x0, x0], [y + 0.25, y - 1.8], color="0.7", lw=0.6, ls=":")
    arrow(ax, 3.2, 0.05, 6.2, 0.05, color="0.4", lw=1.0, ms=8)
    ax.text(4.7, -0.1, "positive direction = the way the river flows", ha="center", va="top", fontsize=8.5, color="0.3")
    save(fig, "f_boat", w)


# --------------------------------------------------------------- Chapter 2
def fig_ex3():
    w = 4.9
    fig, axs = plt.subplots(2, 1, figsize=(w, 4.4), sharex=True, gridspec_kw=dict(hspace=0.1))
    ax = axs[0]
    ax.plot([0, 4, 7, 12], [0, 20, 20, 0], color="black", lw=1.5)
    ax.text(1.7, 24.5, "slope $= 20/4$\n$= +5$ m s$^{-1}$", fontsize=8.5, ha="center", va="top")
    ax.text(5.5, 21.5, "flat $\\rightarrow$ at rest", fontsize=8.5, ha="center", va="bottom")
    ax.text(10.3, 18, "slope $= -20/5$\n$= -4$ m s$^{-1}$", fontsize=8.5, ha="center", va="top")
    ax.set_ylabel(r"$s$ (m)")
    ax.set_ylim(0, 26)
    ax = axs[1]
    for (a_, b_, vv) in [(0, 4, 5), (4, 7, 0), (7, 12, -4)]:
        ax.plot([a_, b_], [vv, vv], color="black", lw=1.8)
        ax.text((a_ + b_) / 2, vv + (0.6 if vv >= 0 else -0.7), f"{vv:+d}".replace("+0", "0").replace("-", "−"),
                ha="center", va="bottom" if vv >= 0 else "top", fontsize=9.5)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel(r"$v$ (m s$^{-1}$)")
    ax.set_ylim(-7, 8)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(0, 12.5)
    for ax in axs:
        for x in (4, 7):
            ax.axvline(x, color="0.6", lw=0.7, ls=":", zorder=0)
    fig.align_ylabels(axs)
    save(fig, "f_ex3", w)


def fig_ex5():
    w = 4.9
    fig, ax = plt.subplots(figsize=(w, 2.9))
    T = [0, 4, 10, 14, 16]
    V = [0, 10, 10, 0, -5]
    ax.fill_between([0, 4, 10, 14], [0, 10, 10, 0], color="#cfdcf3", lw=0)
    ax.fill_between([14, 16], [0, -5], color="#f3d3d3", lw=0)
    ax.plot(T, V, color="black", lw=1.6)
    ax.axhline(0, color="black", lw=0.6)
    ax.plot([4, 4], [0, 10], [10, 10], [0, 10], color="0.6", lw=0.6, ls=":")
    ax.plot(14, 0, "o", color=RED, ms=4.5, zorder=5)
    ax.text(2.7, 2.8, r"$A_1 = 20$", color=BLUE, fontsize=9.5, ha="center")
    ax.text(7.0, 5.0, r"$A_2 = 60$", color=BLUE, fontsize=9.5, ha="center")
    ax.text(11.3, 2.8, r"$A_3 = 20$", color=BLUE, fontsize=9.5, ha="center")
    ax.annotate(r"$A_4 = -5$", xy=(15.0, -2.2), xytext=(11.2, -4.6), color=RED, fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ax.text(14.8, 1.2, "turns round\nat $t = 14$ s", color=RED, fontsize=8.2, ha="center", va="bottom")
    ax.set_xticks([0, 4, 10, 14, 16])
    ax.set_xlim(0, 17)
    ax.set_ylim(-7, 12)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    save(fig, "f_ex5", w)


def fig_ex6():
    w = 4.9
    fig, axs = plt.subplots(2, 1, figsize=(w, 4.4), sharex=True, gridspec_kw=dict(hspace=0.1))
    ax = axs[0]
    ax.fill_between([0, 5], [2, 2], color="#f3d3d3", lw=0, step="post")
    ax.fill_between([8, 12], [-1.5, -1.5], color="#f3d3d3", lw=0)
    ax.step([0, 5, 8, 12], [2, 0, -1.5, -1.5], where="post", color="black", lw=1.6)
    ax.axhline(0, color="black", lw=0.6)
    ax.text(2.5, 1.0, "area $= 2.0 \\times 5.0$\n$= +10$ m s$^{-1}$", ha="center", va="center", fontsize=8.8)
    ax.text(10, -0.75, "area $= -1.5 \\times 4.0$\n$= -6$ m s$^{-1}$", ha="center", va="center", fontsize=8.8)
    ax.set_ylabel(r"$a$ (m s$^{-2}$)")
    ax.set_ylim(-2.5, 3)
    ax = axs[1]
    ax.plot([0, 5, 8, 12], [0, 10, 10, 4], color="black", lw=1.6)
    ax.plot([5, 8, 12], [10, 10, 4], "o", color="black", ms=4)
    for x, y in [(5, 10), (8, 10), (12, 4)]:
        ax.text(x, y + 0.6, f"{y}", ha="center", va="bottom", fontsize=9)
    ax.text(2.4, 6.0, "slope $= +2$", fontsize=8.8, color="0.35", ha="right")
    ax.text(9.2, 8.6, "slope $= -1.5$", fontsize=8.8, color="0.35")
    ax.set_ylabel(r"$v$ (m s$^{-1}$)")
    ax.set_ylim(0, 12.8)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_xlim(0, 12.5)
    for ax in axs:
        for x in (5, 8):
            ax.axvline(x, color="0.6", lw=0.7, ls=":", zorder=0)
    fig.align_ylabels(axs)
    save(fig, "f_ex6", w)


def fig_ex8():
    w = 4.9
    fig, ax = plt.subplots(figsize=(w, 2.8))
    T = [0, 40, 160, 180]
    V = [0, 20, 20, 0]
    ax.fill_between(T, V, color="#d6ead9", lw=0)
    ax.plot(T, V, color="black", lw=1.6)
    for x in (40, 160):
        ax.plot([x, x], [0, 20], color="0.6", lw=0.6, ls=":")
    ax.text(20, 22, "$a = +0.50$", ha="center", fontsize=8.8, color="0.35")
    ax.text(100, 22, "$a = 0$", ha="center", fontsize=8.8, color="0.35")
    ax.text(170, 22, "$a = -1.0$", ha="center", fontsize=8.8, color="0.35")
    ax.text(100, 10, r"stage 2:  $s = 20 \times 120 = 2400$ m", ha="center", fontsize=9)
    ax.text(27, 5.5, "stage 1\n$s = 400$ m", ha="center", fontsize=8.8)
    ax.text(150, 5.5, "stage 3\n$s = 200$ m", ha="center", fontsize=8.8)
    ax.set_xticks([0, 40, 160, 180])
    ax.set_xlim(0, 190)
    ax.set_ylim(0, 25)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    save(fig, "f_ex8", w)


def fig_ex9():
    w = 4.7
    fig, ax = plt.subplots(figsize=(w, 2.9))
    t = np.linspace(0, 14, 300)
    ax.plot(t, 20 * t, color=BLUE, lw=1.5, label=r"car: constant 20 m s$^{-1}$  ($s = 20t$)")
    ax.plot(t, 2 * t ** 2, color=RED, lw=1.5, label=r"police car: from rest at 4.0 m s$^{-2}$  ($s = 2t^2$)")
    ax.plot([0, 10], [200, 200], ls=":", color=GREY, lw=0.8)
    ax.plot([10, 10], [0, 200], ls=":", color=GREY, lw=0.8)
    ax.plot(10, 200, "o", color="black", ms=4.5, zorder=5)
    ax.text(0.3, 205, "$s = 200$ m", fontsize=8.8, va="bottom")
    ax.text(10.3, 55, "$t = 10$ s", fontsize=8.8)
    ax.annotate("they meet where the two\ngraphs cross", xy=(10.1, 198), xytext=(10.4, 100), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 300)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"displacement $s$ (m)")
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "f_ex9", w)


def fig_ex13():
    w = 3.9
    H, u = 1.20, 2.5
    tl = np.sqrt(2 * H / G)
    R = u * tl
    vy = G * tl
    fig, ax = plt.subplots(figsize=(w, 2.6))
    ax.add_patch(Rectangle((-0.9, 0), 0.9, H, fc=EARTHFILL, ec="none"))
    ax.plot([-0.9, 0, 0], [H, H, 0], color=EARTH, lw=1.6)
    ground(ax, -0.9, 2.2)
    t = np.linspace(0, tl, 200)
    ax.plot(u * t, H - 0.5 * G * t ** 2, ls="--", color="black", lw=1.1)
    k = 0.085  # metres of drawing per m/s
    arrow(ax, 0, H, k * u, H, color=BLUE, lw=1.6, ms=9)
    ax.text(0.05, H + 0.1, r"$u = 2.5$ m s$^{-1}$", color=BLUE, fontsize=9.5, va="bottom")
    arrow(ax, R, 0, R + k * u, 0, color=BLUE, lw=1.5, ms=8, z=6)
    arrow(ax, R, 0, R, -k * vy, color=RED, lw=1.5, ms=8, z=6)
    arrow(ax, R, 0, R + k * u, -k * vy, color=GREEN, lw=1.6, ms=9, z=6)
    ax.plot(R, 0, "o", color="black", ms=3.5, zorder=7)
    ax.text(R + 0.38, 0.06, "landing:\n$v_x = 2.5$,  $v_y = -4.85$", fontsize=8.8, va="bottom")
    dimline(ax, -0.45, 0, -0.45, H)
    ax.text(-0.52, H / 2, "1.20 m", rotation=90, ha="right", va="center", fontsize=9)
    dimline(ax, 0, -0.25, R, -0.25)
    ax.text(R / 2, -0.32, f"$x = {R:.2f}$ m", ha="center", va="top", fontsize=9)
    ax.set_xlim(-0.95, 2.3)
    ax.set_ylim(-0.75, 1.55)
    ax.set_aspect("equal")
    plain_axes(ax)
    save(fig, "f_ex13", w)


def fig_ex15():
    w = 4.9
    u, th = 18.0, np.radians(35)
    ux, uy = u * np.cos(th), u * np.sin(th)
    T = 2 * uy / G
    t = np.linspace(0, T, 300)
    tw = 20 / ux
    yw = uy * tw - 0.5 * G * tw ** 2
    fig, ax = plt.subplots(figsize=(w, 2.75))
    ax.plot(ux * t, uy * t - 0.5 * G * t ** 2, ls="--", color="black", lw=1.1)
    ground(ax, -1, 33)
    ax.add_patch(Rectangle((19.6, 0), 0.8, 3.0, fc="#a0522d", ec="black", lw=0.6, zorder=3))
    ax.plot(20, yw, "o", color=RED, ms=5, zorder=5)
    dimline(ax, 20, 3.0, 20, yw, color=RED)
    ax.text(20.8, yw, f"ball at $y = {yw:.2f}$ m", color=RED, fontsize=8.8, va="center")
    ax.text(20.8, 0.8, "wall: 3.0 m high", color="#7a3b18", fontsize=8.8, va="center")
    dimline(ax, 0, -1.1, 20, -1.1)
    ax.text(10, -1.25, "20 m", ha="center", va="top", fontsize=8.8)
    ax.set_xlim(-1, 33)
    ax.set_ylim(-2.6, 7)
    ax.set_xlabel(r"$x$ (m)")
    ax.set_ylabel(r"$y$ (m)")
    save(fig, "f_ex15", w)
    return dict(yw=float(yw))


def fig_ex16():
    w = 4.9
    fig, ax = plt.subplots(figsize=(w, 3.0))
    H, u, ang = 20.0, 15.0, 30
    R, tl, ux, uy = cliff_scene(ax, H, u, ang, 55, True)
    ax.text(5.0, H + 0.7, "30°", fontsize=9)
    ax.text(-6.5, H + 4.6, r"launch: $u = 15$ m s$^{-1}$ at 30°", color=BLUE, fontsize=9, weight="bold")
    ax.text(19, 27.6, f"flight time $t = {tl:.2f}$ s", fontsize=9, ha="center")
    dimline(ax, R + 3, 0, R + 3, H, color=RED)
    ax.text(R + 4, H / 2, r"$h = 20$ m", color=RED, fontsize=10, va="center")
    ax.text(R, -1.4, f"$x = {R:.1f}$ m", ha="center", va="top", fontsize=9)
    ax.set_xlim(-9, 55)
    ax.set_ylim(-4.5, 31)
    ax.set_aspect("equal")
    ax.set_xlabel(r"horizontal distance $x$ (m)")
    ax.set_ylabel("height above ground (m)")
    save(fig, "f_ex16", w)
    return dict(R=float(R), t=float(tl))


if __name__ == "__main__":
    info = {}
    fig_concept()
    fig_walk()
    fig_chord_tangent()
    fig_motion_diagrams()
    fig_three_graphs()
    info["realcar"] = fig_real_car()
    fig_suvat_area()
    fig_throw_up()
    info["sensortoss"] = fig_sensor_toss()
    fig_components()
    fig_drop_vs_throw()
    fig_projectile_vectors()
    fig_angles()
    fig_cliff_general()
    fig_forces()
    info["terminal"] = fig_terminal()
    info["realfalls"] = fig_real_falls()
    info["dragproj"] = fig_drag_projectile()
    info["ggraph"] = fig_g_graph()
    fig_boat()
    fig_ex3()
    fig_ex5()
    fig_ex6()
    fig_ex8()
    fig_ex9()
    fig_ex13()
    info["ex15"] = fig_ex15()
    info["ex16"] = fig_ex16()
    json.dump({"widths": sizes, "info": info}, open(f"{OUT}/figs.json", "w"), indent=1, default=float)
    print(json.dumps(info, indent=1, default=float))
