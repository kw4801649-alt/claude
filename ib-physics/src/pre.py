"""Stage 1 (on the original unpacked guide):
- remove Chapter 2 (Worked Examples) and Chapter 3 (Quick Reference) and anything pointing at them;
- rename Chapter 1 to "Kinematics", update the front matter and the contents for the new Chapter 2;
- typeset every Chapter 1 equation as Office Math (stacked fractions, roots, etc.).
usage: pre.py <unpacked dir> <ch2 markup>
"""
import copy
import os
import re
import sys
from lxml import etree

from eqlib import W, w, el, latex_to_omml, equation_table, replace_inline

UN, CH2 = sys.argv[1], sys.argv[2]
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"

doc_path = f"{UN}/word/document.xml"
tree = etree.parse(doc_path)
body = tree.getroot().find(w("body"))


def text_of(e):
    return "".join(t.text or "" for t in e.iter(w("t")))


def set_cell(tc, text):
    """Replace a cell's text, keeping the formatting of its first run."""
    ps = tc.findall(w("p"))
    for extra in ps[1:]:
        tc.remove(extra)
    p = ps[0]
    runs = p.findall(w("r"))
    for r in runs[1:]:
        p.remove(r)
    runs[0].find(w("t")).text = text


# ------------------------------------------------------------ 1. cut chapters 2 and 3
kids = list(body)
start = next(i for i, e in enumerate(kids)
             if e.find(f"{w('pPr')}/{w('pStyle')}") is not None
             and e.find(f"{w('pPr')}/{w('pStyle')}").get(w("val")) == "Heading1"
             and "Worked Examples" in text_of(e))
removed_rids = set()
for e in kids[start:]:
    if etree.QName(e).localname == "sectPr":
        continue
    for blip in e.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
        removed_rids.add(blip.get(f"{{{R}}}embed"))
    body.remove(e)

rels_path = f"{UN}/word/_rels/document.xml.rels"
rels = etree.parse(rels_path)
for rel in list(rels.getroot()):
    if rel.get("Id") in removed_rids:
        target = os.path.join(UN, "word", rel.get("Target"))
        if os.path.exists(target):
            os.remove(target)
        rels.getroot().remove(rel)
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)

# the g-measurement caption pointed at a worked example
for t in body.iter(w("t")):
    if t.text and " The data are used in Example 21." in t.text:
        t.text = t.text.replace(" The data are used in Example 21.", "")
for dp in body.iter(f"{{{WP}}}docPr"):
    dp.set("descr", dp.get("descr", "").replace(" The data are used in Example 21.", ""))

# ------------------------------------------------------------ 2. front matter
paras = list(body.iter(w("p")))
p_title, p_sub = paras[1], paras[2]
r = p_title.find(w("r"))
r.find(w("t")).text = "A.1 Kinematics"
r2 = copy.deepcopy(r)
r2.find(w("t")).text = "A.2 Forces and Momentum"
br = el("r")
br.append(el("br"))
r.addnext(br)
br.addnext(r2)
p_sub.find(w("r")).find(w("t")).text = "The important stuff. Every idea explained from the ground up."

ch2_sections = [l[3:].strip() for l in open(CH2, encoding="utf8") if l.startswith("## ")]

tables = list(body.iter(w("tbl")))
for tbl in tables:
    first = text_of(tbl.find(".//" + w("tc"))).strip()
    rows = tbl.findall(w("tr"))
    if first == "Chapter":  # "How this guide is organised"
        set_cell(rows[1].findall(w("tc"))[0], "1. Kinematics (A.1)")
        set_cell(rows[1].findall(w("tc"))[1], "Motion described without asking why: displacement, velocity, acceleration, "
                 "motion graphs, SUVAT, free fall, projectiles and fluid resistance.")
        set_cell(rows[2].findall(w("tc"))[0], "2. Forces and Momentum (A.2)")
        set_cell(rows[2].findall(w("tc"))[1], "Why things move: Newton’s three laws, free-body diagrams, the forces you need "
                 "to know, momentum and impulse, collisions and circular motion.")
        set_cell(rows[2].findall(w("tc"))[2], "Read after Chapter 1: it uses the kinematics equations throughout.")
        tbl.remove(rows[3])
    elif first == "Section":  # contents
        chap_row = next(r for r in rows if text_of(r).startswith("Chapter 1"))
        sec_row = next(r for r in rows if text_of(r).startswith("1.1"))
        cut = next(i for i, r in enumerate(rows) if text_of(r).startswith("Chapter 2"))
        for r_ in rows[cut:]:
            tbl.remove(r_)
        set_cell(chap_row.findall(w("tc"))[1], "Kinematics")
        new = copy.deepcopy(chap_row)
        set_cell(new.findall(w("tc"))[0], "Chapter 2")
        set_cell(new.findall(w("tc"))[1], "Forces and Momentum")
        tbl.append(new)
        for sec in ch2_sections:
            num, title = sec.split(" ", 1)
            row = copy.deepcopy(sec_row)
            set_cell(row.findall(w("tc"))[0], num)
            set_cell(row.findall(w("tc"))[1], re.sub(r"\$([^$]*)\$", r"\1", title))
            tbl.append(row)
        # drop the "Examples" column
        grid = tbl.find(w("tblGrid"))
        cols = grid.findall(w("gridCol"))
        total = sum(int(c.get(w("w"))) for c in cols)
        grid.remove(cols[2])
        cols[1].set(w("w"), str(total - int(cols[0].get(w("w")))))
        for r_ in tbl.findall(w("tr")):
            tcs = r_.findall(w("tc"))
            r_.remove(tcs[2])
            tcs[1].find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), cols[1].get(w("w")))

for p in body.iter(w("p")):
    t = text_of(p)
    if t.strip() == "The six-step method used in every worked example":
        p.findall(w("r"))[0].find(w("t")).text = "The six-step method for any problem"
        for r_ in p.findall(w("r"))[1:]:
            p.remove(r_)
    if p.find(f"{w('pPr')}/{w('pStyle')}") is not None and "The Important Stuff" in t and t.startswith("Chapter 1"):
        for t_ in p.iter(w("t")):
            if t_.text and "The Important Stuff" in t_.text:
                t_.text = t_.text.replace("The Important Stuff", "Kinematics")

# ------------------------------------------------------------ 3. equations
DISPLAY = {
    "1.1": r"\Delta s=s_{\text{final}}-s_{\text{initial}}",
    "1.2": r"\text{average speed}=\frac{\text{total distance}}{\text{total time}}",
    "1.3": r"\text{average velocity}\quad\bar{v}=\frac{\Delta s}{\Delta t}=\frac{s_{2}-s_{1}}{t_{2}-t_{1}}",
    "1.4": r"v=\frac{\mathrm{d}s}{\mathrm{d}t}\qquad(\text{the gradient of the tangent to the }s\text{–}t\text{ graph})",
    "1.5": r"a=\frac{\Delta v}{\Delta t}=\frac{v-u}{t}",
    "1.6": r"v=u+at",
    "1.7": r"s=\frac{1}{2}(u+v)t",
    "1.8": r"s=ut+\frac{1}{2}at^{2}",
    "1.9": r"v^{2}=u^{2}+2as",
    "1.10": r"a=g=9.81\ \text{m s}^{-2}\text{   directed downwards}",
    "1.11": r"v_{x}=v\cos\theta",
    "1.12": r"v_{y}=v\sin\theta",
    "1.13": r"v=\sqrt{v_{x}^{2}+v_{y}^{2}}",
    "1.14": r"\tan\theta=\frac{|v_{y}|}{|v_{x}|}",
    "1.15": r"s_{x}=u_{x}t",
    "1.16": r"v_{y}=u_{y}-gt",
    "1.17": r"s_{y}=u_{y}t-\frac{1}{2}gt^{2}",
    "1.18": r"v_{y}^{2}=u_{y}^{2}-2gs_{y}",
    "1.19": r"T=\frac{2u\sin\theta}{g}",
    "1.20": r"H=\frac{(u\sin\theta)^{2}}{2g}",
    "1.21": r"R=\frac{u^{2}\sin2\theta}{g}",
    "1.22": r"a=\frac{mg-D}{m}",
    "1.23": r"s=\frac{g}{2}\,t^{2}\qquad\text{so}\qquad g=2\times(\text{gradient of the }s\text{–}t^{2}\text{ graph})",
    "1.24": r"v_{\text{A relative to C}}=v_{\text{A relative to B}}+v_{\text{B relative to C}}",
}

HALF = r"\frac{1}{2}"
# (paragraph start, [(exact text, LaTeX), ...]) -- applied to paragraphs and table cells
INLINE = [
    ("Δs / Δt", [("Δs / Δt", r"\frac{\Delta s}{\Delta t}")]),
    ("draw tangent, then rise / run", [("rise / run", r"\frac{\text{rise}}{\text{run}}")]),
    ("WATCH OUT   Average speed is not", [("d/20 + d/30 = d/12", r"\frac{d}{20}+\frac{d}{30}=\frac{d}{12}"),
                                          ("2d ÷ (d/12)", r"2d\div\frac{d}{12}"),
                                          ("total distance ÷ total time", r"\frac{\text{total distance}}{\text{total time}}")]),
    ("WATCH OUT   SUVAT works only", [("s = ut + ½at²", "s=ut+" + HALF + "at^{2}")]),
    ("Gradient. The gradient", [("a = (v − u)/t", r"a=\frac{v-u}{t}"), ("v = u + at", r"v=u+at")]),
    ("Trapezium. The area", [("½ × (sum of parallel sides) × width = ½(u + v)t",
                              HALF + r"\times(\text{sum of parallel sides})\times\text{width}=" + HALF + "(u+v)t"),
                             ("s = ½(u + v)t", "s=" + HALF + "(u+v)t")]),
    ("Rectangle + triangle.", [("u × t", r"u\times t"),
                               ("½ × t × (v − u) = ½ × t × at = ½at²",
                                HALF + r"\times t\times(v-u)=" + HALF + r"\times t\times at=" + HALF + "at^{2}"),
                               ("s = ut + ½at²", "s=ut+" + HALF + "at^{2}")]),
    ("Eliminate t.", [("t = (v − u)/a", r"t=\frac{v-u}{a}"), ("s = ½(u + v)t", "s=" + HALF + "(u+v)t"),
                      ("s = (v² − u²)/2a", r"s=\frac{v^{2}-u^{2}}{2a}"), ("v² = u² + 2as", "v^{2}=u^{2}+2as")]),
    ("WHY IT WORKS   The middle equation", [("½(u + v)", HALF + "(u+v)")]),
    ("EXAM TIP   For “derive” questions", [("v = u + at", "v=u+at"), ("s = ½(u + v)t", "s=" + HALF + "(u+v)t")]),
    ("v = u + at", [("v = u + at", "v=u+at")]),
    ("s = ½(u + v)t", [("s = ½(u + v)t", "s=" + HALF + "(u+v)t")]),
    ("s = ut + ½at²", [("s = ut + ½at²", "s=ut+" + HALF + "at^{2}")]),
    ("v² = u² + 2as", [("v² = u² + 2as", "v^{2}=u^{2}+2as")]),
    ("tup = u / g", [("tup = u / g", r"t_{\text{up}}=\frac{u}{g}")]),
    ("H = u² / 2g", [("H = u² / 2g", r"H=\frac{u^{2}}{2g}")]),
    ("T = 2u / g", [("T = 2u / g", r"T=\frac{2u}{g}")]),
    ("t = √(2h/g),  v = √(2gh)", [("t = √(2h/g),  v = √(2gh)", r"t=\sqrt{\frac{2h}{g}},\quad v=\sqrt{2gh}")]),
    ("s = ½at² and v² = 2as with u = 0", [("s = ½at²", "s=" + HALF + "at^{2}"), ("v² = 2as", "v^{2}=2as")]),
    ("Direction of a final answer", [("tan θ = |vy| / |vx|", r"\tan\theta=\frac{|v_{y}|}{|v_{x}|}")]),
    ("sy = uy t − ½gt²", [("sy = uy t − ½gt²", r"s_{y}=u_{y}t-" + HALF + "gt^{2}")]),
    ("vy² = uy² − 2g sy", [("vy² = uy² − 2g sy", r"v_{y}^{2}=u_{y}^{2}-2gs_{y}")]),
    ("If the object lands higher", [("sy = uy t − ½gt²", r"s_{y}=u_{y}t-" + HALF + "gt^{2}")]),
    ("2u sin θ / g", [("2u sin θ / g", r"\frac{2u\sin\theta}{g}")]),
    ("A classic experiment measures g", [("s = ½gt²", "s=" + HALF + "gt^{2}")]),
    ("(steepest − shallowest) ÷ 2", [("(steepest − shallowest) ÷ 2", r"\frac{\text{steepest}-\text{shallowest}}{2}")]),
    ("(5.35 − 4.56) ÷ 2 ≈ 0.4", [("(5.35 − 4.56) ÷ 2 ≈ 0.4", r"\frac{5.35-4.56}{2}\approx0.4")]),
]

snips = list(DISPLAY.values()) + [lx for _, pairs in INLINE for _, lx in pairs]
oms = latex_to_omml(snips)
maths = dict(zip(snips, oms))

# display equations: "<tab> formula <tab> (n.n)" paragraphs -> equation tables
for p in list(body.iter(w("p"))):
    pp = p.find(w("pPr"))
    if pp is None or pp.find(w("tabs")) is None:
        continue
    m_ = re.search(r"\((\d\.\d+)\)\s*$", text_of(p))
    if not m_:
        continue
    num = m_.group(1)
    p.addprevious(equation_table(maths[DISPLAY[num]], num))
    p.getparent().remove(p)

done = set()
for p in list(body.iter(w("p"))):
    t = text_of(p)
    for key, pairs in INLINE:
        if t.startswith(key) and id(p) not in done:
            replace_inline(p, [(sub, lx) for sub, lx in pairs], maths)
            done.add(id(p))
            break
missing = [k for k, _ in INLINE if not any(text_of(p).startswith(k) for p in body.iter(w("p")))]
print("inline rewrites:", len(done), "| equation tables:",
      sum(1 for t in body.iter(w("tblCaption")) if t.get(w("val")) == "equation"))

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)
