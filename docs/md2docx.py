#!/usr/bin/env python3
"""마크다운 -> docx 변환기 (표준 라이브러리만 사용).

제목/문단/불릿/번호목록/코드블록/인용/표/구분선/체크박스와
인라인 **굵게**, `코드`를 지원한다.
"""
import re
import sys
import zipfile
from xml.sax.saxutils import escape

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""


def core_props(title):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>{escape(title)}</dc:title><cp:revision>1</cp:revision>
</cp:coreProperties>"""


APP_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>Markdown Converter</Application>
</Properties>"""


def _font(latin, ea, size_half, color=None, bold=False):
    c = f'<w:color w:val="{color}"/>' if color else ""
    b = "<w:b/>" if bold else ""
    return (
        f'<w:rPr><w:rFonts w:ascii="{latin}" w:hAnsi="{latin}" w:eastAsia="{ea}" w:cs="{latin}"/>'
        f'{b}{c}<w:sz w:val="{size_half}"/><w:szCs w:val="{size_half}"/></w:rPr>'
    )


BODY_LATIN, BODY_EA, MONO = "Calibri", "맑은 고딕", "Consolas"

STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="{BODY_LATIN}" w:hAnsi="{BODY_LATIN}" w:eastAsia="{BODY_EA}" w:cs="{BODY_LATIN}"/>
<w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="288" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>

<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/><w:qFormat/></w:style>

<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:before="0" w:after="360"/></w:pPr>
{_font(BODY_LATIN, BODY_EA, 56, "1A1A1A", True)}</w:style>

<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="480" w:after="200"/>
<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="6" w:color="D0D0D0"/></w:pBdr></w:pPr>
{_font(BODY_LATIN, BODY_EA, 34, "1A1A1A", True)}</w:style>

<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="360" w:after="160"/></w:pPr>
{_font(BODY_LATIN, BODY_EA, 27, "2A2A2A", True)}</w:style>

<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:outlineLvl w:val="2"/><w:spacing w:before="280" w:after="120"/></w:pPr>
{_font(BODY_LATIN, BODY_EA, 24, "3A3A3A", True)}</w:style>

<w:style w:type="paragraph" w:styleId="CodeBlock"><w:name w:val="Code Block"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:shd w:val="clear" w:fill="F4F4F6"/><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>
<w:ind w:left="240" w:right="240"/></w:pPr>
{_font(MONO, MONO, 18, "1F2328")}</w:style>

<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:ind w:left="360"/>
<w:pBdr><w:left w:val="single" w:sz="18" w:space="10" w:color="B8B8C0"/></w:pBdr></w:pPr>
{_font(BODY_LATIN, BODY_EA, 21, "4A4A55")}</w:style>

<w:style w:type="character" w:styleId="InlineCode"><w:name w:val="Inline Code"/><w:qFormat/>
{_font(MONO, MONO, 19, "B31D28")}</w:style>

<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr><w:spacing w:after="60"/></w:pPr></w:style>

<w:style w:type="paragraph" w:styleId="ListNumber"><w:name w:val="List Number"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr><w:spacing w:after="60"/></w:pPr></w:style>

<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>
<w:tblPr><w:tblBorders>
<w:top w:val="single" w:sz="4" w:color="C8C8CE"/><w:left w:val="single" w:sz="4" w:color="C8C8CE"/>
<w:bottom w:val="single" w:sz="4" w:color="C8C8CE"/><w:right w:val="single" w:sz="4" w:color="C8C8CE"/>
<w:insideH w:val="single" w:sz="4" w:color="C8C8CE"/><w:insideV w:val="single" w:sz="4" w:color="C8C8CE"/>
</w:tblBorders></w:tblPr></w:style>
</w:styles>"""

NUMBERING = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {NS}>
<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/>
<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="420" w:hanging="240"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr></w:lvl>
<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="◦"/>
<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="840" w:hanging="240"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr></w:lvl>
</w:abstractNum>
<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/>
<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="420" w:hanging="300"/></w:pPr></w:lvl>
</w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
<w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>"""


# ---------- 인라인 파싱 ----------
INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|~~.+?~~)")


def runs(text, base_bold=False):
    """인라인 서식을 <w:r> 시퀀스로 변환."""
    out = []
    for part in INLINE_RE.split(text):
        if not part:
            continue
        bold, code, strike = base_bold, False, False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            inner = part[2:-2]
            if "`" in inner:  # 굵게 안의 인라인 코드는 재귀로 처리
                out.append(runs(inner, base_bold=True))
                continue
            part, bold = inner, True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            part, code = part[1:-1], True
        elif part.startswith("~~") and part.endswith("~~") and len(part) > 4:
            part, strike = part[2:-2], True

        rpr = ""
        if code:
            rpr = '<w:rStyle w:val="InlineCode"/>'
        if bold:
            rpr += "<w:b/>"
        if strike:
            rpr += "<w:strike/>"
        rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
        out.append(f'{"<w:r>"}{rpr}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out) or '<w:r><w:t xml:space="preserve"></w:t></w:r>'


def para(text, style=None, bold=False):
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{ppr}{runs(text, bold)}</w:p>"


def hrule():
    return (
        '<w:p><w:pPr><w:spacing w:before="200" w:after="200"/>'
        '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="D8D8DE"/></w:pBdr>'
        "</w:pPr></w:p>"
    )


def table(rows):
    """rows[0]을 헤더로 하는 표 생성."""
    ncol = max(len(r) for r in rows)
    width = 9360 // ncol
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in range(ncol))
    xml = [
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="5000" w:type="pct"/><w:tblLayout w:type="fixed"/></w:tblPr>'
        f"<w:tblGrid>{grid}</w:tblGrid>"
    ]
    for i, row in enumerate(rows):
        cells = []
        for j in range(ncol):
            cell = row[j] if j < len(row) else ""
            shade = '<w:shd w:val="clear" w:fill="F0F0F4"/>' if i == 0 else ""
            cells.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}'
                '<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
                f"{runs(cell, base_bold=(i == 0))}</w:p></w:tc>"
            )
        header = '<w:trPr><w:tblHeader/></w:trPr>' if i == 0 else ""
        xml.append(f"<w:tr>{header}{''.join(cells)}</w:tr>")
    xml.append("</w:tbl>")
    # 표 뒤에는 빈 문단이 있어야 Word가 안정적으로 렌더링한다
    xml.append('<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>')
    return "".join(xml)


# ---------- 블록 파싱 ----------
def convert(md):
    lines = md.split("\n")
    body, i, doc_title = [], 0, "문서"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 코드 블록
        if stripped.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            body.append('<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>')
            for code_line in block:
                safe = escape(code_line.replace("\t", "    "))
                body.append(
                    '<w:p><w:pPr><w:pStyle w:val="CodeBlock"/></w:pPr>'
                    f'<w:r><w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'
                )
            body.append('<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>')
            continue

        # 표
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\|[\s:|-]+\|$", lines[i + 1].strip()
        ):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i].strip().strip("|")
                if not re.match(r"^[\s:|-]+$", raw):
                    rows.append([c.strip() for c in raw.split("|")])
                i += 1
            body.append(table(rows))
            continue

        # 구분선
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            body.append(hrule())
            i += 1
            continue

        # 제목
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            if level == 1 and doc_title == "문서":
                doc_title = re.sub(r"[*`]", "", text)
                body.append(para(text, "Title"))
            else:
                body.append(para(text, f"Heading{min(level if level > 1 else 1, 3)}"))
            i += 1
            continue

        # 인용
        if stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body.append(para(" ".join(q for q in quote if q), "Quote"))
            continue

        # 체크박스 / 불릿 / 번호
        m = re.match(r"^(\s*)[-*]\s+\[([ xX])\]\s+(.*)$", line)
        if m:
            mark = "☑" if m.group(2).lower() == "x" else "☐"
            body.append(para(f"{mark}  {m.group(3)}"))
            i += 1
            continue

        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            body.append(para(m.group(2), "ListBullet"))
            i += 1
            continue

        m = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if m:
            body.append(para(m.group(2), "ListNumber"))
            i += 1
            continue

        # 빈 줄
        if not stripped:
            i += 1
            continue

        # 일반 문단 (연속된 줄을 합침)
        buf = []
        while i < len(lines):
            cur = lines[i].strip()
            if not cur or re.match(r"^(#{1,6}\s|>|\||```|-{3,})", cur) or re.match(
                r"^\s*([-*]\s|\d+\.\s)", lines[i]
            ):
                break
            buf.append(cur)
            i += 1
        body.append(para(" ".join(buf)))

    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f"<w:document {NS}><w:body>{''.join(body)}"
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1418" w:right="1276" w:bottom="1418" w:left="1276" '
        'w:header="851" w:footer="992" w:gutter="0"/></w:sectPr>'
        "</w:body></w:document>"
    )
    return document, doc_title


def main(src, dst):
    with open(src, encoding="utf-8") as f:
        md = f.read()
    document, title = convert(md)

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("docProps/core.xml", core_props(title))
        z.writestr("docProps/app.xml", APP_PROPS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/numbering.xml", NUMBERING)
    print(f"생성 완료: {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
