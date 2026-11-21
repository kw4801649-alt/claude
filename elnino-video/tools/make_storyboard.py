#!/usr/bin/env python3
"""
tools/make_storyboard.py -- Write docs/02_storyboard.md for "The Pacific, seen in heat".

Each storyboard beat is anchored to a phrase of the narration, exactly like the cue()
function in scene/index.html, so the timecodes here are the real ones of the current
audio (audio/timings.json). Re-run after tools/tts.py.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TL = json.loads((ROOT / "audio" / "timings.json").read_text("utf-8"))


def cue(sid: str, phrase: str, nth: int = 1) -> float:
    sc, p, count = TL["scenes"][sid], phrase.lower(), 0
    for seg in sc["segments"]:
        for s in seg["sentences"]:
            txt, start = s["text"].lower(), 0
            while (idx := txt.find(p, start)) >= 0:
                count += 1
                if count == nth:
                    return sc["start"] + s["start"] + idx / len(txt) * (s["end"] - s["start"])
                start = idx + 1
    raise SystemExit(f"cue not found: {sid} {phrase!r}")


def tc(x: float) -> str:
    return f"{int(x // 60)}:{x % 60:04.1f}"


# (scene, anchor phrase or None for scene start, visual, words in the world, camera)
ROWS = [
    ("s01", None, "Black. A single white line, the equator, draws across a dark dot-matrix world.", "—", "High overhead, looking straight down."),
    ("s01", "turns unusually warm", "The equatorial Pacific ignites: infrared dots go from cyan to amber to red across the east.", "—", "Slow drift overhead."),
    ("s01", "weather around the world", "A ring of light ripples out from the Pacific across every continent.", "—", "Overhead."),
    ("s01", "around Christmas", "Zoom toward Peru; the coast glows.", "DECEMBER (mono, typed onto the coast)", "Descend toward Peru."),
    ("s01", "named it El Niño", "Embers off the warm water condense into a word.", "El Niño (Fraunces italic, assembles from sparks); “the boy child”", "Low over Peru."),
    ("s01", "So how does", "The word bursts back into sparks; the ocean cools to normal; clouds fade.", "—", "Rise and swing to the master angle."),
    ("s02", "Indonesia", "Normal Pacific: warm red west, cool cyan-tinted east.", "INDONESIA · AUSTRALIA · SOUTH AMERICA (mono, lying on the land)", "Wide oblique from the south."),
    ("s02", "trade winds", "1,500 white light-streaks fly east to west over the ocean.", "trade winds (letters peel off and blow west, stretching)", "Push in."),
    ("s02", "warm pool", "Warm water piles up in the west; the dots there run hottest.", "warm pool (letters drop and land on the water)", "Swing west, lower."),
    ("s02", "moist air rises", "Point-cloud thunderheads grow over the warm pool, rain streaks fall.", "—", "Low, looking at the clouds."),
    ("s02", "High up", "Comets of light trace the Walker loop: up in the west, east aloft, down in the east, back west at the surface.", "Walker circulation (letters travel around the loop)", "Low side view along the equator."),
    ("s03", "beneath the surface", "The camera sinks through the surface into a slab of light: warm dots above, deep blue below.", "—", "Dive below the surface."),
    ("s03", "thermocline", "A glowing net, the thermocline, appears where the colours meet.", "thermocline (lies along the net and tilts with it)", "Side-on, under water."),
    ("s03", "about 150 meters", "The net sits deep in the west…", "−150 m (mono)", "Track west."),
    ("s03", "a few tens of meters", "…and shallow in the east.", "−40 m (mono)", "Track east."),
    ("s03", "Cold water rises", "Cyan spirals rise from below the net off Peru.", "upwelling (letters rise out of the deep); fisheries", "Close on the east."),
    ("s03", "cold tongue", "Back above: a cyan stripe along the equator.", "cold tongue (stretched along the stripe, lying flat)", "Rise to a high oblique."),
    ("s04", "Bjerknes feedback", "A ring of light circles the Pacific; a comet runs round it, reaching each station as it is named. Winds lengthen, upwelling brightens, L over the warm west, H over the cold east.", "Bjerknes feedback; strong winds · upwelling · cold east · warm west · air pressure; L / H", "High, slowly orbiting."),
    ("s04", "the loop goes around again", "The comet whips round twice, then stalls and twitches backwards.", "—", "High."),
    ("s05", "The trade winds weaken", "The white streaks thin and slow.", "—", "Oblique over the west."),
    ("s05", "bursts of westerly wind", "Gold streaks burst eastward in the west Pacific.", "westerly burst (blows east)", "Low over the west."),
    ("s05", "sloshes east", "A bulge pushes the thermocline net down and travels east along the equator.", "Kelvin wave (rides the bulge); ~2 MONTHS", "Under water, tracking with the wave west → east."),
    ("s05", "the tilt flattens", "The net flattens; upwelling spirals turn orange; the east surface warms.", "flattens (squashes on the net); warm water rising", "Close on the east, then rise."),
    ("s06", "runs in reverse", "The ring returns, comet running the other way.", "warmer east · smaller gap · weaker winds · more warm water east", "High orbit."),
    ("s06", "Warm water now covers", "The whole basin glows orange-red.", "—", "High oblique."),
    ("s06", "The rising air", "Western clouds shrink, central-Pacific towers grow; the Walker loop slides east and dims.", "rain follows the heat (mono)", "Low side view."),
    ("s06", "jet stream", "The camera rises to show the world; a river of light, the jet stream, crosses the North Pacific and sags south; storm swirls ride it into the southern US.", "jet stream (letters ride the river); NOV · DEC · JAN", "Rise high over the North Pacific."),
    ("s07", "teleconnections", "Arcs of light shoot from the warm Pacific to distant regions.", "teleconnections", "High over the whole world."),
    ("s07", "drought to Indonesia", "Regions light up in their impact colours, each with a ring pulse.", "drought ×3 (cracks and crumbles); weaker monsoon", "Glide to Asia, then Africa."),
    ("s07", "Peru and Ecuador", "Cyan for wet, coral for mild.", "floods / wetter (letters drip); milder (floats up)", "Glide to the Americas."),
    ("s07", "Atlantic hurricanes", "A spiral of letters unwinds over the Atlantic; another spins up in the East Pacific.", "hurricanes (unwinds); more storms (spins up)", "Over the Americas."),
    ("s07", "global average temperature", "Every land dot warms slightly.", "+0.1 – 0.2 °C; tendencies; not guarantees (flickers)", "Pull back over the world."),
    ("s08", "Rossby waves", "Two bulges either side of the equator travel west…", "Rossby waves (ride the sea surface)", "Down to the basin."),
    ("s08", "bounce off", "…bounce off the west and run back east, lifting the net.", "bounce (rides the reflected wave)", "Under water, tracking east."),
    ("s08", "drains heat", "Warm dots stream away from the equator.", "heat drains poleward (mono)", "High over the basin."),
    ("s08", "La Niña", "Stronger streaks, a deep-cyan tongue reaching far west, bigger western clouds.", "La Niña (freezes into place)", "Oblique from the east."),
    ("s09", "form ENSO", "A line of light, the Pacific's heartbeat, draws across the sky: red peaks for El Niño, blue troughs for La Niña. The ocean below follows the cursor.", "ENSO; EL NIÑO – SOUTHERN OSCILLATION", "Ride along the line."),
    ("s09", "see-saw", "L and H rock up and down at opposite ends of the Pacific.", "L / H (see-saw)", "Along the line."),
    ("s09", "corals show", "Ghost copies of the line stretch back into the distance.", "THOUSANDS OF YEARS", "Pull far back."),
    ("s09", "every 2 to 7 years", "The line keeps drawing.", "2 – 7 YEARS; 9 – 12 MONTHS", "Back along the line."),
    ("s09", "Climate change", "The world returns; impact regions flash brighter on a warmer world.", "climate change; doesn't create it · can make impacts hit harder", "High over the world."),
    ("s09", "How ENSO itself", "The world dims.", "still being researched (flickers)", "Settle toward the Pacific."),
    ("s10", "the trade winds weaken", "Recap at speed: streaks thin, warm water rushes east, clouds follow, a ripple crosses the world.", "—", "Master angle, then high."),
    ("s10", "Next time", "The equator line redraws; the ocean glows.", "El Niño (embers, lying on the ocean); HOW EL NIÑO FORMS", "Back overhead; fade to black."),
]

lines = ["# How El Niño Forms — Storyboard: “The Pacific, seen in heat”", "",
         "_Generated by `tools/make_storyboard.py` from the measured narration (`audio/timings.json`). "
         "Every beat is triggered by the moment its anchor phrase is spoken; `scene/index.html` uses the same phrases._", "",
         "**Look:** one continuous camera move, no cuts and no interface chrome (no title bars, chips, cards or pills). "
         "A dark infrared dot-matrix world: sea-surface temperature is colour "
         "(indigo → blue → cyan → white-hot → amber → orange → red), winds and currents are streaks of light, "
         "clouds are point volumes, the thermocline is a glowing net. Key words live inside the physics "
         "(Fraunces italic for ideas, JetBrains Mono for numbers and places). 16:9, 1920×1080.", "",
         "| # | Time | Anchor (spoken) | Visual | Words in the world | Camera |", "|---|---|---|---|---|---|"]
for i, (sid, phrase, vis, words, cam) in enumerate(ROWS, 1):
    t = TL["scenes"][sid]["start"] if phrase is None else cue(sid, phrase)
    lines.append(f"| {i} | {tc(t)} | {('“' + phrase + '”') if phrase else sid + ' start'} | {vis} | {words} | {cam} |")
lines += ["", f"**End of picture: {tc(TL['total'])} ({TL['total']:.2f} s).**", ""]
(ROOT / "docs" / "02_storyboard.md").write_text("\n".join(lines), "utf-8")
print("Wrote docs/02_storyboard.md")
