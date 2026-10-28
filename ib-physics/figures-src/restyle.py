"""Restyle the unpacked guide so it looks like the reference LaTeX textbook
chapters, swap in the redrawn figures and add the new realistic ones.

usage: restyle.py <unpacked dir> <figure dir>
"""
import copy
import json
import re
import sys
from PIL import Image
from lxml import etree

UN, FIG = sys.argv[1], sys.argv[2]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "r": R, "wp": WP, "a": A}
FONT = "CMU Serif"
EMU = 914400


def w(tag):
    return f"{{{W}}}{tag}"


def el(tag, **attrs):
    e = etree.Element(w(tag))
    for k, v in attrs.items():
        e.set(w(k), str(v))
    return e


def child(parent, tag, first=False, **attrs):
    e = parent.find(w(tag))
    if e is None:
        e = el(tag, **attrs)
        if first:
            parent.insert(0, e)
        else:
            parent.append(e)
    else:
        for k, v in attrs.items():
            e.set(w(k), str(v))
    return e


# schema order of pPr / rPr children (subset that occurs here)
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "numPr", "pBdr", "shd", "tabs",
             "spacing", "ind", "jc", "outlineLvl", "rPr"]
RPR_ORDER = ["rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "color", "spacing",
             "sz", "szCs", "u", "vertAlign"]


def reorder(e, order):
    kids = list(e)
    kids.sort(key=lambda k: order.index(etree.QName(k).localname) if etree.QName(k).localname in order else 99)
    for k in kids:
        e.remove(k)
    for k in kids:
        e.append(k)


def ppr(p):
    pp = p.find(w("pPr"))
    if pp is None:
        pp = el("pPr")
        p.insert(0, pp)
    return pp


def set_ppr(p, tag, **attrs):
    pp = ppr(p)
    e = child(pp, tag, **attrs)
    reorder(pp, PPR_ORDER)
    return e


def drop(parent, tag):
    for e in parent.findall(w(tag)):
        parent.remove(e)


def text_of(e):
    return "".join(t.text or "" for t in e.iter(w("t")))


def runs(p):
    return [r for r in p.iter(w("r"))]


def rpr(r):
    rp = r.find(w("rPr"))
    if rp is None:
        rp = el("rPr")
        r.insert(0, rp)
    return rp


def set_rpr(r, tag, **attrs):
    rp = rpr(r)
    e = child(rp, tag, **attrs)
    reorder(rp, RPR_ORDER)
    return e


def set_size(r, half_points):
    set_rpr(r, "sz", val=half_points)
    set_rpr(r, "szCs", val=half_points)


def in_table(e):
    return any(etree.QName(a).localname == "tc" for a in e.iterancestors())


# ---------------------------------------------------------------- load
doc_path = f"{UN}/word/document.xml"
tree = etree.parse(doc_path)
root = tree.getroot()
body = root.find(w("body"))
rels_path = f"{UN}/word/_rels/document.xml.rels"
rels = etree.parse(rels_path)
rel_targets = {r.get("Id"): r.get("Target") for r in rels.getroot()}
figinfo = json.load(open(f"{FIG}/figs.json"))
widths = figinfo["widths"]
info = figinfo["info"]

# ---------------------------------------------------------------- figures
ORDER = ["f_concept", "f_walk", "f_chord", "f_motiondiag", "f_threegraphs", "f_suvatarea", "f_throwup",
         "f_components", "f_dropthrow", "f_projvectors", "f_angles", "f_cliffgeneral", "f_forces",
         "f_terminal", "f_dragproj", "f_ggraph", "f_boat", "f_ex3", "f_ex5", "f_ex6", "f_ex8", "f_ex9",
         "f_ex13", "f_ex15", "f_ex16"]


def set_extent(drawing, name):
    im = Image.open(f"{FIG}/{name}.png")
    wpx, hpx = im.size
    cx = int(widths[name] * EMU)
    cy = int(cx * hpx / wpx)
    for e in drawing.iter(f"{{{WP}}}extent", f"{{{A}}}ext"):
        e.set("cx", str(cx))
        e.set("cy", str(cy))


drawings = list(body.iter(w("drawing")))
assert len(drawings) == len(ORDER), len(drawings)
for d, name in zip(drawings, ORDER):
    rid = d.find(".//a:blip", NS).get(f"{{{R}}}embed")
    target = rel_targets[rid]
    with open(f"{FIG}/{name}.png", "rb") as src, open(f"{UN}/word/{target}", "wb") as dst:
        dst.write(src.read())
    set_extent(d, name)

# ------------------------------------------- renumber chapter-1 figures (3 new ones)
def new_num(n):
    if n <= 5:
        return n
    if n <= 7:
        return n + 1
    if n <= 14:
        return n + 2
    return n + 3


def renum(s):
    return re.sub(r"(Figures? )1\.(\d+)", lambda m: f"{m.group(1)}1.{new_num(int(m.group(2)))}", s)


for t in body.iter(w("t")):
    if t.text and "Figure" in t.text:
        t.text = renum(t.text)
for dp in body.iter(f"{{{WP}}}docPr"):
    dp.set("descr", renum(dp.get("descr", "")))


def caption_para(num):
    for p in body.iter(w("p")):
        rs = runs(p)
        if rs and text_of(rs[0]).strip() == f"Figure {num}:":
            return p
    raise KeyError(num)


NEW = [
    ("1.5", "f_realcar", "1.6",
     " A real car pulling away from one set of traffic lights, cruising and braking at the next (computer model, "
     "with simulated GPS readings every 0.5 s). A real acceleration cannot jump from one value to another, so the "
     "real v–t graph has no sharp corners, and each gear change shows up as a brief dip in a. The straight-line "
     f"model used in exam questions has the same top speed and the same area under it (about {info['realcar']['s_real']:.0f} m)."),
    ("1.8", "f_sensortoss", "1.9",
     " Simulated motion-sensor readings (every 0.05 s) for a ball tossed upward and caught. The ball is in free "
     "fall only between release and catch: that part of the v–t graph is a straight line with gradient "
     f"{info['sensortoss']['gradient']:.2f} m s⁻², very close to −g. While the hand is pushing or catching, it is not free fall."),
    ("1.16", "f_realfalls", "1.17",
     " Computed speed–time graphs for three balls dropped from rest in air, compared with free fall (no air). "
     "The light table-tennis ball reaches its low terminal speed in about a second; the small, dense steel ball "
     "is still close to free fall after several seconds."),
]

next_docpr = max(int(dp.get("id")) for dp in body.iter(f"{{{WP}}}docPr")) + 100
rid_n = max(int(r.get("Id")[3:]) for r in rels.getroot()) + 1
for after_num, name, num, text in NEW:
    cap = caption_para(after_num)
    pic_p = cap.getprevious()
    new_pic = copy.deepcopy(pic_p)
    new_cap = copy.deepcopy(cap)
    rid = f"rId{rid_n}"
    rid_n += 1
    etree.SubElement(rels.getroot(), "Relationship", Id=rid,
                     Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                     Target=f"media/{name}.png")
    with open(f"{FIG}/{name}.png", "rb") as src, open(f"{UN}/word/media/{name}.png", "wb") as dst:
        dst.write(src.read())
    d = new_pic.find(".//" + w("drawing"))
    d.find(".//a:blip", NS).set(f"{{{R}}}embed", rid)
    dp = d.find(f".//{{{WP}}}docPr")
    dp.set("id", str(next_docpr))
    next_docpr += 1
    dp.set("name", name)
    dp.set("title", name)
    dp.set("descr", f"**Figure {num}:**{text}")
    set_extent(d, name)
    rs = runs(new_cap)
    rs[0].find(w("t")).text = f"Figure {num}:"
    rs[1].find(w("t")).text = text
    for extra in rs[2:]:
        extra.getparent().remove(extra)
    cap.addnext(new_pic)
    new_pic.addnext(new_cap)

# ---------------------------------------------------------------- restyle
NAVY = "1F2F7A"

# 1. callout boxes and data tables
for tbl in body.iter(w("tbl")):
    tp = tbl.find(w("tblPr"))
    ncol = len(tbl.find(w("tblGrid")))
    first = text_of(tbl.find(".//" + w("tc")))
    borders = tp.find(w("tblBorders"))
    if borders is not None:
        tp.remove(borders)
    borders = el("tblBorders")
    if ncol == 1:  # callout: thin framed box, like \fbox
        spec = {s: ("single", 6) for s in ("top", "left", "bottom", "right")}
        spec.update(insideH=("none", 0), insideV=("none", 0))
    elif first.strip() == "Section":  # contents: borderless, like a LaTeX table of contents
        spec = {s: ("none", 0) for s in ("top", "left", "bottom", "right", "insideH", "insideV")}
    else:  # data table: double outer rules, single inner rules
        spec = {s: ("double", 4) for s in ("top", "left", "bottom", "right")}
        spec.update(insideH=("single", 4), insideV=("single", 4))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        val, sz = spec[side]
        borders.append(el(side, val=val, sz=sz, space=0, color="000000" if val != "none" else "auto"))
    # tblBorders goes after tblW / jc
    idx = 0
    for i, k in enumerate(tp):
        if etree.QName(k).localname in ("tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
                                        "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd"):
            idx = i + 1
    tp.insert(idx, borders)
    for tc in tbl.iter(w("tc")):
        tcp = tc.find(w("tcPr"))
        if tcp is not None:
            drop(tcp, "tcBorders")
            drop(tcp, "shd")
    if first.strip() == "Section":
        hdr = tbl.find(w("tr"))
        for tc in hdr.findall(w("tc")):
            tcp = tc.find(w("tcPr"))
            b = el("tcBorders")
            b.append(el("bottom", val="single", sz=6, space=0, color="000000"))
            tcp.insert(1, b)
        for tr in tbl.findall(w("tr"))[1:]:
            if text_of(tr).startswith("Chapter"):
                for tc in tr.findall(w("tc"))[1:2]:
                    for r in tc.iter(w("r")):
                        set_rpr(r, "b")
                        set_rpr(r, "bCs")
                tcs = tr.findall(w("tc"))
                for tc in tcs:
                    tcp = tc.find(w("tcPr"))
                    mar = tcp.find(w("tcMar"))
                    if mar is not None:
                        child(mar, "top", type="dxa", w=140)

# 2. paragraphs
def is_caption(p):
    rs = runs(p)
    return bool(rs) and re.fullmatch(r"Figure \d\.\d+:", text_of(rs[0]).strip() or "") is not None


def is_equation(p):
    pp = p.find(w("pPr"))
    return pp is not None and pp.find(w("tabs")) is not None


def is_plain_body(p):
    if in_table(p) or p.find(".//" + w("drawing")) is not None:
        return False
    pp = p.find(w("pPr"))
    if pp is None:
        return bool(text_of(p).strip())
    if pp.find(w("pStyle")) is not None or pp.find(w("tabs")) is not None or pp.find(w("pBdr")) is not None:
        return False
    if pp.find(w("ind")) is not None:
        return False
    jc = pp.find(w("jc"))
    if jc is not None and jc.get(w("val")) not in ("left", "both"):
        return False
    if is_caption(p):
        return False
    return bool(text_of(p).strip())


paras = list(body.iter(w("p")))

# title block (first three paragraphs)
p_kicker, p_title, p_sub = paras[0], paras[1], paras[2]
set_ppr(p_kicker, "spacing", before=200, after=60)
for r in runs(p_kicker):
    rp = rpr(r)
    drop(rp, "b")
    drop(rp, "bCs")
    set_size(r, 22)
    set_rpr(r, "spacing", val=10)
for r in runs(p_title):
    set_size(r, 58)
for r in runs(p_sub):
    set_size(r, 24)
pb = ppr(p_sub).find(w("pBdr"))
drop(pb, "bottom")
pb.append(el("bottom", val="double", sz=6, space=10, color="000000"))

for p in paras:
    pp = p.find(w("pPr"))
    style = pp.find(w("pStyle")).get(w("val")) if pp is not None and pp.find(w("pStyle")) is not None else None
    txt = text_of(p)

    if style == "Heading1":
        drop(pp, "pBdr")
        m = re.match(r"\s*Chapter (\d)\s*·\s*(.+)", txt)
        rs = runs(p)
        base = rs[0]
        for r in rs:
            r.getparent().remove(r)
        if m:
            # LaTeX chapter opening: "Chapter N" on one line, the title below it
            set_ppr(p, "spacing", before=1700, after=560, line=240, lineRule="auto")
            r1 = copy.deepcopy(base)
            r1.find(w("t")).text = f"Chapter {m.group(1)}"
            set_size(r1, 42)
            br = el("r")
            br.append(el("br"))
            r2 = copy.deepcopy(base)
            t2 = r2.find(w("t"))
            t2.text = m.group(2)
            set_size(r2, 50)
            # small gap between the two lines
            r_gap = el("r")
            r_gap.append(el("br"))
            gap_rpr = el("rPr")
            gap_rpr.append(el("sz", val=24))
            r_gap.insert(0, gap_rpr)
            for r in (r1, br, r_gap, r2):
                p.append(r)
        else:
            set_ppr(p, "spacing", before=1700, after=560)
            set_size(base, 50)
            p.append(base)
        continue

    if style == "Heading2":
        set_ppr(p, "spacing", before=380, after=160)
        for r in runs(p):
            set_size(r, 29)
            t = r.find(w("t"))
            if t is not None and t.text:
                t.text = re.sub(r"^(\d+\.\d+)\s+", "\\1\u2003", t.text)
        continue

    if style == "Heading3":
        set_ppr(p, "spacing", before=260, after=100)
        for r in runs(p):
            set_size(r, 24)
        continue

    if pp is not None and pp.find(w("shd")) is not None:
        bdr = pp.find(w("pBdr"))
        left = bdr.find(w("left")) if bdr is not None else None
        drop(pp, "shd")
        drop(pp, "pBdr")
        drop(pp, "ind")
        if txt.startswith("EXAMPLE"):
            # worked example: bold statement under a thin navy rule, as in the textbook
            b = el("pBdr")
            b.append(el("top", val="single", sz=6, space=10, color=NAVY))
            pp.insert(PPR_ORDER.index("pBdr"), b)
            reorder(pp, PPR_ORDER)
            set_ppr(p, "spacing", before=320, after=160, line=264, lineRule="auto")
            set_ppr(p, "jc", val="both")
        else:  # answer line
            set_ppr(p, "spacing", before=100, after=240, line=264, lineRule="auto")
        continue

    if is_caption(p):
        rs = runs(p)
        for i, r in enumerate(rs):
            rp = rpr(r)
            if i == 0:
                drop(rp, "b")
                drop(rp, "bCs")
                set_size(r, 21)
            else:
                set_size(r, 18)
        long = len(txt) > 115
        set_ppr(p, "jc", val="both" if long else "center")
        set_ppr(p, "spacing", before=40, after=260, line=240, lineRule="auto")
        continue

    if is_equation(p):
        for r in runs(p):
            t = text_of(r)
            if re.fullmatch(r"\s*\(\d\.\d+\)", t):
                set_size(r, 22)
            else:
                set_size(r, 23)

# body text: justified, indented continuation paragraphs (no gap between them)
prev = None
for p in body:
    if etree.QName(p).localname != "p":
        prev = None
        continue
    if is_plain_body(p) and p not in (p_kicker, p_title, p_sub):
        set_ppr(p, "jc", val="both")
        if prev is not None:
            sp = ppr(prev).find(w("spacing"))
            if sp is not None:
                sp.set(w("after"), "30")
            set_ppr(p, "ind", firstLine=340)
            sp2 = set_ppr(p, "spacing")
            sp2.set(w("before"), "0")
        prev = p
    else:
        prev = None

# answer / label runs: black text everywhere, no coloured backgrounds
for c in body.iter(w("color")):
    c.set(w("val"), "000000")
for s in list(body.iter(w("shd"))):
    s.getparent().remove(s)

# 3. characters that CMU Serif lacks
SUP = {"⁻": "−", "¹": "1", "²": "2", "³": "3", "ⁿ": "n", "⁰": "0", "⁴": "4"}
SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4"}
MATH = set("≈≠∝")
SYM = set("☐✓")


def classify(ch):
    if ch in SUP:
        return "sup"
    if ch in SUB:
        return "sub"
    if ch in MATH:
        return "math"
    if ch in SYM:
        return "sym"
    return None


def split_run(r):
    t = r.find(w("t"))
    if t is None or not t.text or not any(classify(c) for c in t.text):
        return
    if r.find(w("rPr")) is not None and r.find(w("rPr")).find(w("vertAlign")) is not None:
        # already super/subscript: just map to plain characters
        t.text = "".join(SUP.get(c, SUB.get(c, c)) for c in t.text)
        return
    segs = []
    for ch in t.text:
        k = classify(ch)
        if segs and segs[-1][0] == k:
            segs[-1][1].append(ch)
        else:
            segs.append((k, [ch]))
    parent = r.getparent()
    pos = parent.index(r)
    for kind, chars in segs:
        nr = copy.deepcopy(r)
        nt = nr.find(w("t"))
        s = "".join(chars)
        if kind == "sup":
            nt.text = "".join(SUP[c] for c in s)
            set_rpr(nr, "vertAlign", val="superscript")
        elif kind == "sub":
            nt.text = "".join(SUB[c] for c in s)
            set_rpr(nr, "vertAlign", val="subscript")
        else:
            nt.text = s
            if kind == "math":
                set_rpr(nr, "rFonts", ascii="Cambria Math", hAnsi="Cambria Math", cs="Cambria Math", eastAsia="Cambria Math")
            elif kind == "sym":
                set_rpr(nr, "rFonts", ascii="Segoe UI Symbol", hAnsi="Segoe UI Symbol", cs="Segoe UI Symbol",
                        eastAsia="Segoe UI Symbol")
        nt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        parent.insert(pos, nr)
        pos += 1
    parent.remove(r)


for r in list(body.iter(w("r"))):
    split_run(r)

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)
print("done")
