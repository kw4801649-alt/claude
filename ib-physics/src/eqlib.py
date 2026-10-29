"""Shared helpers: LaTeX -> Office Math (OMML) via pandoc, numbered display
equations, inline formulas, and a tiny inline markup for new paragraphs."""
import copy
import os
import re
import subprocess
import tempfile
import zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
FONT = "CMU Serif"


def w(tag):
    return f"{{{W}}}{tag}"


def m(tag):
    return f"{{{M}}}{tag}"


def el(tag, **attrs):
    e = etree.Element(w(tag))
    for k, v in attrs.items():
        e.set(w(k), str(v))
    return e


# ------------------------------------------------------------------ pandoc
def latex_to_omml(snippets):
    """Convert a list of LaTeX strings to a list of <m:oMath> elements."""
    with tempfile.TemporaryDirectory() as td:
        md = os.path.join(td, "eq.md")
        out = os.path.join(td, "eq.docx")
        with open(md, "w", encoding="utf8") as f:
            for s in snippets:
                f.write("$" + s.strip() + "$\n\n")
        subprocess.run(["pandoc", md, "-f", "markdown+tex_math_dollars", "-o", out], check=True)
        root = etree.fromstring(zipfile.ZipFile(out).read("word/document.xml"))
    maths = []
    for p in root.iter(w("p")):
        found = list(p.iter(m("oMath")))
        if not found:
            continue
        assert len(found) == 1, etree.tostring(p)[:300]
        maths.append(found[0])
    assert len(maths) == len(snippets), (len(maths), len(snippets))
    for om in maths:
        _schema_fix(om)
        for acc in list(om.iter(m("acc"))):
            chr_ = acc.find(f"{m('accPr')}/{m('chr')}")
            if chr_ is not None and chr_.get(m("val")) == "‾":  # \bar -> Word's overbar structure
                bar = etree.Element(m("bar"))
                pr = etree.SubElement(bar, m("barPr"))
                etree.SubElement(pr, m("pos")).set(m("val"), "top")
                bar.append(acc.find(m("e")))
                acc.addprevious(bar)
                acc.getparent().remove(acc)
    return maths


def _reorder(e, order):
    kids = list(e)
    kids.sort(key=lambda k: order.index(etree.QName(k).localname) if etree.QName(k).localname in order else 99)
    for k in kids:
        e.remove(k)
    for k in kids:
        e.append(k)


def _schema_fix(om):
    """pandoc writes a few OMML property elements in an order the schema rejects."""
    for dpr in om.iter(m("dPr")):
        _reorder(dpr, ["begChr", "sepChr", "endChr", "grow", "shp", "ctrlPr"])
    for rpr in om.iter(m("rPr")):
        if rpr.find(m("nor")) is not None:
            for sty in rpr.findall(m("sty")):
                rpr.remove(sty)
        _reorder(rpr, ["lit", "nor", "scr", "sty", "brk", "aln"])


def size_math(om, half_points):
    """Give every math run an explicit size (for tables, captions, call-outs)."""
    om = copy.deepcopy(om)
    for r in om.iter(m("r")):
        rpr = el("rPr")
        rpr.append(el("rFonts", ascii="Cambria Math", hAnsi="Cambria Math"))
        rpr.append(el("sz", val=half_points))
        rpr.append(el("szCs", val=half_points))
        mrpr = r.find(m("rPr"))
        r.insert(1 if mrpr is not None else 0, rpr)
    return om


# ------------------------------------------------------------------ display equations
def equation_table(om, number, text_width=9638, side=1150):
    """A borderless 3-column table: [ | centred display equation | (n.n) ].

    Word renders an equation that is alone in its paragraph in display style
    (full-size stacked fractions), and the number stays right-aligned."""
    mid = text_width - 2 * side
    tbl = el("tbl")
    tp = el("tblPr")
    tp.append(el("tblCaption", val="equation"))
    tp.append(el("tblW", type="dxa", w=text_width))
    b = el("tblBorders")
    for s in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(el(s, val="none", sz=0, space=0, color="auto"))
    tp.append(b)
    tp.append(el("tblLayout", type="fixed"))
    mar = el("tblCellMar")
    mar.append(el("left", w=0, type="dxa"))
    mar.append(el("right", w=0, type="dxa"))
    tp.append(mar)
    # tblCaption must come after tblW etc. in the schema: reorder
    order = ["tblW", "tblBorders", "tblLayout", "tblCellMar", "tblCaption"]
    kids = sorted(list(tp), key=lambda k: order.index(etree.QName(k).localname))
    for k in kids:
        tp.remove(k)
    for k in kids:
        tp.append(k)
    tbl.append(tp)
    grid = el("tblGrid")
    for wd in (side, mid, side):
        grid.append(el("gridCol", w=wd))
    tbl.append(grid)
    tr = el("tr")
    trpr = el("trPr")
    trpr.append(el("cantSplit"))
    tr.append(trpr)
    for i, wd in enumerate((side, mid, side)):
        tc = el("tc")
        tcp = el("tcPr")
        tcp.append(el("tcW", type="dxa", w=wd))
        tcp.append(el("vAlign", val="center"))
        tc.append(tcp)
        p = el("p")
        pp = el("pPr")
        pp.append(el("keepLines"))
        pp.append(el("spacing", before=70, after=110, line=240, lineRule="auto"))
        pp.append(el("jc", val=["left", "center", "right"][i]))
        p.append(pp)
        if i == 1:
            para = etree.SubElement(p, m("oMathPara"))
            ppr = etree.SubElement(para, m("oMathParaPr"))
            etree.SubElement(ppr, m("jc")).set(m("val"), "center")
            para.append(copy.deepcopy(om))
        elif i == 2 and number:
            r = el("r")
            rpr = el("rPr")
            rpr.append(el("rFonts", ascii=FONT, hAnsi=FONT, cs=FONT, eastAsia=FONT))
            rpr.append(el("sz", val=22))
            rpr.append(el("szCs", val=22))
            r.append(rpr)
            t = el("t")
            t.text = f"({number})"
            r.append(t)
            p.append(r)
        tc.append(p)
        tr.append(tc)
    tbl.append(tr)
    return tbl


# ------------------------------------------------------------------ inline formulas in existing text
def _direct_runs(p):
    return [r for r in p if etree.QName(r).localname == "r" and r.find(w("t")) is not None]


def _split(r, k):
    """Split run r at character k; returns (left, right) runs (both in the tree)."""
    t = r.find(w("t"))
    s = t.text or ""
    if k <= 0 or k >= len(s):
        return None
    r2 = copy.deepcopy(r)
    t.text = s[:k]
    r2.find(w("t")).text = s[k:]
    for tt in (t, r2.find(w("t"))):
        tt.set(XML_SPACE, "preserve")
    r.addnext(r2)
    return r, r2


def replace_inline(p, pairs, maths):
    """Replace text in paragraph p with inline equations.

    pairs: list of (exact substring, key); maths: dict key -> oMath.
    Substrings are searched in order, each after the previous match."""
    pos = 0
    for sub, key in pairs:
        runs = _direct_runs(p)
        full = "".join(r.find(w("t")).text or "" for r in runs)
        a = full.find(sub, pos)
        if a < 0:
            raise ValueError(f"not found: {sub!r} in {full!r}")
        b = a + len(sub)
        # split at a and at b
        for cut in (b, a):
            acc = 0
            for r in _direct_runs(p):
                n = len(r.find(w("t")).text or "")
                if acc < cut < acc + n:
                    _split(r, cut - acc)
                    break
                acc += n
        acc = 0
        inside = []
        for r in _direct_runs(p):
            n = len(r.find(w("t")).text or "")
            if acc >= a and acc + n <= b and n:
                inside.append(r)
            acc += n
        first = inside[0]
        sz = first.find(w("rPr") + "/" + w("sz")) if first.find(w("rPr")) is not None else None
        om = maths[key]
        om = size_math(om, sz.get(w("val"))) if sz is not None else copy.deepcopy(om)
        first.addprevious(om)
        for r in inside:
            p.remove(r)
        pos = a  # the formula is no longer text, so the next search starts where it was
    return p


# ------------------------------------------------------------------ markup -> runs
TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|\$[^$]+?\$|\^\{[^}]*\}|_\{[^}]*\})")


def markup_runs(text, base_rpr, maths, math_size=None):
    """Turn **bold**, *italic*, $math$, ^{sup}, _{sub} markup into run/math elements."""
    out = []

    def run(s, bold=False, italic=False, va=None):
        r = el("r")
        rpr = copy.deepcopy(base_rpr) if base_rpr is not None else el("rPr")
        if bold and rpr.find(w("b")) is None:
            rpr.insert(1, el("b"))
            rpr.insert(2, el("bCs"))
        if italic:
            rpr.insert(1, el("i"))
            rpr.insert(2, el("iCs"))
        if va:
            rpr.append(el("vertAlign", val=va))
        order = ["rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "color", "spacing", "sz", "szCs", "vertAlign"]
        kids = sorted(list(rpr), key=lambda k: order.index(etree.QName(k).localname)
                      if etree.QName(k).localname in order else 99)
        for k in kids:
            rpr.remove(k)
        for k in kids:
            rpr.append(k)
        r.append(rpr)
        t = el("t")
        t.text = s
        t.set(XML_SPACE, "preserve")
        r.append(t)
        return r

    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**"):
            for sub in markup_runs(part[2:-2], base_rpr, maths, math_size):
                if etree.QName(sub).localname == "r":
                    rp = sub.find(w("rPr"))
                    if rp.find(w("b")) is None:
                        rp.insert(1, el("b"))
                        rp.insert(2, el("bCs"))
                out.append(sub)
        elif part.startswith("*"):
            out.append(run(part[1:-1], italic=True))
        elif part.startswith("$"):
            om = maths[part[1:-1]]
            out.append(size_math(om, math_size) if math_size else copy.deepcopy(om))
        elif part.startswith("^{"):
            out.append(run(part[2:-1], va="superscript"))
        elif part.startswith("_{"):
            out.append(run(part[2:-1], va="subscript"))
        else:
            out.append(run(part))
    return out


def inline_latex(text):
    """All $...$ snippets in a markup string."""
    return [s[1:-1] for s in re.findall(r"\$[^$]+?\$", text)]
