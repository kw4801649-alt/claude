"""Stage 4 (after post.py): make the guide compact without removing content.

- no text smaller than 12 pt (body, tables, call-outs, captions, equations);
- tighter margins and paragraph spacing, single line spacing;
- figures become half-width floating blocks (figure + caption) on the right,
  with the text wrapping round them; multi-panel figures stay full width.
usage: compact.py <unpacked dir> <figure dir>
"""
import json
import re
import sys
from PIL import Image
from lxml import etree

from eqlib import W, M, w, el

UN, FIG = sys.argv[1], sys.argv[2]
DEBUG = len(sys.argv) > 3
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
EMU = 914400
MIN = 24            # 12 pt, in half-points
TEXT_W = 11906 - 2 * 720
FLOAT_IN = 2.45      # width of a floating/side figure, inches
FULL_IN = 4.8

doc_path = f"{UN}/word/document.xml"
tree = etree.parse(doc_path)
root = tree.getroot()
body = root.find(w("body"))


def style_of(p):
    s = p.find(f"{w('pPr')}/{w('pStyle')}")
    return s.get(w("val")) if s is not None else None


def text_of(e):
    return "".join(t.text or "" for t in e.iter(w("t")))


def spacing(p, **kw):
    pp = p.find(w("pPr"))
    if pp is None:
        pp = el("pPr")
        p.insert(0, pp)
    sp = pp.find(w("spacing"))
    if sp is None:
        sp = el("spacing")
        # spacing sits after pStyle/keepNext/keepLines/pageBreakBefore/numPr/pBdr/shd/tabs
        after = [k for k in pp if etree.QName(k).localname in
                 ("pStyle", "keepNext", "keepLines", "pageBreakBefore", "numPr", "pBdr", "shd", "tabs")]
        (after[-1].addnext(sp) if after else pp.insert(0, sp))
    for k, v in kw.items():
        if v is None:
            sp.attrib.pop(w(k), None)
        else:
            sp.set(w(k), str(v))


# ------------------------------------------------------------ 1. page
sect = body.find(w("sectPr"))
mar = sect.find(w("pgMar"))
for k, v in dict(top=780, bottom=720, left=720, right=720, header=360, footer=340).items():
    mar.set(w(k), str(v))

# ------------------------------------------------------------ 2. sizes: nothing below 12 pt
for tag in ("sz", "szCs"):
    for e in root.iter(w(tag)):
        if e.getparent() is not None and etree.QName(e.getparent()).localname == "rPr":
            if int(e.get(w("val"))) < MIN:
                e.set(w("val"), str(MIN))
# the tiny spacer paragraphs between touching tables keep their tiny size
for p in body.iter(w("p")):
    sp = p.find(f"{w('pPr')}/{w('spacing')}")
    if sp is not None and sp.get(w("lineRule")) == "exact" and sp.get(w("line")) == "120":
        for e in p.iter(w("sz")):
            e.set(w("val"), "4")

# headings and title: smaller, but still the LaTeX look
for p in body.iter(w("p")):
    st = style_of(p)
    rs = [r for r in p.iter(w("r"))]
    def setsz(r, v):
        for tag in ("sz", "szCs"):
            e = r.find(f"{w('rPr')}/{w(tag)}")
            if e is not None:
                e.set(w("val"), str(v))
    if st == "Heading1":
        spacing(p, before=500, after=260)
        texts = [r for r in rs if r.find(w("t")) is not None and (r.find(w("t")).text or "").strip()]
        if len(texts) == 2:
            setsz(texts[0], 34)
            setsz(texts[1], 40)
        else:
            for r in texts:
                setsz(r, 40)
    elif st == "Heading2":
        spacing(p, before=220, after=80)
        for r in rs:
            setsz(r, 28)
    elif st == "Heading3":
        spacing(p, before=140, after=40)
        for r in rs:
            setsz(r, 25)

paras = list(body.iter(w("p")))
for r in paras[1].iter(w("r")):          # title
    for tag in ("sz", "szCs"):
        e = r.find(f"{w('rPr')}/{w(tag)}")
        if e is not None:
            e.set(w("val"), "44")
spacing(paras[0], before=0, after=40)

# ------------------------------------------------------------ 3. spacing
for p in body.iter(w("p")):
    st = style_of(p)
    if st in ("Heading1", "Heading2", "Heading3"):
        continue
    sp = p.find(f"{w('pPr')}/{w('spacing')}")
    if sp is not None and sp.get(w("lineRule")) == "exact":
        continue
    in_tc = any(etree.QName(a).localname == "tc" for a in p.iterancestors())
    if in_tc:
        spacing(p, line=240, lineRule="auto", after=0, before=0)
    elif st == "ListParagraph":
        spacing(p, line=240, lineRule="auto", after=20, before=0)
    else:
        b = sp.get(w("before")) if sp is not None else None
        a = sp.get(w("after")) if sp is not None else None
        spacing(p, line=240, lineRule="auto",
                before=min(int(b), 60) if b else None,
                after=(min(int(a), 50) if a else 50))

# table cells: smaller margins
for mar_ in body.iter(w("tcMar")):
    for side in mar_:
        if etree.QName(side).localname in ("top", "bottom"):
            side.set(w("w"), "10")
        else:
            side.set(w("w"), "80")
# equation rows: a little space only
for cap in body.iter(w("tblCaption")):
    if cap.get(w("val")) == "equation":
        tbl = cap.getparent().getparent()
        for p in tbl.iter(w("p")):
            spacing(p, before=30, after=30)
        # equation tables follow the new text width
        side = 1150
        grid = tbl.find(w("tblGrid")).findall(w("gridCol"))
        grid[1].set(w("w"), str(TEXT_W - 2 * side))
        tbl.find(f"{w('tblPr')}/{w('tblW')}").set(w("w"), str(TEXT_W))
        for tr in tbl.findall(w("tr")):
            tr.findall(w("tc"))[1].find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(TEXT_W - 2 * side))

# data tables / call-outs: scale column widths to the new text width
for tbl in body.iter(w("tbl")):
    tp = tbl.find(w("tblPr"))
    if tp.find(w("tblCaption")) is not None:
        continue
    tw = tp.find(w("tblW"))
    old = int(tw.get(w("w")))
    if old <= 0:
        continue
    f = TEXT_W / old
    tw.set(w("w"), str(TEXT_W))
    for gc in tbl.find(w("tblGrid")):
        gc.set(w("w"), str(int(int(gc.get(w("w"))) * f)))
    for tcw in tbl.iter(w("tcW")):
        tcw.set(w("w"), str(int(int(tcw.get(w("w"))) * f)))

# ------------------------------------------------------------ 4. equations: short ones two per row
M_T = f"{{{M}}}t"


def eq_len(tc):
    return sum(len(t.text or "") for t in tc.iter(M_T))


for cap in list(body.iter(w("tblCaption"))):
    if cap.get(w("val")) != "equation":
        continue
    tbl = cap.getparent().getparent()
    rows = tbl.findall(w("tr"))
    if len(rows) < 2 or max(eq_len(r.findall(w("tc"))[1]) for r in rows) > 24:
        continue
    num_w, eq_w = 900, TEXT_W // 2 - 900
    grid = tbl.find(w("tblGrid"))
    for g in list(grid):
        grid.remove(g)
    for wd in (eq_w, num_w, eq_w, num_w):
        grid.append(el("gridCol", w=wd))
    cells = [(r.findall(w("tc"))[1], r.findall(w("tc"))[2]) for r in rows]
    for r in rows:
        tbl.remove(r)
    for k in range(0, len(cells), 2):
        tr = el("tr")
        trpr = el("trPr")
        trpr.append(el("cantSplit"))
        tr.append(trpr)
        pair = cells[k:k + 2]
        for eq_tc, num_tc in pair:
            eq_tc.find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(eq_w))
            num_tc.find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(num_w))
            tr.append(eq_tc)
            tr.append(num_tc)
        if len(pair) == 1:
            for wd in (eq_w, num_w):
                tc = el("tc")
                tcp = el("tcPr")
                tcp.append(el("tcW", type="dxa", w=wd))
                tc.append(tcp)
                tc.append(el("p"))
                tr.append(tc)
        tbl.append(tr)

# ------------------------------------------------------------ 5. figures
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RELS = {r.get("Id"): r.get("Target") for r in etree.parse(f"{UN}/word/_rels/document.xml.rels").getroot()}
PT_LINE = 13.8             # 12 pt CMU Serif, single spacing
CHARS_BESIDE = 62          # characters per line in the text column beside a float
CHARS_CAPTION = 50         # characters per caption line inside a float


def borderless_table(widths_, caption):
    tbl = el("tbl")
    tp = el("tblPr")
    tbl.append(tp)
    tp.append(el("tblW", type="dxa", w=sum(widths_)))
    b = el("tblBorders")
    for s_ in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(el(s_, val="none", sz=0, space=0, color="auto"))
    tp.append(b)
    tp.append(el("tblLayout", type="fixed"))
    m_ = el("tblCellMar")
    m_.append(el("left", w=0, type="dxa"))
    m_.append(el("right", w=0, type="dxa"))
    tp.append(m_)
    tp.append(el("tblCaption", val=caption))
    g = el("tblGrid")
    for wd in widths_:
        g.append(el("gridCol", w=wd))
    tbl.append(g)
    tr = el("tr")
    trpr = el("trPr")
    trpr.append(el("cantSplit"))
    tr.append(trpr)
    tbl.append(tr)
    cells = []
    for wd in widths_:
        tc = el("tc")
        tcp = el("tcPr")
        tcp.append(el("tcW", type="dxa", w=wd))
        tcp.append(el("vAlign", val="center"))
        tc.append(tcp)
        tr.append(tc)
        cells.append(tc)
    return tbl, cells


def plain_text_para(e):
    return (e is not None and etree.QName(e).localname == "p" and style_of(e) in (None, "ListParagraph")
            and e.find(".//" + w("drawing")) is None and text_of(e).strip()
            and not re.match(r"Figure \d\.\d+:", text_of(e)))


def text_room(start, need_pt, skip=()):
    """Is there enough plain text (and headings) from `start` on to fill need_pt beside a float?"""
    have = 0.0
    e = start
    while e is not None and have < need_pt:
        if any(e is k for k in skip):
            e = e.getnext()
            continue
        tag = etree.QName(e).localname
        if tag != "p" or e.find(".//" + w("drawing")) is not None:
            return False
        st_ = style_of(e)
        if st_ == "Heading1":
            return False
        if st_ in ("Heading2", "Heading3"):
            have += 30
        else:
            n = len(text_of(e))
            have += (n // CHARS_BESIDE + 1) * PT_LINE + 3
        e = e.getnext()
    return have >= need_pt


def prep_parts(fig_p, cap_p, win):
    d = fig_p.find(".//" + w("drawing"))
    target = RELS[d.find(f".//{{{A}}}blip").get(f"{{{R}}}embed")]
    im = Image.open(f"{UN}/word/{target}")
    cx = int(win * EMU)
    cy = int(cx * im.size[1] / im.size[0])
    for e in d.iter(f"{{{WP}}}extent", f"{{{A}}}ext"):
        e.set("cx", str(cx))
        e.set("cy", str(cy))
    for p_ in (fig_p, cap_p):
        ind = p_.find(f"{w('pPr')}/{w('ind')}")
        if ind is not None:
            ind.getparent().remove(ind)
    return cy / EMU * 72, target


def is_eq(e):
    cap = e.find(f"{w('tblPr')}/{w('tblCaption')}") if etree.QName(e).localname == "tbl" else None
    return cap is not None and cap.get(w("val")) == "equation"


_num = etree.parse(f"{UN}/word/numbering.xml").getroot()
_abs = {}
for an in _num.findall(w("abstractNum")):
    lvl = an.find(w("lvl"))
    ind_ = lvl.find(f"{w('pPr')}/{w('ind')}")
    _abs[an.get(w("abstractNumId"))] = (int(ind_.get(w("left"))), int(ind_.get(w("hanging"))))
LIST_IND = {n.get(w("numId")): _abs[n.find(w("abstractNumId")).get(w("val"))] for n in _num.findall(w("num"))}


def is_box(e):
    return (etree.QName(e).localname == "tbl" and e.find(f"{w('tblPr')}/{w('tblCaption')}") is None
            and len(e.find(w("tblGrid"))) == 1)


def beside_text(fp, cp, h_pt, wd):
    """Figure with its caption underneath on the left; the paragraphs that follow it flow
    into the right-hand cell. Wrap-around done with a table, so every renderer agrees."""
    gap = 240
    right_w = TEXT_W - wd
    chars = int(right_w / 1440 * 13.8)          # about 13.8 characters per inch at 12 pt
    left_h = h_pt + (len(text_of(cp)) // int(wd / 1440 * 13.8) + 1) * PT_LINE + 8
    def cost(e):
        tag = etree.QName(e).localname
        if tag == "p":
            st_ = style_of(e)
            if st_ not in (None, "ListParagraph") or e.find(".//" + w("drawing")) is not None:
                return None
            if not text_of(e).strip() and e.find(f".//{{{M}}}oMath") is None:
                return None
            if re.match(r"Figure \d\.\d+:", text_of(e)):
                return None
            lines = len(text_of(e)) // chars + 1
            return lines * (PT_LINE + (3 if e.find(f".//{{{M}}}oMath") is not None else 0)) + 3
        if is_eq(e):
            return 30 * len(e.findall(w("tr")))
        if tag == "tbl" and is_box(e):
            return (len(text_of(e)) // (chars - 4) + 1) * PT_LINE + 14
        return None

    after_, have = [], 0.0
    e = cp.getnext()
    while e is not None and have < left_h:
        c = cost(e)
        if c is None:
            break
        after_.append(e)
        have += c
        e = e.getnext()
    before_ = []
    e = fp.getprevious()
    while e is not None and have < left_h:
        c = cost(e)
        if c is None:
            break
        before_.insert(0, e)
        have += c
        e = e.getprevious()
    take = before_ + after_
    if have < 0.4 * left_h or not take:
        return False
    # do not leave a heading or table hanging just after a very short remainder: fine either way
    tbl, (tc1, tc2) = borderless_table([wd, right_w], "figure")
    for tc in (tc1, tc2):
        tc.find(f"{w('tcPr')}/{w('vAlign')}").set(w("val"), "top")
    (take[0] if before_ else fp).addprevious(tbl)
    fp.getparent().remove(fp)
    cp.getparent().remove(cp)
    tc1.append(fp)
    tc1.append(cp)
    for k, e in enumerate(take):
        e.getparent().remove(e)
        if etree.QName(e).localname == "p":
            pp = e.find(w("pPr"))
            ind = pp.find(w("ind"))
            if ind is None:
                ind = el("ind")
                jc = pp.find(w("jc"))
                (jc.addprevious(ind) if jc is not None else pp.append(ind))
            num = e.find(f"{w('pPr')}/{w('numPr')}/{w('numId')}")
            if num is not None and ind.get(w("left")) is None:
                base_left, hang = LIST_IND.get(num.get(w("val")), (560, 280))
                ind.set(w("left"), str(gap + base_left))
                ind.set(w("hanging"), str(hang))
            else:
                ind.set(w("left"), str(gap + int(ind.get(w("left"), "0"))))
            if k == 0 and ind.get(w("firstLine")):
                del ind.attrib[w("firstLine")]
        elif is_box(e):
            tw_ = e.find(f"{w('tblPr')}/{w('tblW')}")
            tw_.set(w("w"), str(right_w - gap))
            tw_.addnext(el("tblInd", w=gap, type="dxa"))
            e.find(w("tblGrid"))[0].set(w("w"), str(right_w - gap))
            for tcw in e.iter(w("tcW")):
                tcw.set(w("w"), str(right_w - gap))
        else:  # equation table: fit the narrower cell
            cols = e.find(w("tblGrid")).findall(w("gridCol"))
            ws = [int(c.get(w("w"))) for c in cols]
            f = (right_w - gap) / sum(ws)
            e.find(f"{w('tblPr')}/{w('tblW')}").set(w("w"), str(right_w - gap))
            ind_ = el("tblInd", w=gap, type="dxa")
            e.find(f"{w('tblPr')}/{w('tblW')}").addnext(ind_)
            # number columns stay wide enough for "(1.12)"; the equation columns share the rest
            new = []
            num_cols = [i for i, x in enumerate(ws) if x <= 1150]
            eq_cols = [i for i in range(len(ws)) if i not in num_cols]
            rest = right_w - gap - 850 * len(num_cols)
            for i in range(len(ws)):
                new.append(850 if i in num_cols else rest // len(eq_cols))
            if len(ws) == 3:          # [ side | eq | number ]: drop the left spacer width
                new = [200, right_w - gap - 200 - 850, 850]
            for c, v in zip(cols, new):
                c.set(w("w"), str(v))
            for tr in e.findall(w("tr")):
                for tc, v in zip(tr.findall(w("tc")), new):
                    tc.find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(v))
        tc2.append(e)
    tc2.append(el("p"))  # a cell must end with a paragraph
    tc2[-1].append(el("pPr"))
    tc2[-1][0].append(el("spacing", before=0, after=0, line=120, lineRule="exact"))
    spacing(fp, before=40, after=20)
    spacing(cp, before=0, after=60)
    return True


stats = {"float": 0, "side": 0, "full": 0}
figs = [p for p in list(body.iter(w("p"))) if p.find(".//" + w("drawing")) is not None]
for fp in figs:
    cp = fp.getnext()
    name = fp.find(f".//{{{WP}}}docPr").get("name")
    target = RELS[fp.find(f".//{{{A}}}blip").get(f"{{{R}}}embed")]
    if name == "f_terminal" or target.split("/")[-1] in {"f_fbd.png", "f_thirdlaw.png", "f_stokes.png"}:
        prep_parts(fp, cp, FULL_IN)
        spacing(fp, before=40, after=20)
        spacing(cp, before=0, after=100)
        stats["full"] += 1
        continue
    h_pt, _ = prep_parts(fp, cp, FLOAT_IN)
    need = h_pt + (len(text_of(cp)) // CHARS_CAPTION + 1) * PT_LINE + 10
    prev, nxt = fp.getprevious(), cp.getnext()
    anchor = None
    if plain_text_para(prev) and text_room(prev, need, (fp, cp)):
        anchor = prev
    elif plain_text_para(nxt) and text_room(nxt, need):
        anchor = nxt
    spacing(fp, before=0, after=20)
    fp.find(f"{w('pPr')}/{w('jc')}").set(w("val"), "center")
    spacing(cp, before=0, after=0)
    cp.find(f"{w('pPr')}/{w('jc')}").set(w("val"), "both")
    wd = int(FLOAT_IN * 1440) + 60
    if DEBUG:
        def why(start, skip=()):
            out = []; e = start; have = 0
            while e is not None and have < need and len(out) < 12:
                if any(e is k for k in skip): e = e.getnext(); continue
                tag = etree.QName(e).localname
                out.append((tag, style_of(e) if tag == "p" else "", len(text_of(e))))
                if tag != "p": break
                have += (len(text_of(e)) // CHARS_BESIDE + 1) * PT_LINE + 3
                e = e.getnext()
            return out
        print(name, int(need), anchor is not None, text_room(prev, need, (fp, cp)), why(prev, (fp, cp)) if prev is not None else None)
    if anchor is not None:
        tbl, (tc,) = borderless_table([wd], "figure")
        tbl.find(w("tblPr")).insert(0, el("tblOverlap", val="never"))
        tbl.find(w("tblPr")).insert(0, el("tblpPr", leftFromText=230, rightFromText=0, topFromText=40,
                                            bottomFromText=110, vertAnchor="text", horzAnchor="margin",
                                            tblpXSpec="right", tblpY=1))
        fp.getparent().remove(fp)
        cp.getparent().remove(cp)
        tc.append(fp)
        tc.append(cp)
        anchor.addprevious(tbl)
        stats["float"] += 1
    elif beside_text(fp, cp, h_pt, wd):
        stats["beside"] = stats.get("beside", 0) + 1
    else:
        # side caption: figure on the left, caption beside it
        gap = 260
        tbl, (tc1, tc2) = borderless_table([wd, TEXT_W - wd], "figure")
        fp.addprevious(tbl)
        fp.getparent().remove(fp)
        cp.getparent().remove(cp)
        tc1.append(fp)
        pp = cp.find(w("pPr"))
        ind = el("ind", left=gap)
        pp.find(w("jc")).addprevious(ind)
        tc2.append(cp)
        spacing(fp, before=40, after=60)
        stats["side"] += 1

# a table directly followed by a table (e.g. a side-caption figure then a call-out): add a spacer
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

# ------------------------------------------------------------ 6. page breaks, contents, line height
for p in body.iter(w("p")):
    if style_of(p) == "Heading1":
        pb = p.find(f"{w('pPr')}/{w('pageBreakBefore')}")
        if pb is not None:
            pb.getparent().remove(pb)
        spacing(p, before=360, after=200)

# contents: two columns of sections side by side
toc = next(t for t in body.iter(w("tbl")) if text_of(t.find(".//" + w("tc"))).strip() == "Section")
rows = toc.findall(w("tr"))
hdr, data = rows[0], rows[1:]
half = (len(data) + 1) // 2
split = next(i for i, r in enumerate(data) if text_of(r).startswith("Chapter 2"))
left, right = data[:split], data[split:]
cw = TEXT_W // 2
grid = toc.find(w("tblGrid"))
for g in list(grid):
    grid.remove(g)
for wd in (1250, cw - 1250, 1250, cw - 1250):
    grid.append(el("gridCol", w=wd))


def set_w(tc, wd):
    tc.find(f"{w('tcPr')}/{w('tcW')}").set(w("w"), str(wd))


import copy as _copy
for r in rows:
    toc.remove(r)
hdr2 = _copy.deepcopy(hdr)
for tc in list(_copy.deepcopy(hdr)):
    pass
new_hdr = _copy.deepcopy(hdr)
for tc in [_copy.deepcopy(c) for c in hdr.findall(w("tc"))]:
    new_hdr.append(tc)
for tc, wd in zip(new_hdr.findall(w("tc")), (1250, cw - 1250, 1250, cw - 1250)):
    set_w(tc, wd)
toc.append(new_hdr)
empty_row = left[1] if len(left) > 1 else left[0]
for i in range(max(len(left), len(right))):
    a_ = left[i] if i < len(left) else None
    b_ = right[i] if i < len(right) else None
    tr = _copy.deepcopy(a_ if a_ is not None else b_)
    for tc in tr.findall(w("tc")):
        tr.remove(tc)
    for src in (a_, b_):
        if src is not None:
            cells = [_copy.deepcopy(c) for c in src.findall(w("tc"))]
        else:
            cells = [_copy.deepcopy(c) for c in empty_row.findall(w("tc"))]
            for c in cells:
                for t in c.iter(w("t")):
                    t.text = ""
        for c in cells:
            tr.append(c)
    for tc, wd in zip(tr.findall(w("tc")), (1250, cw - 1250, 1250, cw - 1250)):
        set_w(tc, wd)
    toc.append(tr)

# exact 14.2 pt lines (what Word's "single" gives for 12 pt CMU Serif) wherever the line holds only
# 12 pt text, so every renderer lays the page out the same way
for p in body.iter(w("p")):
    if p.find(f".//{{{M}}}oMath") is not None or p.find(".//" + w("drawing")) is not None:
        continue
    if style_of(p) in ("Heading1", "Heading2", "Heading3"):
        continue
    szs = [int(e.get(w("val"))) for e in p.iter(w("sz"))]
    if szs and max(szs) > 24:
        continue
    sp = p.find(f"{w('pPr')}/{w('spacing')}")
    if sp is not None and sp.get(w("lineRule")) == "exact":
        continue
    spacing(p, line=276, lineRule="exact")

tree.write(doc_path, xml_declaration=True, encoding="UTF-8", standalone=True)

# ------------------------------------------------------------ 5. styles default: 12 pt, single spacing
st_p = f"{UN}/word/styles.xml"
st = open(st_p, encoding="utf8").read()
st = st.replace('<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang', '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang')
st = st.replace('<w:spacing w:after="120" w:line="264" w:lineRule="auto"/>',
                '<w:spacing w:after="70" w:line="240" w:lineRule="auto"/>')
open(st_p, "w", encoding="utf8").write(st)
print("compact:", stats)
