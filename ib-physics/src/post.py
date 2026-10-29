"""Stage 3 (after restyle.py): append Chapter 2, Forces and Momentum, built from
ch2.txt. Every element is cloned from an already-restyled Chapter 1 element,
so the new chapter looks exactly like the first one.
usage: post.py <unpacked dir> <ch2 markup> <figure dir>
"""
import copy
import json
import re
import shutil
import sys
from PIL import Image
from lxml import etree

from eqlib import W, w, el, latex_to_omml, equation_table, markup_runs, inline_latex

UN, CH2, FIG = sys.argv[1], sys.argv[2], sys.argv[3]
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
EMU = 914400

doc_path = f"{UN}/word/document.xml"
tree = etree.parse(doc_path)
body = tree.getroot().find(w("body"))
sect = body.find(w("sectPr"))
widths = json.load(open(f"{FIG}/figs.json"))["widths"]


def text_of(e):
    return "".join(t.text or "" for t in e.iter(w("t")))


def style_of(p):
    s = p.find(f"{w('pPr')}/{w('pStyle')}")
    return s.get(w("val")) if s is not None else None


def plain_rpr(r):
    rp = copy.deepcopy(r.find(w("rPr"))) if r.find(w("rPr")) is not None else el("rPr")
    for tag in ("b", "bCs", "i", "iCs", "vertAlign"):
        for e in rp.findall(w(tag)):
            rp.remove(e)
    return rp


def size_of(rpr):
    sz = rpr.find(w("sz"))
    return sz.get(w("val")) if sz is not None else None


# ------------------------------------------------------------ templates from Chapter 1
paras = list(body.iter(w("p")))
T_H1 = next(p for p in paras if style_of(p) == "Heading1" and text_of(p).startswith("Chapter 1"))
T_H2 = next(p for p in paras if style_of(p) == "Heading2")
T_H3 = next(p for p in paras if style_of(p) == "Heading3" and text_of(p).startswith("What each shape"))
i_11 = list(body).index(T_H2)
T_BODY = next(e for e in list(body)[i_11 + 1:] if etree.QName(e).localname == "p" and style_of(e) is None
              and e.find(w("pPr")) is not None and e.find(f"{w('pPr')}/{w('ind')}") is None and text_of(e).strip())
T_BULLET = next(p for p in paras if style_of(p) == "ListParagraph"
                and p.find(f".//{w('numId')}").get(w("val")) == "2")
T_NUM = next(p for p in paras if style_of(p) == "ListParagraph"
             and p.find(f".//{w('numId')}").get(w("val")) == "3")
tables = list(body.iter(w("tbl")))
T_BOX = next(t for t in tables if text_of(t).startswith("IN PLAIN ENGLISH"))
T_TABLE = next(t for t in tables if text_of(t).startswith("Scalar (size only)"))
T_FIG = next(p for p in paras if p.find(".//" + w("drawing")) is not None)
T_CAP = T_FIG.getnext()

BODY_RPR = plain_rpr(next(r for r in T_BODY.findall(w("r")) if r.find(w("rPr")) is None
                          or r.find(f"{w('rPr')}/{w('b')}") is None))
BULLET_RPR = plain_rpr(T_BULLET.findall(w("r"))[-1])


def clear_runs(p):
    for k in list(p):
        if etree.QName(k).localname != "pPr":
            p.remove(k)
    return p


def para_from(template, markup, rpr, maths, math_size=None):
    p = clear_runs(copy.deepcopy(template))
    for r in markup_runs(markup, rpr, maths, math_size):
        p.append(r)
    return p


# ------------------------------------------------------------ numbering for new lists
num_path = f"{UN}/word/numbering.xml"
num_xml = open(num_path, encoding="utf8").read()
next_num = max(int(n) for n in re.findall(r'<w:num w:numId="(\d+)"', num_xml)) + 1
new_nums = []


def new_list_id():
    global next_num
    nid = next_num
    next_num += 1
    new_nums.append(f'<w:num w:numId="{nid}"><w:abstractNumId w:val="3"/><w:lvlOverride w:ilvl="0">'
                    f'<w:startOverride w:val="1"/></w:lvlOverride></w:num>')
    return nid


# ------------------------------------------------------------ parse the markup
lines = [l.rstrip("\n") for l in open(CH2, encoding="utf8")]
blocks = []
i = 0
while i < len(lines):
    l = lines[i]
    if not l.strip():
        i += 1
        continue
    if l.startswith("[TABLE"):
        cols = [int(x) for x in l[6:-1].split(",")]
        rows = []
        i += 1
        while i < len(lines) and lines[i].startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        blocks.append(("table", cols, rows))
        continue
    if l.startswith("# "):
        blocks.append(("h1", l[2:]))
    elif l.startswith("## "):
        blocks.append(("h2", l[3:]))
    elif l.startswith("### "):
        blocks.append(("h3", l[4:]))
    elif l.startswith("- "):
        blocks.append(("bullet", l[2:]))
    elif re.match(r"\d+\. ", l):
        blocks.append(("num", l.split(" ", 1)[1]))
    elif l.startswith("$$"):
        m_ = re.match(r"\$\$(.+?)\$\$\s*\((\d\.\d+)\)", l)
        blocks.append(("eq", m_.group(1).strip(), m_.group(2)))
    elif l.startswith("[FIG "):
        m_ = re.match(r"\[FIG (\S+)\]\s*(.*)", l)
        blocks.append(("fig", m_.group(1), m_.group(2)))
    elif l.startswith("[BOX "):
        m_ = re.match(r"\[BOX ([^\]]+)\]\s*(.*)", l)
        blocks.append(("box", m_.group(1), m_.group(2)))
    else:
        blocks.append(("p", l))
    i += 1

# collect every formula and convert them in one pandoc run
snips = []
for b in blocks:
    if b[0] == "eq":
        snips.append(b[1])
    elif b[0] == "table":
        for row in b[2]:
            for c in row:
                snips += inline_latex(c)
    else:
        for part in b[1:]:
            snips += inline_latex(part)
snips = list(dict.fromkeys(snips))
maths = dict(zip(snips, latex_to_omml(snips)))

# ------------------------------------------------------------ build
rels_path = f"{UN}/word/_rels/document.xml.rels"
rels = etree.parse(rels_path)
rid_n = max(int(r.get("Id")[3:]) for r in rels.getroot() if r.get("Id")[3:].isdigit()) + 1
docpr_n = max(int(d.get("id")) for d in body.iter(f"{{{WP}}}docPr")) + 1
fig_n = 0
out = []
list_id = None
prev_kind = None

for b in blocks:
    kind = b[0]
    if kind != "num":
        list_id = None
    if kind == "h1":
        num, title = re.match(r"Chapter (\d)\s*·\s*(.+)", b[1]).groups()
        p = copy.deepcopy(T_H1)
        ts = [t for t in p.iter(w("t")) if t.text]
        ts[0].text = f"Chapter {num}"
        ts[1].text = title
        out.append(p)
    elif kind in ("h2", "h3"):
        tpl = T_H2 if kind == "h2" else T_H3
        text = b[1]
        if kind == "h2":
            n, rest = text.split(" ", 1)
            text = n + " " + rest
        rpr = copy.deepcopy(tpl.find(f"{w('r')}/{w('rPr')}"))
        out.append(para_from(tpl, text, rpr, maths, size_of(rpr)))
    elif kind == "p":
        out.append(para_from(T_BODY, b[1], BODY_RPR, maths))
    elif kind == "bullet":
        out.append(para_from(T_BULLET, b[1], BULLET_RPR, maths))
    elif kind == "num":
        if list_id is None:
            list_id = new_list_id()
        p = para_from(T_NUM, b[1], BULLET_RPR, maths)
        p.find(f".//{w('numId')}").set(w("val"), str(list_id))
        out.append(p)
    elif kind == "eq":
        out.append(equation_table(maths[b[1]], b[2]))
    elif kind == "box":
        label, text = b[1], b[2]
        tbl = copy.deepcopy(T_BOX)
        tc = tbl.find(".//" + w("tc"))
        tps = tc.findall(w("p"))
        tpl_p = tps[0]
        label_run = copy.deepcopy(tpl_p.findall(w("r"))[0])
        content_rpr = plain_rpr(tpl_p.findall(w("r"))[1])
        for p_ in tps:
            tc.remove(p_)
        for k, seg in enumerate(text.split(" || ")):
            p = clear_runs(copy.deepcopy(tpl_p))
            if k == 0:
                lr = copy.deepcopy(label_run)
                lr.find(w("t")).text = label + "   "
                p.append(lr)
            for r in markup_runs(seg, content_rpr, maths, size_of(content_rpr)):
                p.append(r)
            tc.append(p)
        out.append(tbl)
    elif kind == "table":
        cols, rows = b[1], b[2]
        tbl = copy.deepcopy(T_TABLE)
        trs = tbl.findall(w("tr"))
        hdr_tpl, row_tpl = trs[0], trs[1]
        for tr in trs:
            tbl.remove(tr)
        grid = tbl.find(w("tblGrid"))
        for gc in list(grid):
            grid.remove(gc)
        for c in cols:
            grid.append(el("gridCol", w=c))
        for ri, row in enumerate(rows):
            tpl = hdr_tpl if ri == 0 else row_tpl
            tr = copy.deepcopy(tpl)
            tcs = tr.findall(w("tc"))
            cell_tpl = tcs[0]
            for tc in tcs:
                tr.remove(tc)
            for ci, (cell, width) in enumerate(zip(row, cols)):
                tc = copy.deepcopy(cell_tpl)
                tc.find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(width))
                p = tc.find(w("p"))
                rpr = copy.deepcopy(p.find(f"{w('r')}/{w('rPr')}"))
                if ri > 0:
                    for tag in ("b", "bCs"):
                        for e in rpr.findall(w(tag)):
                            rpr.remove(e)
                clear_runs(p)
                for r in markup_runs(cell, rpr, maths, size_of(rpr)):
                    p.append(r)
                tr.append(tc)
            tbl.append(tr)
        out.append(tbl)
    elif kind == "fig":
        name, caption = b[1], b[2]
        fig_n += 1
        rid = f"rId{rid_n}"
        rid_n += 1
        shutil.copy(f"{FIG}/{name}.png", f"{UN}/word/media/{name}.png")
        etree.SubElement(rels.getroot(), "Relationship", Id=rid,
                         Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                         Target=f"media/{name}.png")
        fp = copy.deepcopy(T_FIG)
        d = fp.find(".//" + w("drawing"))
        d.find(f".//{{{A}}}blip").set(f"{{{R}}}embed", rid)
        im = Image.open(f"{FIG}/{name}.png")
        cx = int(widths[name] * EMU)
        cy = int(cx * im.size[1] / im.size[0])
        for e in d.iter(f"{{{WP}}}extent", f"{{{A}}}ext"):
            e.set("cx", str(cx))
            e.set("cy", str(cy))
        dp = d.find(f".//{{{WP}}}docPr")
        dp.set("id", str(docpr_n))
        docpr_n += 1
        dp.set("name", name)
        dp.set("title", name)
        plain_caption = re.sub(r"\$([^$]*)\$", r"\1", caption)
        dp.set("descr", f"**Figure 2.{fig_n}:** {plain_caption}")
        cp = copy.deepcopy(T_CAP)
        cruns = cp.findall(w("r"))
        num_run = copy.deepcopy(cruns[0])
        rest_rpr = copy.deepcopy(cruns[1].find(w("rPr")))
        clear_runs(cp)
        num_run.find(w("t")).text = f"Figure 2.{fig_n}:"
        cp.append(num_run)
        for r in markup_runs(" " + caption, rest_rpr, maths, size_of(rest_rpr)):
            cp.append(r)
        jc = cp.find(f"{w('pPr')}/{w('jc')}")
        jc.set(w("val"), "both" if len(plain_caption) > 110 else "center")
        out.append(fp)
        out.append(cp)
    prev_kind = kind

# body text: indent continuation paragraphs, as restyle.py does for Chapter 1
prev = None
for e in out:
    is_body = etree.QName(e).localname == "p" and style_of(e) is None and e.find(".//" + w("drawing")) is None \
        and e.find(f"{w('pPr')}/{w('jc')}") is not None and e.find(f"{w('pPr')}/{w('jc')}").get(w("val")) == "both" \
        and not text_of(e).startswith("Figure 2.")
    if is_body:
        if prev is not None:
            sp = prev.find(f"{w('pPr')}/{w('spacing')}")
            if sp is not None:
                sp.set(w("after"), "30")
            pp = e.find(w("pPr"))
            ind = pp.find(w("ind"))
            if ind is None:
                ind = el("ind")
                jc = pp.find(w("jc"))
                jc.addprevious(ind)
            ind.set(w("firstLine"), "340")
            sp2 = pp.find(w("spacing"))
            if sp2 is not None:
                sp2.set(w("before"), "0")
        prev = e
    else:
        prev = None

for e in out:
    sect.addprevious(e)

# consecutive equation tables become one table (Word merges touching tables anyway);
# any other pair of touching tables gets a tiny spacer paragraph between them
def is_eq_table(e):
    if e is None or etree.QName(e).localname != "tbl":
        return False
    cap = e.find(f"{w('tblPr')}/{w('tblCaption')}")
    return cap is not None and cap.get(w("val")) == "equation"


for e in list(body):
    if etree.QName(e).localname != "tbl" or e.getparent() is None:
        continue
    nxt = e.getnext()
    while is_eq_table(e) and is_eq_table(nxt):
        for tr in nxt.findall(w("tr")):
            e.append(tr)
        body.remove(nxt)
        nxt = e.getnext()
for e in list(body):
    nxt = e.getnext()
    if etree.QName(e).localname == "tbl" and nxt is not None and etree.QName(nxt).localname == "tbl":
        sp = el("p")
        pp = el("pPr")
        pp.append(el("spacing", before=0, after=0, line=120, lineRule="exact"))
        rpr = el("rPr")
        rpr.append(el("sz", val=4))
        pp.append(rpr)
        sp.append(pp)
        e.addnext(sp)

# paragraphs with inline formulas: single (auto) line spacing so tall fractions get room
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
for p in body.iter(w("p")):
    if p.find(f"{{{M_NS}}}oMath") is not None:
        sp = p.find(f"{w('pPr')}/{w('spacing')}")
        if sp is not None:
            for att in ("line", "lineRule"):
                if sp.get(w(att)) is not None:
                    del sp.attrib[w(att)]

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)
rels.write(rels_path, xml_declaration=True, encoding="UTF-8", standalone=True)
num_xml = num_xml.replace("</w:numbering>", "".join(new_nums) + "</w:numbering>")
open(num_path, "w", encoding="utf8").write(num_xml)
print(f"chapter 2: {len(out)} elements, {fig_n} figures, {len(maths)} formulas")
