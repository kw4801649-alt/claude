"""Package-level restyle: fonts (embedded CMU Serif), styles, running heads,
list bullets and settings.

usage: finish.py <unpacked dir> <font dir>
"""
import re
import sys
import uuid
from pathlib import Path

UN, FONTS = Path(sys.argv[1]), Path(sys.argv[2])
FONT = "CMU Serif"
W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
R_NS = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'

# ---------------------------------------------------------------- fonts everywhere
for part in ["document.xml", "styles.xml", "numbering.xml", "footnotes.xml", "endnotes.xml", "comments.xml"]:
    p = UN / "word" / part
    s = p.read_text(encoding="utf8")
    s = s.replace('"Calibri"', f'"{FONT}"').replace('"Cambria"', f'"{FONT}"')
    p.write_text(s, encoding="utf8")

# ---------------------------------------------------------------- styles
st = (UN / "word/styles.xml").read_text(encoding="utf8")
st = st.replace('<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault/>',
                '<w:color w:val="000000"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
                '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault>')
st = re.sub(r'<w:color w:val="(2E74B5|1F4D78|1B2F5B|1F4E9C)"/>', '<w:color w:val="000000"/>', st)
(UN / "word/styles.xml").write_text(st, encoding="utf8")

# bullets: plain LaTeX bullet
nb = (UN / "word/numbering.xml").read_text(encoding="utf8")
nb = nb.replace('<w:lvlText w:val="●"/>', '<w:lvlText w:val="•"/>')
(UN / "word/numbering.xml").write_text(nb, encoding="utf8")

# ---------------------------------------------------------------- running heads
HEAD_NS = (UN / "word/header1.xml").read_text(encoding="utf8")
open_tag = re.match(r'(<\?xml[^>]*\?>)?\s*(<w:hdr[^>]*>)', HEAD_NS).group(2)
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
RPR = (f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}" w:eastAsia="{FONT}"/>'
       '<w:i/><w:iCs/><w:caps/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>')
RPR_NUM = (f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}" w:eastAsia="{FONT}"/>'
           '<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>')
TABS = '<w:tabs><w:tab w:val="right" w:pos="10466"/></w:tabs>'
PPR = f'<w:pPr>{TABS}<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'


def page_field():
    return (f'<w:r>{RPR_NUM}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{RPR_NUM}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            f'<w:r>{RPR_NUM}<w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{RPR_NUM}<w:t>1</w:t></w:r>'
            f'<w:r>{RPR_NUM}<w:fldChar w:fldCharType="end"/></w:r>')


def styleref(style, cached):
    return (f'<w:r>{RPR}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{RPR}<w:instrText xml:space="preserve"> STYLEREF "{style}" </w:instrText></w:r>'
            f'<w:r>{RPR}<w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{RPR}<w:t xml:space="preserve">{cached}</w:t></w:r>'
            f'<w:r>{RPR}<w:fldChar w:fldCharType="end"/></w:r>')


TAB_RUN = f'<w:r>{RPR}<w:tab/></w:r>'
# odd (right-hand) pages: current section on the left, page number on the right
odd = f'{XML}{open_tag}<w:p>{PPR}{styleref("Heading 2", "A.1 Kinematics")}{TAB_RUN}{page_field()}</w:p></w:hdr>'
# even (left-hand) pages: page number on the left, guide title on the right
even = (f'{XML}{open_tag}<w:p>{PPR}{page_field()}{TAB_RUN}'
        f'<w:r>{RPR}<w:t xml:space="preserve">IB Physics SL.  Kinematics, forces and momentum</w:t></w:r></w:p></w:hdr>')
first = f'{XML}{open_tag}<w:p>{PPR}</w:p></w:hdr>'
(UN / "word/header1.xml").write_text(odd, encoding="utf8")
(UN / "word/header2.xml").write_text(even, encoding="utf8")
(UN / "word/header3.xml").write_text(first, encoding="utf8")

FOOT = (UN / "word/footer1.xml").read_text(encoding="utf8")
fopen = re.match(r'(<\?xml[^>]*\?>)?\s*(<w:ftr[^>]*>)', FOOT).group(2)
empty_footer = f'{XML}{fopen}<w:p><w:pPr></w:pPr></w:p></w:ftr>'
first_footer = (f'{XML}{fopen}<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
                f'{page_field()}</w:p></w:ftr>')
(UN / "word/footer1.xml").write_text(empty_footer, encoding="utf8")
(UN / "word/footer2.xml").write_text(first_footer, encoding="utf8")

rels_p = UN / "word/_rels/document.xml.rels"
rels = rels_p.read_text(encoding="utf8")
HDR_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
FTR_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
FNT_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
add = (f'<Relationship Id="rIdHdrEven" Type="{HDR_T}" Target="header2.xml"/>'
       f'<Relationship Id="rIdHdrFirst" Type="{HDR_T}" Target="header3.xml"/>'
       f'<Relationship Id="rIdFtrFirst" Type="{FTR_T}" Target="footer2.xml"/>')
rels = rels.replace("</Relationships>", add + "</Relationships>")
rels_p.write_text(rels, encoding="utf8")

ct_p = UN / "[Content_Types].xml"
ct = ct_p.read_text(encoding="utf8")
H_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
F_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
ct = ct.replace("</Types>",
                f'<Override ContentType="{H_CT}" PartName="/word/header2.xml"/>'
                f'<Override ContentType="{H_CT}" PartName="/word/header3.xml"/>'
                f'<Override ContentType="{F_CT}" PartName="/word/footer2.xml"/></Types>')
ct_p.write_text(ct, encoding="utf8")

doc_p = UN / "word/document.xml"
doc = doc_p.read_text(encoding="utf8")
old_sect = re.search(r"<w:sectPr>.*?</w:sectPr>", doc, flags=re.S).group(0)
new_sect = old_sect.replace(
    '<w:headerReference w:type="default" r:id="rId7"/><w:footerReference w:type="default" r:id="rId8"/>',
    '<w:headerReference w:type="default" r:id="rId7"/><w:headerReference w:type="even" r:id="rIdHdrEven"/>'
    '<w:headerReference w:type="first" r:id="rIdHdrFirst"/><w:footerReference w:type="default" r:id="rId8"/>'
    '<w:footerReference w:type="even" r:id="rId8"/><w:footerReference w:type="first" r:id="rIdFtrFirst"/>')
new_sect = new_sect.replace('w:header="560"', 'w:header="620"')
new_sect = new_sect.replace("<w:pgNumType/>", "<w:pgNumType/><w:titlePg/>")
assert new_sect != old_sect
doc = doc.replace(old_sect, new_sect)
doc_p.write_text(doc, encoding="utf8")

# ---------------------------------------------------------------- settings
set_p = UN / "word/settings.xml"
sx = set_p.read_text(encoding="utf8")
sx = sx.replace('<w:evenAndOddHeaders w:val="false"/>',
                '<w:embedTrueTypeFonts/><w:saveSubsetFonts w:val="false"/><w:evenAndOddHeaders/>')
set_p.write_text(sx, encoding="utf8")

# ---------------------------------------------------------------- embed CMU Serif (obfuscated, ECMA-376 17.8.1)
faces = {"Regular": "cmu-serif-500-roman.ttf", "Bold": "cmu-serif-700-roman.ttf",
         "Italic": "cmu-serif-500-italic.ttf", "BoldItalic": "cmu-serif-700-italic.ttf"}
(UN / "word/fonts").mkdir(exist_ok=True)
frels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
embeds = []
for i, (face, fname) in enumerate(faces.items(), 1):
    key = str(uuid.uuid4()).upper()
    hexkey = key.replace("-", "")
    keybytes = bytes(int(hexkey[j:j + 2], 16) for j in range(30, -2, -2))
    data = bytearray((FONTS / fname).read_bytes())
    for j in range(32):
        data[j] ^= keybytes[j % 16]
    (UN / f"word/fonts/font{i}.odttf").write_bytes(bytes(data))
    frels.append(f'<Relationship Id="rIdF{i}" Type="{FNT_T}" Target="fonts/font{i}.odttf"/>')
    embeds.append(f'<w:embed{face} r:id="rIdF{i}" w:fontKey="{{{key}}}"/>')
frels.append("</Relationships>")
(UN / "word/_rels/fontTable.xml.rels").write_text("".join(frels), encoding="utf8")

ft_p = UN / "word/fontTable.xml"
ft = ft_p.read_text(encoding="utf8")
if R_NS not in ft:
    ft = ft.replace("<w:fonts ", f"<w:fonts {R_NS} ", 1)
font_el = (f'<w:font w:name="{FONT}"><w:altName w:val="Latin Modern Roman"/>'
           '<w:panose1 w:val="02000603000000000000"/><w:charset w:val="00"/><w:family w:val="roman"/>'
           '<w:pitch w:val="variable"/>' + "".join(embeds) + '</w:font>'
           '<w:font w:name="Cambria Math"><w:panose1 w:val="02040503050406030204"/><w:charset w:val="00"/>'
           '<w:family w:val="roman"/><w:pitch w:val="variable"/></w:font>'
           '<w:font w:name="Segoe UI Symbol"><w:panose1 w:val="020B0502040204020203"/><w:charset w:val="00"/>'
           '<w:family w:val="swiss"/><w:pitch w:val="variable"/></w:font>')
if re.search(r"/>\s*$", ft) and "</w:fonts>" not in ft:
    ft = re.sub(r"/>\s*$", ">" + font_el + "</w:fonts>", ft)
else:
    ft = re.sub(r"</w:fonts>\s*$", font_el + "</w:fonts>", ft)
ft_p.write_text(ft, encoding="utf8")
print("finished")
