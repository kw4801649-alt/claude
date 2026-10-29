"""Figures for Chapter 2 (Forces and Momentum), in the same style as figs.py.

Force diagrams are drawn to scale from the numbers in the text; the
"measured" graphs are simulated from the physics with realistic noise.
usage: figs2.py <out dir>
"""
import json
import sys
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon, Arc
from matplotlib.transforms import Affine2D

import figs
from figs import plt, arrow, dimline, plain_axes, smoothstep, save, sizes, G
from figs import BLUE, RED, GREEN, ORANGE, GREY, EARTH, EARTHFILL

OUT = sys.argv[1]
PURPLE = "#6a3d9a"


def force(ax, x, y, dx, dy, color, label=None, lx=0.0, ly=0.0, ha="left", va="center", fs=9, lw=1.8):
    arrow(ax, x, y, x + dx, y + dy, color=color, lw=lw, ms=10, z=6)
    if label:
        ax.text(x + dx + lx, y + dy + ly, label, color=color, ha=ha, va=va, fontsize=fs)


# ------------------------------------------------------------ 2.1 free-body diagrams
def fig_fbd():
    w = 6.0
    fig, axs = plt.subplots(1, 3, figsize=(w, 3.0), gridspec_kw=dict(width_ratios=[0.8, 0.8, 2.1], wspace=0.05))
    k = 0.11  # drawing units per newton for (a) and (b)

    ax = axs[0]
    W = 1.5 * G
    ax.add_patch(Rectangle((-0.8, -0.25), 1.6, 0.5, fc="#d9d9d9", ec="black", lw=0.9, zorder=3))
    ax.add_patch(Rectangle((-1.4, -0.45), 2.8, 0.2, fc=EARTHFILL, ec=EARTH, lw=0.8, zorder=2))
    force(ax, 0, 0, 0, -k * W, RED, f"weight\n{W:.1f} N", lx=0.08, ly=0.25)
    force(ax, 0, 0.25, 0, k * W, BLUE, f"normal force\n{W:.1f} N", lx=0.08, ly=-0.2)
    ax.plot(0, 0, "o", color="black", ms=2.5, zorder=7)

    ax = axs[1]
    W = 1.0 * G
    ax.plot([-0.6, 0.6], [2.2, 2.2], color=EARTH, lw=2.5)
    ax.plot([0, 0], [2.2, 0.25], color="0.4", lw=0.9)
    ax.add_patch(Rectangle((-0.3, -0.25), 0.6, 0.5, fc="#d9d9d9", ec="black", lw=0.9, zorder=3))
    force(ax, 0.0, 0.25, 0, k * W, BLUE, f"tension\n{W:.1f} N", lx=0.1, ly=-0.3)
    force(ax, 0, -0.25, 0, -k * W, RED, f"weight\n{W:.1f} N", lx=0.1, ly=0.25)

    ax = axs[2]
    kc = 0.22  # drawing units per kN for the car
    m = 1200
    Wc = m * G / 1000
    body = FancyBboxPatch((-1.6, 0.25), 3.2, 0.55, boxstyle="round,pad=0.02,rounding_size=0.15",
                          fc="#e8e8e8", ec="black", lw=0.9, zorder=3)
    cab = Polygon([(-0.9, 0.8), (-0.5, 1.2), (0.6, 1.2), (1.0, 0.8)], closed=True, fc="#e8e8e8", ec="black", lw=0.9, zorder=3)
    ax.add_patch(body)
    ax.add_patch(cab)
    for xw in (-1.0, 1.0):
        ax.add_patch(Circle((xw, 0.25), 0.25, fc="0.3", ec="black", zorder=4))
    # normal forces push up on the tyres: 55 % on the front axle, 45 % on the rear
    for xw, f, ha, dx in ((1.0, 0.55, "left", 0.08), (-1.0, 0.45, "right", -0.08)):
        L = kc * Wc * f
        arrow(ax, xw, -L, xw, 0.0, color=BLUE, lw=1.8, ms=10, z=6)
        ax.text(xw + dx, -L, f"normal\n{Wc*f:.1f} kN", color=BLUE, fontsize=8.5, ha=ha, va="center")
    force(ax, 0, 0.55, 0, -kc * Wc, RED, None)
    ax.plot(0, 0.55, "o", color="black", ms=2.5, zorder=7)
    ax.text(-0.08, 0.55 - kc * Wc + 0.1, f"weight\n{Wc:.1f} kN", color=RED, fontsize=8.5, ha="right", va="center")
    force(ax, 1.0, 0.0, kc * 3.0, 0, GREEN, "road on tyres\n3.0 kN", lx=0.06, ly=0.0, fs=8.5)
    force(ax, -1.62, 0.55, -kc * 1.0, 0, ORANGE, "drag\n1.0 kN", lx=-0.05, ly=0.0, ha="right", fs=8.5)
    arrow(ax, 0.3, 1.75, 1.3, 1.75, color="0.35", lw=1.0, ms=8)
    ax.text(0.8, 1.83, "motion, $a = 1.7$ m s$^{-2}$", ha="center", va="bottom", fontsize=8.5, color="0.3")
    for ax in axs[:2]:
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-2.1, 2.4)
        ax.set_aspect("equal")
        plain_axes(ax)
    axs[2].set_xlim(-2.8, 3.1)
    axs[2].set_ylim(-2.3, 2.2)
    axs[2].set_aspect("equal")
    plain_axes(axs[2])
    fig.canvas.draw()
    for ax, lab in zip(axs, ["(a) book on\na table", "(b) hanging\nmass", "(c) car accelerating"]):
        bb = ax.get_position()
        fig.text((bb.x0 + bb.x1) / 2, 0.06, lab, ha="center", va="top", fontsize=9.5)
    save(fig, "f_fbd", w)


# ------------------------------------------------------------ 2.2 friction
def fig_friction():
    w = 5.0
    rng = np.random.default_rng(11)
    m, mus, mud = 2.0, 0.45, 0.30
    FN = m * G
    fs_max, fd = mus * FN, mud * FN
    t = np.arange(0, 12, 0.02)
    pull_rate = 1.5  # N/s
    t_slip = fs_max / pull_rate
    F = np.where(t < t_slip, pull_rate * t, np.nan)
    after = t >= t_slip
    tau = t[after] - t_slip
    slide = fd + (fs_max - fd) * np.exp(-tau / 0.08) + 0.25 * np.sin(2 * np.pi * tau / 0.7) * np.exp(-tau / 6) \
        + rng.normal(0, 0.12, tau.size)
    F[after] = slide
    F[~after] += rng.normal(0, 0.05, (~after).sum())
    fig, ax = plt.subplots(figsize=(w, 3.0))
    ax.plot(t, F, color="black", lw=1.0)
    ax.axhline(fs_max, ls="--", color=RED, lw=0.9)
    ax.axhline(fd, ls="--", color=BLUE, lw=0.9)
    ax.text(0.2, fs_max + 0.25, f"limiting friction $\\mu_s F_N = {fs_max:.1f}$ N", color=RED, fontsize=8.8)
    ax.text(11.8, fd - 0.35, f"dynamic friction $\\mu_d F_N = {fd:.1f}$ N", color=BLUE, fontsize=8.8, ha="right", va="top")
    ax.text(2.4, 1.5, "block at rest:\nstatic friction = pull", fontsize=8.8, color="0.3")
    ax.annotate("block starts\nto slide", xy=(t_slip, fs_max), xytext=(7.0, 10.3), fontsize=8.8,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11.5)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"friction force $F_f$ (N)")
    save(fig, "f_friction", w)


# ------------------------------------------------------------ 2.3 Hooke's law
def fig_hooke():
    w = 4.8
    rng = np.random.default_rng(5)
    k = 25.0
    F = np.arange(0, 6.01, 0.5)
    F_lim = 4.5
    x_true = np.where(F <= F_lim, F / k, F_lim / k + (F - F_lim) / k * (1 + 0.9 * (F - F_lim)))
    x = x_true + rng.normal(0, 0.0015, F.size)
    x[0] = 0
    lin = F <= F_lim
    kfit, c = np.polyfit(x[lin], F[lin], 1)
    fig, ax = plt.subplots(figsize=(w, 3.1))
    xx = np.linspace(0, 0.215, 50)
    ax.plot(xx, kfit * xx + c, color=BLUE, lw=1.2, label=f"best-fit line: gradient $k = {kfit:.1f}$ N m$^{{-1}}$")
    ax.errorbar(x * 100, F, xerr=0.2, fmt="o", ms=3.5, color="black", capsize=2, elinewidth=0.8, label="measurements")
    ax.lines[0].set_xdata(xx * 100)
    ax.annotate("limit of\nproportionality", xy=(x[9] * 100, F[9]), xytext=(9.0, 5.2), fontsize=8.8,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 6.6)
    ax.set_xlabel(r"extension $x$ (cm)")
    ax.set_ylabel(r"force $F$ (N)")
    ax.legend(loc="lower right", fontsize=8.2)
    save(fig, "f_hooke", w)
    return dict(k=float(kfit))


# ------------------------------------------------------------ 2.4 Stokes + buoyancy
def fig_stokes():
    w = 6.0
    rho_s, rho_f, eta = 7850.0, 1260.0, 1.41
    fig, axs = plt.subplots(1, 2, figsize=(w, 2.9), gridspec_kw=dict(width_ratios=[0.8, 1.3], wspace=0.25))
    ax = axs[0]
    r = 2.0e-3
    V = 4 / 3 * np.pi * r ** 3
    W = rho_s * V * G
    B = rho_f * V * G
    D = W - B
    k = 1.6 / W
    ax.add_patch(Rectangle((-1.3, -2.2), 2.6, 4.4, fc="#f3ecd2", ec="0.6", lw=0.6))
    ax.text(-1.2, 2.05, "glycerol", fontsize=8.5, va="top", color="0.35")
    ax.add_patch(Circle((0, 0), 0.22, fc="0.55", ec="black", zorder=5))
    force(ax, 0, -0.22, 0, -k * W, RED, f"weight\n{W*1e3:.2f} mN", lx=0.08, ly=0.3, fs=8.5)
    force(ax, -0.1, 0.22, 0, k * B, GREEN, f"buoyancy\n{B*1e3:.2f} mN", lx=-0.08, ly=0.05, ha="right", fs=8.5)
    force(ax, 0.1, 0.22, 0, k * D, BLUE, f"drag\n{D*1e3:.2f} mN", lx=0.08, ly=-0.05, fs=8.5)
    arrow(ax, 0.85, 0.4, 0.85, -0.4, color="0.5", lw=0.9, ms=7)
    ax.text(0.92, 0, "$v_T$", fontsize=9, color="0.4", va="center")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-2.3, 2.3)
    ax.set_aspect("equal")
    plain_axes(ax)
    ax.set_title("$r = 2.0$ mm, at terminal speed", fontsize=9)

    ax = axs[1]
    rng = np.random.default_rng(2)
    info = {}
    for r_mm, c in ((1.0, RED), (1.5, GREEN), (2.0, BLUE)):
        r = r_mm * 1e-3
        vt = 2 * (rho_s - rho_f) * G * r ** 2 / (9 * eta)
        t = np.arange(0, 10.01, 0.5)
        y = vt * t * 100 + rng.normal(0, 0.12, t.size)
        ax.plot(t, y, "o", ms=3, color=c)
        ax.plot(t, vt * t * 100, color=c, lw=1.0, label=f"$r = {r_mm:.1f}$ mm: $v_T = {vt*100:.2f}$ cm s$^{{-1}}$")
        info[r_mm] = vt
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 45)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel("distance fallen (cm)")
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "f_stokes", w)
    return {str(k_): float(v) for k_, v in info.items()}


# ------------------------------------------------------------ 2.5 lift
def fig_lift():
    w = 5.0
    rng = np.random.default_rng(4)
    m, a0 = 60.0, 1.0
    t = np.arange(0, 16, 0.02)
    a = a0 * (smoothstep((t - 1.0) / 0.4) - smoothstep((t - 2.6) / 0.4)) \
        - a0 * (smoothstep((t - 11.0) / 0.4) - smoothstep((t - 12.6) / 0.4))
    N = m * (G + a) + rng.normal(0, 2.2, t.size) + 3 * np.sin(2 * np.pi * t * 3.1) * (np.abs(np.gradient(a, t)) > 0.1)
    fig, ax = plt.subplots(figsize=(w, 3.0))
    ax.plot(t, N, color="black", lw=0.8)
    for val, lab, c in ((m * (G + a0), f"$m(g+a) = {m*(G+a0):.0f}$ N", RED), (m * G, f"$mg = {m*G:.0f}$ N", GREY),
                        (m * (G - a0), f"$m(g-a) = {m*(G-a0):.0f}$ N", BLUE)):
        ax.axhline(val, ls="--", color=c, lw=0.8)
        ax.text(7.0, val + (4 if c != GREY else -6), lab, color=c, ha="center", va="bottom" if c != GREY else "top", fontsize=8.5)
    ax.text(2.0, 670, "speeding up\n(going up)", ha="center", fontsize=8.5)
    ax.text(7.0, 606, "constant velocity", ha="center", fontsize=8.5)
    ax.text(12.0, 497, "slowing down\n(still going up)", ha="center", fontsize=8.5)
    ax.set_xlim(0, 16)
    ax.set_ylim(480, 700)
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylabel(r"scale reading $F_N$ (N)")
    save(fig, "f_lift", w)


# ------------------------------------------------------------ 2.6 incline
def fig_incline():
    w = 4.8
    th = np.radians(25)
    m = 4.0
    W = m * G
    Fpar, Fperp = W * np.sin(th), W * np.cos(th)
    k = 0.06
    fig, ax = plt.subplots(figsize=(w, 3.3))
    L = 7.0
    ax.add_patch(Polygon([(0, 0), (L, 0), (L, L * np.tan(th))], closed=True, fc=EARTHFILL, ec=EARTH, lw=1.2))
    ax.add_patch(Arc((0, 0), 2.4, 2.4, theta1=0, theta2=25, lw=0.8))
    ax.text(1.35, 0.22, "25°", fontsize=9)
    s = 4.0  # block position along the slope
    ux, uy = np.cos(th), np.sin(th)   # along the slope (up)
    nx, ny = -np.sin(th), np.cos(th)  # out of the slope
    bw, bh = 1.2, 0.8
    base = np.array([s * ux, s * uy])
    corners = [base - bw / 2 * np.array([ux, uy]), base + bw / 2 * np.array([ux, uy]),
               base + bw / 2 * np.array([ux, uy]) + bh * np.array([nx, ny]),
               base - bw / 2 * np.array([ux, uy]) + bh * np.array([nx, ny])]
    ax.add_patch(Polygon(corners, closed=True, fc="#d9d9d9", ec="black", lw=0.9, zorder=3))
    c = base + bh / 2 * np.array([nx, ny])
    force(ax, c[0], c[1], 0, -k * W, RED, f"weight $mg$ = {W:.0f} N", lx=0.1, ly=-0.05, fs=8.8)
    arrow(ax, c[0], c[1], c[0] - k * Fpar * ux, c[1] - k * Fpar * uy, color=RED, lw=1.0, ls="--", ms=8, z=5)
    arrow(ax, c[0], c[1], c[0] - k * Fperp * nx, c[1] - k * Fperp * ny, color=RED, lw=1.0, ls="--", ms=8, z=5)
    p1 = c - k * Fpar * np.array([ux, uy])
    ax.text(p1[0] - 0.1, p1[1] - 0.05, f"$mg\\sin\\theta$\n= {Fpar:.1f} N", color=RED, fontsize=8.5, ha="right", va="top")
    p2 = c - k * Fperp * np.array([nx, ny])
    ax.text(p2[0] + 0.12, p2[1] + 0.05, f"$mg\\cos\\theta$ = {Fperp:.1f} N", color=RED, fontsize=8.5, va="top")
    top = base + bh * np.array([nx, ny])
    force(ax, base[0], base[1] + 0.02, k * Fperp * nx, k * Fperp * ny, BLUE, f"normal\n{Fperp:.1f} N", lx=-0.1, ly=0.15,
          ha="right", fs=8.5)
    fpt = base + bw / 2 * np.array([ux, uy])
    force(ax, fpt[0], fpt[1], k * Fpar * ux, k * Fpar * uy, GREEN, f"friction {Fpar:.1f} N", lx=0.1, ly=-0.15, fs=8.5)
    ax.set_xlim(-0.3, L + 0.4)
    ax.set_ylim(-0.4, L * np.tan(th) + 0.9)
    ax.set_aspect("equal")
    plain_axes(ax)
    save(fig, "f_incline", w)


# ------------------------------------------------------------ 2.7 third law
def skater(ax, x, scale, facing):
    """Simple stick figure standing at x."""
    h = 1.6 * scale
    ax.add_patch(Circle((x, h + 0.16 * scale), 0.15 * scale, fc="white", ec="black", lw=0.9, zorder=4))
    ax.plot([x, x], [0.55 * h, h], color="black", lw=1.4)
    ax.plot([x, x - 0.18 * scale], [0.55 * h, 0.02], color="black", lw=1.4)
    ax.plot([x, x + 0.18 * scale], [0.55 * h, 0.02], color="black", lw=1.4)
    ax.plot([x, x + facing * 0.42 * scale], [0.9 * h, 0.82 * h], color="black", lw=1.4)


def fig_thirdlaw():
    w = 6.0
    fig, axs = plt.subplots(1, 2, figsize=(w, 2.9), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.08))
    ax = axs[0]
    ax.plot([-3.2, 3.2], [0, 0], color="#9cc3e6", lw=3)
    skater(ax, -0.5, 1.15, +1)
    skater(ax, 0.45, 0.85, -1)
    force(ax, 0.1, 1.55, 1.3, 0, BLUE, None)
    force(ax, -0.1, 1.55, -1.3, 0, RED, None)
    ax.text(1.5, 1.75, "force of A on B\n100 N", color=BLUE, fontsize=8.5, va="bottom", ha="center")
    ax.text(-1.5, 1.75, "force of B on A\n100 N", color=RED, fontsize=8.5, va="bottom", ha="center")
    ax.text(-1.4, -0.35, "A: 80 kg\n$a = 1.25$ m s$^{-2}$", ha="center", va="top", fontsize=8.5)
    ax.text(1.4, -0.35, "B: 50 kg\n$a = 2.0$ m s$^{-2}$", ha="center", va="top", fontsize=8.5)
    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-1.4, 3.0)
    ax.set_aspect("equal")
    plain_axes(ax)
    ax.set_title("(a) skaters pushing apart", fontsize=9.5)

    ax = axs[1]
    ax.add_patch(Rectangle((-0.7, 1.55), 1.4, 0.35, fc="#d9d9d9", ec="black", lw=0.9))
    ax.text(0, 1.725, "book", ha="center", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((-1.5, 0.5), 3.0, 0.25, fc=EARTHFILL, ec=EARTH, lw=0.9))
    ax.text(-1.45, 0.625, "table", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((-1.8, -1.9), 3.6, 0.6, fc="#cfe3c4", ec="0.4", lw=0.8))
    ax.text(0, -1.6, "Earth", ha="center", va="center", fontsize=8.5)
    # pair 1 (gravitational): Earth on book / book on Earth
    force(ax, -0.3, 1.55, 0, -0.6, RED, "Earth pulls book", lx=-0.06, ly=0.3, ha="right", fs=8)
    force(ax, -0.3, -1.3, 0, 0.6, RED, "book pulls Earth", lx=-0.06, ly=-0.3, ha="right", fs=8)
    # pair 2 (contact): table on book / book on table
    force(ax, 0.35, 1.9, 0, 0.6, BLUE, "table pushes book", lx=0.07, ly=-0.3, fs=8)
    force(ax, 0.35, 1.35, 0, -0.6, BLUE, "book pushes table", lx=0.07, ly=0.3, fs=8)
    ax.text(0, -2.1, "red: gravitational pair     blue: contact pair", ha="center", va="top", fontsize=8, color="0.3")
    ax.set_xlim(-2.2, 2.4)
    ax.set_ylim(-2.5, 2.7)
    ax.set_aspect("equal")
    plain_axes(ax)
    ax.set_title("(b) book on a table (pulled apart)", fontsize=9.5)
    save(fig, "f_thirdlaw", w)


# ------------------------------------------------------------ 2.8 kick
def pulse(t, t0, dur, a=2.0, b=2.6):
    x = np.clip((t - t0) / dur, 0, 1)
    return x ** a * (1 - x) ** b


def fig_kick():
    w = 5.0
    rng = np.random.default_rng(8)
    m, v = 0.43, 26.0
    J = m * v
    dur = 9.0e-3
    t = np.arange(-2e-3, 12e-3, 1e-4)
    shape = pulse(t, 0, dur)
    F = shape * J / np.trapezoid(shape, t)
    Fm = F + rng.normal(0, 15, t.size)
    Favg = J / dur
    fig, ax = plt.subplots(figsize=(w, 3.0))
    ax.fill_between(t * 1e3, 0, F, color="#cfdcf3", lw=0)
    ax.plot(t * 1e3, Fm, color="black", lw=0.8)
    ax.plot([0, 0, dur * 1e3, dur * 1e3], [0, Favg, Favg, 0], ls="--", color=RED, lw=1.0)
    ax.text(dur * 1e3 + 0.2, Favg, f"average force\n$= J/\\Delta t \\approx {Favg/1e3:.2f}$ kN", color=RED, fontsize=8.5, va="center")
    ax.text(3.2, 500, f"area = impulse\n$J = {J:.1f}$ N s", color=BLUE, fontsize=9, ha="center")
    ax.text(t[F.argmax()] * 1e3 + 0.3, F.max(), f"peak {F.max()/1e3:.1f} kN", fontsize=8.5, va="bottom")
    dimline(ax, 0, -150, dur * 1e3, -150)
    ax.text(dur * 1e3 / 2, -190, "contact time 9 ms", ha="center", va="top", fontsize=8.5)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xlim(-2, 14)
    ax.set_ylim(-420, 2850)
    ax.set_xlabel(r"time $t$ (ms)")
    ax.set_ylabel(r"force $F$ (N)")
    save(fig, "f_kick", w)
    return dict(peak=float(F.max()), avg=float(Favg))


# ------------------------------------------------------------ 2.9 airbag
def fig_airbag():
    w = 5.0
    m, v = 5.0, 14.0
    J = m * v
    t = np.linspace(-5e-3, 80e-3, 4000)
    fig, ax = plt.subplots(figsize=(w, 3.0))
    out = {}
    for dur, c, lab in ((5e-3, RED, "rigid dashboard"), (60e-3, BLUE, "airbag")):
        shape = pulse(t, 0, dur, 2.0, 2.0)
        F = shape * J / np.trapezoid(shape, t)
        ax.fill_between(t * 1e3, 0, F / 1e3, color=c, alpha=0.15, lw=0)
        ax.plot(t * 1e3, F / 1e3, color=c, lw=1.4, label=f"{lab}: $\\Delta t$ = {dur*1e3:.0f} ms, peak {F.max()/1e3:.1f} kN")
        out[lab] = float(F.max())
    ax.text(40, 6.5, "both areas = 70 N s\n(same change of momentum)", fontsize=8.8, ha="center")
    ax.set_xlim(-5, 80)
    ax.set_ylim(0, 29)
    ax.set_xlabel(r"time $t$ (ms)")
    ax.set_ylabel(r"force on head $F$ (kN)")
    ax.legend(loc="upper right", fontsize=8.2)
    save(fig, "f_airbag", w)
    return out


# ------------------------------------------------------------ 2.10 trolleys
def fig_trolleys():
    w = 5.0
    rng = np.random.default_rng(6)
    m1 = m2 = 0.50
    u1 = 0.60
    fr = 0.02  # m/s^2 rolling-friction deceleration
    t = np.arange(0, 3.0, 0.001)
    tc, dur = 1.2, 0.04
    # collision force from a smooth pulse, momentum transferred = m1*u1*m2/(m1+m2) (sticky)
    shape = pulse(t, tc, dur, 2, 2)
    Fc = shape / np.trapezoid(shape, t) * (m1 * m2 / (m1 + m2)) * (u1 - fr * tc)
    v1 = np.empty_like(t)
    v2 = np.empty_like(t)
    v1[0], v2[0] = u1, 0.0
    dt = t[1] - t[0]
    for i in range(1, t.size):
        f1 = -fr if v1[i - 1] > 0 else 0
        f2 = -fr if v2[i - 1] > 0 else 0
        v1[i] = v1[i - 1] + (f1 - Fc[i - 1] / m1) * dt
        v2[i] = v2[i - 1] + (f2 + Fc[i - 1] / m2) * dt
    ts = np.arange(0, 3.0, 0.05)
    s1 = np.interp(ts, t, v1) + rng.normal(0, 0.006, ts.size)
    s2 = np.interp(ts, t, v2) + rng.normal(0, 0.006, ts.size)
    fig, axs = plt.subplots(2, 1, figsize=(w, 4.4), sharex=True, gridspec_kw=dict(hspace=0.1))
    ax = axs[0]
    ax.plot(t, v1, color=RED, lw=1.0)
    ax.plot(t, v2, color=BLUE, lw=1.0)
    ax.plot(ts, s1, "o", ms=2.8, color=RED, label="trolley A")
    ax.plot(ts, s2, "s", ms=2.6, color=BLUE, label="trolley B")
    ax.axvline(tc + dur / 2, ls=":", color="0.6", lw=0.7)
    ax.text(tc + 0.05, 0.66, "collision", fontsize=8.5, color="0.3")
    ax.set_ylabel(r"velocity $v$ (m s$^{-1}$)")
    ax.set_ylim(-0.05, 0.75)
    ax.legend(loc="center right", fontsize=8.2)
    ax = axs[1]
    p1, p2 = m1 * v1, m2 * v2
    ax.plot(t, p1, color=RED, lw=1.1, label="A")
    ax.plot(t, p2, color=BLUE, lw=1.1, ls="--", label="B")
    ax.plot(t, p1 + p2, color="black", lw=1.6, label="total")
    ax.axvline(tc + dur / 2, ls=":", color="0.6", lw=0.7)
    ax.set_ylabel(r"momentum $p$ (kg m s$^{-1}$)")
    ax.set_xlabel(r"time $t$ (s)")
    ax.set_ylim(-0.02, 0.36)
    ax.set_xlim(0, 3.0)
    ax.legend(loc="center right", fontsize=8.2, ncol=3)
    fig.align_ylabels(axs)
    save(fig, "f_trolleys", w)


# ------------------------------------------------------------ 2.11 explosion
def trolley(ax, x, wdt, label, color):
    ax.add_patch(Rectangle((x - wdt / 2, 0.18), wdt, 0.5, fc=color, ec="black", lw=0.9, zorder=3))
    for dx in (-wdt * 0.3, wdt * 0.3):
        ax.add_patch(Circle((x + dx, 0.12), 0.1, fc="0.3", ec="black", zorder=4))
    ax.text(x, 0.43, label, ha="center", va="center", fontsize=8.5, zorder=5)


def fig_explosion():
    w = 5.4
    fig, axs = plt.subplots(2, 1, figsize=(w, 2.9), gridspec_kw=dict(hspace=0.25))
    for ax in axs:
        ax.plot([-3.2, 3.2], [0, 0], color=EARTH, lw=1.4)
        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-0.25, 1.3)
        ax.set_aspect("equal")
        plain_axes(ax)
    ax = axs[0]
    trolley(ax, -0.55, 0.9, "1.0 kg", "#f3d3d3")
    trolley(ax, 0.75, 1.5, "2.0 kg", "#cfdcf3")
    xs = np.linspace(-0.1, 0.0, 9)
    ax.plot(np.linspace(-0.1, 0.0, 9), 0.43 + 0.08 * np.array([0, 1, -1, 1, -1, 1, -1, 1, 0]), color="black", lw=0.8)
    ax.text(-3.1, 1.15, "Before: at rest, total momentum = 0", fontsize=9, va="top")
    ax = axs[1]
    trolley(ax, -1.6, 0.9, "1.0 kg", "#f3d3d3")
    trolley(ax, 1.75, 1.5, "2.0 kg", "#cfdcf3")
    k = 2.5
    arrow(ax, -1.6, 0.85, -1.6 - k * 0.40, 0.85, color=RED, lw=1.6)
    ax.text(-2.1, 0.95, r"0.40 m s$^{-1}$", color=RED, ha="center", va="bottom", fontsize=8.5)
    arrow(ax, 1.75, 0.85, 1.75 + k * 0.20, 0.85, color=BLUE, lw=1.6)
    ax.text(2.0, 0.95, r"0.20 m s$^{-1}$", color=BLUE, ha="center", va="bottom", fontsize=8.5)
    ax.text(-0.1, 0.45, "$p = -0.40 + 0.40 = 0$", ha="center", va="center", fontsize=9)
    ax.text(-3.1, 1.25, "After", fontsize=9, va="top")
    save(fig, "f_explosion", w)


# ------------------------------------------------------------ 2.12 circular motion
def fig_circle():
    w = 4.6
    fig, ax = plt.subplots(figsize=(w, 3.4))
    R = 1.6
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(R * np.cos(th), R * np.sin(th), color="black", lw=1.0)
    ax.plot(0, 0, "+", color="black", ms=7)
    for ang in np.radians([20, 110, 200, 290]):
        x, y = R * np.cos(ang), R * np.sin(ang)
        arrow(ax, x, y, x - 0.9 * np.sin(ang), y + 0.9 * np.cos(ang), color=BLUE, lw=1.6)
        arrow(ax, x, y, x - 0.55 * np.cos(ang), y - 0.55 * np.sin(ang), color=RED, lw=1.6)
        ax.plot(x, y, "o", color="black", ms=5, zorder=6)
    ang = np.radians(20)
    ax.text(R * np.cos(ang) - 0.9 * np.sin(ang) + 0.05, R * np.sin(ang) + 0.9 * np.cos(ang), r"$\mathbf{v}$", color=BLUE, fontsize=11)
    ax.text(R * np.cos(ang) - 0.6 * np.cos(ang), R * np.sin(ang) - 0.55 * np.sin(ang) - 0.25, r"$\mathbf{a}$", color=RED, fontsize=11)
    ax.plot([0, R * np.cos(np.radians(200))], [0, R * np.sin(np.radians(200))], ls=":", color="0.5", lw=0.8)
    ax.text(-0.85, -0.1, "$r$", fontsize=10, color="0.3")
    # inset: velocity change over a short time (vectors drawn tail to tail)
    a1, a2 = np.radians(40), np.radians(80)
    ox, oy = 3.3, -1.0
    L = 1.3
    v1 = L * np.array([-np.sin(a1), np.cos(a1)])
    v2 = L * np.array([-np.sin(a2), np.cos(a2)])
    arrow(ax, ox, oy, ox + v1[0], oy + v1[1], color=BLUE, lw=1.3, ms=8)
    arrow(ax, ox, oy, ox + v2[0], oy + v2[1], color=BLUE, lw=1.3, ms=8)
    arrow(ax, ox + v1[0], oy + v1[1], ox + v2[0], oy + v2[1], color=RED, lw=1.3, ms=8)
    ax.text(ox + v1[0] / 2 + 0.12, oy + v1[1] / 2 - 0.05, r"$\mathbf{v}_1$", color=BLUE, fontsize=9)
    ax.text(ox + v2[0] / 2 - 0.05, oy + v2[1] / 2 - 0.3, r"$\mathbf{v}_2$", color=BLUE, fontsize=9)
    mid = np.array([ox, oy]) + (v1 + v2) / 2
    ax.text(mid[0] - 0.55, mid[1] + 0.1, r"$\Delta\mathbf{v}$", color=RED, fontsize=9)
    ax.text(ox - 0.3, oy - 0.25, "inset: $\\Delta\\mathbf{v}$ points\nto the centre", fontsize=8, ha="center", va="top", color="0.3")
    ax.set_xlim(-2.7, 4.2)
    ax.set_ylim(-2.3, 2.6)
    ax.set_aspect("equal")
    plain_axes(ax)
    save(fig, "f_circle", w)


# ------------------------------------------------------------ 2.13 conical pendulum
def fig_conical():
    w = 4.6
    m, L, th = 0.20, 0.80, np.radians(30)
    r = L * np.sin(th)
    h = L * np.cos(th)
    T = m * G / np.cos(th)
    v = np.sqrt(T * np.sin(th) * r / m)
    fig, ax = plt.subplots(figsize=(w, 3.6))
    ax.plot([-0.25, 0.25], [h, h], color=EARTH, lw=3)
    ax.plot([0, 0], [h, -0.05], ls=":", color="0.5", lw=0.8)
    ex = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(ex), 0.08 * np.sin(ex), ls="--", color="0.5", lw=0.8)
    ax.plot([0, r], [h, 0], color="0.3", lw=1.0)
    ax.add_patch(Arc((0, h), 0.3, 0.3, theta1=270, theta2=300, lw=0.8))
    ax.text(0.04, h - 0.25, "30°", fontsize=8.5)
    ax.add_patch(Circle((r, 0), 0.03, fc="0.4", ec="black", zorder=6))
    k = 0.13  # m of drawing per N
    force(ax, r, 0, -k * T * np.sin(th), k * T * np.cos(th), BLUE, f"tension {T:.2f} N", lx=0.02, ly=0.05, fs=8.5)
    arrow(ax, r, 0, r, k * T * np.cos(th), color=BLUE, lw=0.9, ls="--", ms=7, z=5)
    arrow(ax, r, 0, r - k * T * np.sin(th), 0, color=BLUE, lw=0.9, ls="--", ms=7, z=5)
    ax.text(r + 0.02, k * T * np.cos(th) * 0.55, f"$T\\cos\\theta$\n= {T*np.cos(th):.2f} N", color=BLUE, fontsize=8.2)
    ax.text(r - k * T * np.sin(th) - 0.03, 0.045, f"$T\\sin\\theta = {T*np.sin(th):.2f}$ N", color=BLUE, fontsize=8.2, ha="right", va="bottom")
    force(ax, r, 0, 0, -k * m * G, RED, f"weight {m*G:.2f} N", lx=0.02, ly=0.0, fs=8.5)
    ax.text(-0.02, 0.1, "centre", fontsize=8, ha="right", color="0.4")
    dimline(ax, 0, -0.42, r, -0.42)
    ax.text(r / 2, -0.45, f"$r = L\\sin\\theta = {r:.2f}$ m", ha="center", va="top", fontsize=8.5)
    ax.text(-0.05, h / 2, f"$L$ = {L:.2f} m", fontsize=8.5, ha="right")
    ax.set_xlim(-0.55, 0.85)
    ax.set_ylim(-0.6, h + 0.12)
    ax.set_aspect("equal")
    plain_axes(ax)
    save(fig, "f_conical", w)
    return dict(T=float(T), v=float(v), period=float(2 * np.pi * r / v))


if __name__ == "__main__":
    info = {}
    fig_fbd()
    fig_friction()
    info["hooke"] = fig_hooke()
    info["stokes"] = fig_stokes()
    fig_lift()
    fig_incline()
    fig_thirdlaw()
    info["kick"] = fig_kick()
    info["airbag"] = fig_airbag()
    fig_trolleys()
    fig_explosion()
    fig_circle()
    info["conical"] = fig_conical()
    old = json.load(open(f"{OUT}/figs.json"))
    old["widths"].update(sizes)
    old["info"]["ch2"] = info
    json.dump(old, open(f"{OUT}/figs.json", "w"), indent=1, default=float)
    print(json.dumps(info, indent=1, default=float))
