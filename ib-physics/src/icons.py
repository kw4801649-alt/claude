"""Small, realistic-looking objects drawn with matplotlib patches, for adding to graphs.

Each function draws into an axes in data coordinates, around a reference point and with a
size `s`; most expect an equal-aspect axes (use `inset(ax, bounds)` to get one on any graph).
"""
import numpy as np
from matplotlib.patches import (Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, Wedge, Arc,
                                PathPatch)
from matplotlib.path import Path
import matplotlib.transforms as mtransforms

STEEL = "#8a8f96"
WOOD = "#b98a55"
WOOD_DARK = "#8a6134"
SKIN = "#e8b98f"
WATER = "#7fb2d9"
GLASS = "#dfeef7"


def inset(ax, bounds, xlim=(0, 1), ylim=(0, 1)):
    """An invisible, equal-aspect inset axes for drawing an object on top of a graph."""
    ia = ax.inset_axes(bounds)
    ia.set_xlim(*xlim)
    ia.set_ylim(*ylim)
    ia.set_aspect("equal", adjustable="datalim")
    ia.set_axis_off()
    ia.patch.set_alpha(0)
    return ia


def shaded_ball(ax, x, y, r, color="#c0392b", z=6, edge="black"):
    """A sphere with a soft highlight (concentric discs shifted towards the light)."""
    base = np.array(__import__("matplotlib").colors.to_rgb(color))
    ax.add_patch(Circle((x, y), r, fc=base * 0.75, ec=edge, lw=0.5, zorder=z))
    n = 7
    for k in range(1, n + 1):
        f = k / n
        rr = r * (1 - 0.82 * f)
        c = base * (0.75 + 0.25 * f) + (1 - base) * 0.55 * f ** 2
        ax.add_patch(Circle((x - 0.35 * r * f, y + 0.35 * r * f), rr, fc=np.clip(c, 0, 1), ec="none", zorder=z + 0.01 * k))


def ball_markers(ax, xs, ys, size=7, color="#c0392b", z=6):
    """Shaded balls as markers, so they stay round on axes of any aspect ratio."""
    base = np.array(__import__("matplotlib").colors.to_rgb(color))
    ax.plot(xs, ys, "o", ms=size, mfc=base * 0.72, mec="black", mew=0.4, zorder=z, ls="none")
    for k, f in enumerate((0.35, 0.65, 0.9)):
        off = mtransforms.offset_copy(ax.transData, fig=ax.figure, x=-0.13 * size * f, y=0.13 * size * f, units="points")
        c = np.clip(base * (0.8 + 0.2 * f) + (1 - base) * 0.6 * f ** 2, 0, 1)
        ax.plot(xs, ys, "o", ms=size * (1 - 0.7 * f), mfc=c, mec="none", zorder=z + 0.1 * (k + 1), ls="none",
                transform=off)


def car(ax, x, y, s=1.0, color="#2f5d9e", facing=1):
    """A hatchback seen from the side; (x, y) is the middle of the road contact line."""
    f = facing
    def P(pts):
        return [(x + f * px * s, y + py * s) for px, py in pts]
    body = P([(-1.0, 0.18), (-1.0, 0.42), (-0.82, 0.48), (-0.55, 0.75), (0.25, 0.77), (0.55, 0.5), (0.95, 0.44),
              (1.02, 0.3), (1.0, 0.18)])
    ax.add_patch(Polygon(body, closed=True, fc=color, ec="black", lw=0.6, zorder=5, joinstyle="round"))
    ax.add_patch(Polygon(P([(-0.5, 0.5), (-0.42, 0.7), (-0.12, 0.71), (-0.12, 0.5)]), closed=True, fc="#cfe6f5", ec="black", lw=0.4, zorder=6))
    ax.add_patch(Polygon(P([(-0.05, 0.5), (-0.05, 0.71), (0.2, 0.71), (0.42, 0.5)]), closed=True, fc="#cfe6f5", ec="black", lw=0.4, zorder=6))
    ax.add_patch(Rectangle((x + f * 0.9 * s - (0.08 * s if f > 0 else 0), y + 0.33 * s), 0.08 * s, 0.05 * s, fc="#ffe9a6", ec="black", lw=0.3, zorder=6))
    for px in (-0.6, 0.6):
        cx = x + f * px * s
        ax.add_patch(Circle((cx, y + 0.17 * s), 0.17 * s, fc="#222222", ec="black", lw=0.5, zorder=7))
        ax.add_patch(Circle((cx, y + 0.17 * s), 0.08 * s, fc="#bfc4c9", ec="#555555", lw=0.3, zorder=8))


def traffic_light(ax, x, y, s=1.0, lit="red"):
    """A traffic light on a pole; (x, y) is the foot of the pole."""
    ax.add_patch(Rectangle((x - 0.03 * s, y), 0.06 * s, 1.0 * s, fc="#555555", ec="black", lw=0.4, zorder=5))
    ax.add_patch(FancyBboxPatch((x - 0.13 * s, y + 0.95 * s), 0.26 * s, 0.62 * s, boxstyle="round,pad=0.0,rounding_size=0.05",
                                fc="#2b2b2b", ec="black", lw=0.5, zorder=6))
    for k, (c_on, c_off, name) in enumerate((("#ff3b30", "#5a1f1c", "red"), ("#ffb000", "#5a4410", "amber"),
                                             ("#30d158", "#163f22", "green"))):
        cy = y + (1.47 - 0.2 * k) * s
        on = lit == name
        ax.add_patch(Circle((x, cy), 0.07 * s, fc=c_on if on else c_off, ec="black", lw=0.3, zorder=7))
        if on:
            ax.add_patch(Circle((x, cy), 0.11 * s, fc=c_on, alpha=0.25, ec="none", zorder=6.5))


def person(ax, x, y, s=1.0, color="#3b5b8a", arms="down"):
    """A simple standing figure; (x, y) is between the feet."""
    ax.add_patch(Circle((x, y + 1.62 * s), 0.13 * s, fc=SKIN, ec="black", lw=0.4, zorder=6))
    ax.add_patch(Polygon([(x - 0.17 * s, y + 0.85 * s), (x - 0.2 * s, y + 1.42 * s), (x + 0.2 * s, y + 1.42 * s),
                          (x + 0.17 * s, y + 0.85 * s)], closed=True, fc=color, ec="black", lw=0.4, zorder=5))
    ax.add_patch(Polygon([(x - 0.16 * s, y + 0.87 * s), (x - 0.13 * s, y), (x - 0.03 * s, y), (x, y + 0.6 * s),
                          (x + 0.03 * s, y), (x + 0.13 * s, y), (x + 0.16 * s, y + 0.87 * s)], closed=True,
                         fc="#3a3a3a", ec="black", lw=0.4, zorder=5))
    if arms == "down":
        for sx in (-1, 1):
            ax.plot([x + sx * 0.2 * s, x + sx * 0.25 * s], [y + 1.38 * s, y + 0.9 * s], color=color, lw=2.2 * s, solid_capstyle="round", zorder=4)
    elif arms == "up":
        ax.plot([x + 0.2 * s, x + 0.32 * s], [y + 1.38 * s, y + 1.9 * s], color=color, lw=2.2 * s, solid_capstyle="round", zorder=4)
        ax.plot([x - 0.2 * s, x - 0.25 * s], [y + 1.38 * s, y + 0.9 * s], color=color, lw=2.2 * s, solid_capstyle="round", zorder=4)


def skydiver(ax, x, y, s=1.0, color="#e4572e"):
    """Free-fall position, seen from the side: belly to earth, arms and legs spread."""
    ax.add_patch(Ellipse((x, y), 0.9 * s, 0.22 * s, fc=color, ec="black", lw=0.4, zorder=6))
    ax.add_patch(Circle((x + 0.55 * s, y + 0.02 * s), 0.12 * s, fc="#333333", ec="black", lw=0.4, zorder=6))
    for (dx, dy) in ((0.25, 0.3), (0.35, 0.22)):
        ax.plot([x + 0.25 * s, x + (0.25 + dx) * s], [y + 0.05 * s, y + dy * s], color=color, lw=2.0 * s, solid_capstyle="round", zorder=5)
    for (dx, dy) in ((-0.3, 0.25), (-0.4, 0.15)):
        ax.plot([x - 0.35 * s, x + (-0.35 + dx) * s], [y, y + dy * s], color="#333333", lw=2.2 * s, solid_capstyle="round", zorder=5)


def parachutist(ax, x, y, s=1.0, canopy="#f0a202"):
    """A person hanging under an open canopy; (x, y) is the person's feet."""
    person(ax, x, y, 0.55 * s, color="#e4572e", arms="down")
    top = y + 2.6 * s
    w = 1.5 * s
    ax.add_patch(Wedge((x, top), w / 2, 0, 180, fc=canopy, ec="black", lw=0.5, zorder=5))
    for k in range(1, 4):
        xx = x - w / 2 + k * w / 4
        ax.plot([xx, xx], [top, top + np.sqrt(max((w / 2) ** 2 - (xx - x) ** 2, 0))], color="#a86b00", lw=0.5, zorder=6)
    for xx in np.linspace(x - w / 2, x + w / 2, 5):
        ax.plot([xx, x], [top, y + 0.85 * s], color="0.35", lw=0.4, zorder=4)


def boat(ax, x, y, s=1.0, color="#d64933", facing=1):
    """A small motor boat sitting on the water line y."""
    f = facing
    hull = [(x - 0.9 * s * f, y + 0.25 * s), (x + 0.75 * s * f, y + 0.25 * s), (x + 1.0 * s * f, y + 0.42 * s),
            (x + 0.6 * s * f, y - 0.12 * s), (x - 0.8 * s * f, y - 0.12 * s)]
    ax.add_patch(Polygon(hull, closed=True, fc=color, ec="black", lw=0.5, zorder=6))
    ax.add_patch(Rectangle((x - 0.6 * s if f > 0 else x + 0.05 * s, y + 0.25 * s), 0.55 * s, 0.32 * s, fc="white", ec="black", lw=0.4, zorder=6))
    ax.add_patch(Rectangle((x - 0.5 * s if f > 0 else x + 0.15 * s, y + 0.36 * s), 0.35 * s, 0.13 * s, fc="#9fd0ee", ec="black", lw=0.3, zorder=7))
    # wake
    for k in range(3):
        xx = x - (1.1 + 0.25 * k) * s * f
        ax.add_patch(Arc((xx, y + 0.02 * s), 0.25 * s, 0.12 * s, theta1=0, theta2=180, color="white", lw=0.8, zorder=6))


def water(ax, x0, x1, y0, y1, n_waves=14):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=WATER, ec="none", zorder=1))
    xs = np.linspace(x0, x1, 400)
    for k, yy in enumerate(np.linspace(y0 + 0.2 * (y1 - y0), y1 - 0.12 * (y1 - y0), 3)):
        ax.plot(xs, yy + 0.02 * (y1 - y0) * np.sin(2 * np.pi * n_waves * (xs - x0) / (x1 - x0) + k), color="white", lw=0.6, alpha=0.8, zorder=2)


def cliff(ax, x0, x1, y_top, y_bottom=0, sea=True, xmax=None):
    """A rocky cliff face from x0..x1 (top at y_top), optionally with sea at its foot."""
    rng = np.random.default_rng(1)
    ys = np.linspace(y_bottom, y_top, 25)
    face = x1 + rng.normal(0, 0.012 * (y_top - y_bottom), ys.size)
    face[-1] = x1
    pts = [(x0, y_bottom)] + list(zip(face, ys)) + [(x0, y_top)]
    ax.add_patch(Polygon(pts, closed=True, fc="#b9a68a", ec="#6b5536", lw=0.8, zorder=2))
    for k in range(18):
        yy = rng.uniform(y_bottom, y_top)
        xx = rng.uniform(x0, x1 - 0.05 * (x1 - x0))
        ax.plot([xx, xx + 0.15 * (x1 - x0)], [yy, yy + rng.normal(0, 0.01) * (y_top - y_bottom)], color="#8d7a5e", lw=0.5, zorder=3)
    ax.add_patch(Rectangle((x0, y_top - 0.02 * (y_top - y_bottom)), x1 - x0, 0.03 * (y_top - y_bottom), fc="#5f8f3e", ec="none", zorder=3))
    if sea and xmax is not None:
        water(ax, x1, xmax, y_bottom - 0.12 * (y_top - y_bottom), y_bottom, n_waves=20)


def grass(ax, x0, x1, y=0, depth=1.0):
    ax.add_patch(Rectangle((x0, y - depth), x1 - x0, depth, fc="#7aa95c", ec="none", zorder=1))
    ax.plot([x0, x1], [y, y], color="#4e7a35", lw=1.0, zorder=2)


def lift_car(ax, x, y, s=1.0):
    """A lift cabin on its cable with a person standing on bathroom scales."""
    ax.plot([x, x], [y + 2.2 * s, y + 3.2 * s], color="0.3", lw=1.0, zorder=3)
    ax.add_patch(Rectangle((x - 0.8 * s, y), 1.6 * s, 2.2 * s, fc="#e9e4da", ec="black", lw=0.7, zorder=4))
    ax.add_patch(Rectangle((x - 0.8 * s, y), 1.6 * s, 0.12 * s, fc="#777777", ec="black", lw=0.5, zorder=5))
    ax.add_patch(Rectangle((x - 0.3 * s, y + 0.12 * s), 0.6 * s, 0.1 * s, fc="#f4f4f4", ec="black", lw=0.4, zorder=6))
    ax.add_patch(Rectangle((x - 0.1 * s, y + 0.14 * s), 0.2 * s, 0.06 * s, fc="#a7e3a1", ec="black", lw=0.3, zorder=7))
    person(ax, x, y + 0.22 * s, 0.95 * s)


def force_sensor_setup(ax, x, y, s=1.0):
    """A wooden block on a bench, pulled through a string by a hand-held force sensor."""
    ax.add_patch(Rectangle((x - 1.6 * s, y - 0.25 * s), 3.4 * s, 0.25 * s, fc="#c9b28f", ec="black", lw=0.5, zorder=3))
    ax.add_patch(Rectangle((x - 1.3 * s, y), 0.9 * s, 0.5 * s, fc=WOOD, ec=WOOD_DARK, lw=0.7, zorder=4))
    for k in range(3):
        ax.plot([x - 1.25 * s, x - 0.45 * s], [y + (0.14 + 0.13 * k) * s] * 2, color=WOOD_DARK, lw=0.4, alpha=0.6, zorder=5)
    ax.plot([x - 0.4 * s, x + 0.55 * s], [y + 0.25 * s] * 2, color="0.2", lw=0.6, zorder=4)
    ax.add_patch(FancyBboxPatch((x + 0.55 * s, y + 0.1 * s), 0.7 * s, 0.32 * s, boxstyle="round,pad=0.0,rounding_size=0.06",
                                fc="#f2c14e", ec="black", lw=0.6, zorder=5))
    ax.add_patch(Rectangle((x + 0.65 * s, y + 0.18 * s), 0.3 * s, 0.16 * s, fc="#cdeccf", ec="black", lw=0.3, zorder=6))
    ax.add_patch(Ellipse((x + 1.42 * s, y + 0.27 * s), 0.38 * s, 0.28 * s, fc=SKIN, ec="black", lw=0.4, zorder=6))


def trolley(ax, x, y, w=1.0, color="#cfdcf3", label=None, s=1.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y + 0.14 * s), w, 0.32 * s, boxstyle="round,pad=0.0,rounding_size=0.04",
                                fc=color, ec="black", lw=0.6, zorder=4))
    for dx in (-0.3 * w, 0.3 * w):
        ax.add_patch(Circle((x + dx, y + 0.08 * s), 0.08 * s, fc="#333333", ec="black", lw=0.4, zorder=5))
        ax.add_patch(Circle((x + dx, y + 0.08 * s), 0.03 * s, fc="#bbbbbb", ec="none", zorder=6))
    if label:
        ax.text(x, y + 0.3 * s, label, ha="center", va="center", fontsize=6, zorder=7)


def motion_sensor(ax, x, y, s=1.0, facing=1):
    ax.add_patch(Rectangle((x - 0.12 * s, y), 0.24 * s, 0.4 * s, fc="#4a4a4a", ec="black", lw=0.5, zorder=4))
    ax.add_patch(Circle((x + 0.12 * s * facing, y + 0.2 * s), 0.1 * s, fc="#999999", ec="black", lw=0.4, zorder=5))


def football(ax, x, y, r):
    ax.add_patch(Circle((x, y), r, fc="white", ec="black", lw=0.6, zorder=6))
    ang = np.radians(90 + np.arange(5) * 72)
    ax.add_patch(Polygon(np.c_[x + 0.42 * r * np.cos(ang), y + 0.42 * r * np.sin(ang)], closed=True, fc="#222222", zorder=7))
    for a in ang:
        cx, cy = x + 0.92 * r * np.cos(a + np.radians(36)), y + 0.92 * r * np.sin(a + np.radians(36))
        ax.add_patch(Circle((cx, cy), 0.2 * r, fc="#222222", zorder=7))
        ax.plot([x + 0.42 * r * np.cos(a), x + 0.75 * r * np.cos(a)], [y + 0.42 * r * np.sin(a), y + 0.75 * r * np.sin(a)],
                color="black", lw=0.4, zorder=7)
    ax.add_patch(Circle((x, y), r, fc="none", ec="black", lw=0.6, zorder=8))


def boot(ax, x, y, s=1.0):
    pts = [(x - 0.6 * s, y + 0.9 * s), (x - 0.6 * s, y + 0.1 * s), (x - 0.45 * s, y), (x + 0.55 * s, y),
           (x + 0.7 * s, y + 0.12 * s), (x + 0.55 * s, y + 0.28 * s), (x - 0.05 * s, y + 0.42 * s), (x - 0.15 * s, y + 0.9 * s)]
    ax.add_patch(Polygon(pts, closed=True, fc="#1f1f1f", ec="black", lw=0.5, zorder=6))
    ax.plot([x - 0.3 * s, x + 0.3 * s], [y + 0.38 * s, y + 0.3 * s], color="white", lw=0.8, zorder=7)
    for dx in (-0.3, 0.0, 0.3):
        ax.plot([x + dx * s, x + dx * s], [y, y - 0.08 * s], color="#555555", lw=1.0, zorder=5)


def head(ax, x, y, s=1.0):
    ax.add_patch(Ellipse((x, y), 0.8 * s, 1.0 * s, fc=SKIN, ec="black", lw=0.5, zorder=6))
    ax.add_patch(Wedge((x, y + 0.05 * s), 0.42 * s, 20, 200, fc="#5b3a1e", ec="none", zorder=7))
    ax.add_patch(Circle((x + 0.22 * s, y + 0.1 * s), 0.05 * s, fc="black", zorder=8))
    ax.add_patch(Rectangle((x - 0.18 * s, y - 0.75 * s), 0.36 * s, 0.35 * s, fc=SKIN, ec="black", lw=0.4, zorder=5))


def airbag(ax, x, y, s=1.0):
    ax.add_patch(Ellipse((x, y), 0.9 * s, 1.3 * s, fc="#f4f4f4", ec="0.4", lw=0.6, zorder=5))
    for k in range(3):
        ax.add_patch(Arc((x, y), (0.5 + 0.12 * k) * s, (0.8 + 0.15 * k) * s, theta1=100, theta2=260, color="0.7", lw=0.4, zorder=6))


def measuring_cylinder(ax, x, y, w=1.0, h=4.0, fill=0.88, liquid="#e9d58a"):
    """A glass measuring cylinder of viscous liquid with graduations; (x, y) is the base centre."""
    ax.add_patch(Rectangle((x - 0.75 * w, y - 0.12 * w), 1.5 * w, 0.12 * w, fc="#cfd8dc", ec="black", lw=0.5, zorder=3))
    ax.add_patch(Rectangle((x - w / 2, y), w, h * fill, fc=liquid, ec="none", alpha=0.9, zorder=3))
    ax.add_patch(Rectangle((x - w / 2, y), w, h, fc=GLASS, ec="black", lw=0.7, alpha=0.35, zorder=4))
    ax.plot([x - w / 2, x - w / 2], [y, y + h], color="black", lw=0.7, zorder=5)
    ax.plot([x + w / 2, x + w / 2], [y, y + h], color="black", lw=0.7, zorder=5)
    for k in range(1, 16):
        yy = y + k * h / 16
        L = 0.25 if k % 4 == 0 else 0.12
        ax.plot([x - w / 2, x - w / 2 + L * w], [yy, yy], color="black", lw=0.4, zorder=5)
    ax.add_patch(Rectangle((x + w * 0.38, y + 0.05 * h), 0.08 * w, h * fill * 0.9, fc="white", alpha=0.35, ec="none", zorder=6))
