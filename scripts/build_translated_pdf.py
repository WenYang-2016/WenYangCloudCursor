#!/usr/bin/env python3
"""Build an English translation PDF preserving the original report layout."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, red
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, FrameBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

ROOT = "/workspace"
CROPS = os.path.join(ROOT, "assets", "report_images")
# Prefer workspace assets; fall back to temp crops if needed
if not os.path.isdir(CROPS):
    CROPS = "/tmp/pdf_work/crops"

OUT = os.path.join(ROOT, "output", "TSQR-0586_Wacker_Neuson_Gear_Pump_Analysis_Report_EN.pdf")

# Map final_* names
ASSET = {
    "p1_photos": "final_p1_photos.png",
    "p2_displays": "final_p2_displays.png",
    "p2_nameplate": "final_p2_nameplate.png",
    "p2_wear": "final_p2_wear.png",
    "p2_bore": "final_p2_bore.png",
    "p3_seal": "final_p3_seal.png",
}


def asset(key):
    return os.path.join(CROPS, ASSET[key])

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

RED = HexColor("#C00000")
DARK = HexColor("#1A1A1A")
GRAY = HexColor("#333333")
LINE = HexColor("#000000")


def styles():
    return {
        "title": ParagraphStyle(
            "title", fontName="DejaVuBold", fontSize=16, leading=22,
            alignment=TA_CENTER, textColor=DARK, spaceAfter=6
        ),
        "meta": ParagraphStyle(
            "meta", fontName="DejaVu", fontSize=10, leading=14,
            alignment=TA_CENTER, textColor=GRAY
        ),
        "meta_right": ParagraphStyle(
            "meta_right", fontName="DejaVu", fontSize=10, leading=14,
            alignment=TA_LEFT, textColor=GRAY
        ),
        "addr": ParagraphStyle(
            "addr", fontName="DejaVuBold", fontSize=11, leading=16,
            textColor=DARK, spaceBefore=4, spaceAfter=2
        ),
        "body": ParagraphStyle(
            "body", fontName="DejaVu", fontSize=10, leading=15,
            alignment=TA_JUSTIFY, textColor=DARK, firstLineIndent=0
        ),
        "body_indent": ParagraphStyle(
            "body_indent", fontName="DejaVu", fontSize=10, leading=15,
            alignment=TA_JUSTIFY, textColor=DARK, leftIndent=12
        ),
        "h1": ParagraphStyle(
            "h1", fontName="DejaVuBold", fontSize=11, leading=16,
            textColor=DARK, spaceBefore=10, spaceAfter=4
        ),
        "h1_red": ParagraphStyle(
            "h1_red", fontName="DejaVuBold", fontSize=11, leading=16,
            textColor=RED, spaceBefore=10, spaceAfter=4
        ),
        "item": ParagraphStyle(
            "item", fontName="DejaVu", fontSize=10, leading=15,
            textColor=DARK, leftIndent=8
        ),
        "item_red": ParagraphStyle(
            "item_red", fontName="DejaVu", fontSize=10, leading=15,
            textColor=RED, leftIndent=20
        ),
        "th": ParagraphStyle(
            "th", fontName="DejaVuBold", fontSize=8.5, leading=11,
            alignment=TA_CENTER, textColor=DARK
        ),
        "td": ParagraphStyle(
            "td", fontName="DejaVu", fontSize=8.5, leading=11,
            alignment=TA_CENTER, textColor=DARK
        ),
        "td_left": ParagraphStyle(
            "td_left", fontName="DejaVu", fontSize=8.5, leading=11,
            alignment=TA_LEFT, textColor=DARK
        ),
        "small": ParagraphStyle(
            "small", fontName="DejaVu", fontSize=9.5, leading=13,
            textColor=DARK
        ),
        "closing": ParagraphStyle(
            "closing", fontName="DejaVu", fontSize=11, leading=16,
            textColor=DARK, spaceBefore=14
        ),
    }


def table_style():
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.7, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F5F5F5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def img(path, max_w=None, max_h=None):
    im = Image(path)
    iw, ih = im.imageWidth, im.imageHeight
    if max_w and max_h:
        scale = min(max_w / iw, max_h / ih)
        im.drawWidth = iw * scale
        im.drawHeight = ih * scale
    elif max_w:
        scale = max_w / iw
        im.drawWidth = max_w
        im.drawHeight = ih * scale
    elif max_h:
        scale = max_h / ih
        im.drawHeight = max_h
        im.drawWidth = iw * scale
    return im


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    S = styles()
    content_w = PAGE_W - 2 * MARGIN

    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Analysis Report on Wacker Neuson Gear Pump (TSQR-0586)",
        author="Tianjin Shimadzu Hydraulic Co., Ltd. / Quality Assurance Dept.",
    )

    story = []

    # ---- Page 1 header ----
    story.append(Paragraph("Analysis Report on Wacker Neuson Gear Pump", S["title"]))
    story.append(Paragraph("TSQR-0586", S["meta"]))
    story.append(Paragraph("2026-6-29", S["meta"]))

    meta_tbl = Table(
        [[
            Paragraph("Prepared by: Wang Kuan", S["meta_right"]),
            Paragraph("Approved by:", S["meta_right"]),
        ]],
        colWidths=[content_w * 0.55, content_w * 0.45],
    )
    meta_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 40),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Wacker Neuson Company:", S["addr"]))
    story.append(Paragraph(
        'Customer feedback failure mode: <u>Gear pump oil leakage</u>',
        S["body"]
    ))
    story.append(Spacer(1, 4))

    # Product photos
    photos = img(asset("p1_photos"), max_w=content_w * 0.92, max_h=42 * mm)
    photo_wrap = Table([[photos]], colWidths=[content_w])
    photo_wrap.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(photo_wrap)

    story.append(Paragraph("I. Background Overview", S["h1"]))
    story.append(Paragraph(
        "Our company received feedback from your company that this gear pump exhibited an oil "
        "leakage failure. To identify the root cause, we conducted a systematic inspection and "
        "analysis of the returned unit immediately upon receipt. After preliminary visual "
        "inspection and performance retests, the results were found to differ significantly "
        "from the failure reported by the customer. Details are as follows.",
        S["body"]
    ))

    story.append(Paragraph("II. Inspection Methods and Process", S["h1"]))
    story.append(Paragraph(
        "1. Preliminary visual inspection: Checked the pump body surface for obvious impact "
        "damage, sand holes, or scratches on seals and mating/joint faces.",
        S["item"]
    ))
    story.append(Paragraph(
        "<u>Abnormal eccentric wear marks were found on the mounting pilot (spigot).</u>",
        S["item_red"]
    ))
    story.append(Paragraph(
        "2. Airtightness test (core reproduction item): Performed in accordance with the "
        "standard work instruction. Observation: no abnormal condition.",
        S["item"]
    ))
    story.append(Paragraph(
        "3. Performance retest: Retested under rated pressure to measure the output flow "
        "of this gear pump.",
        S["item"]
    ))

    story.append(Paragraph("III. Inspection Results and Data Analysis", S["h1_red"]))

    t1 = Table(
        [
            [
                Paragraph("Inspection Item", S["th"]),
                Paragraph("Standard / Requirement", S["th"]),
                Paragraph("Retest Actual Result", S["th"]),
                Paragraph("Conclusion", S["th"]),
            ],
            [
                Paragraph("Airtightness<br/>(oil-leak reproduction)", S["td"]),
                Paragraph("Extended pressure hold<br/>3 min, no leakage", S["td"]),
                Paragraph("No leak point found<br/>(hold pressure stable,<br/>no pressure drop)", S["td"]),
                Paragraph('Inconsistent with<br/>customer feedback<br/>“oil leakage”', S["td"]),
            ],
        ],
        colWidths=[content_w * 0.22, content_w * 0.24, content_w * 0.30, content_w * 0.24],
    )
    t1.setStyle(table_style())
    story.append(t1)

    # ---- Page 2 (matches original page break after airtightness table) ----
    story.append(PageBreak())
    t2 = Table(
        [
            [
                Paragraph("Inspection Item", S["th"]),
                Paragraph("Standard / Requirement", S["th"]),
                Paragraph("Retest Actual Result", S["th"]),
                Paragraph("Conclusion", S["th"]),
            ],
            [
                Paragraph("Flow confirmation", S["td"]),
                Paragraph("19.2–21.4 L/min", S["td"]),
                Paragraph("Essentially no flow", S["td"]),
                Paragraph("Unqualified", S["td"]),
            ],
        ],
        colWidths=[content_w * 0.22, content_w * 0.24, content_w * 0.30, content_w * 0.24],
    )
    t2.setStyle(table_style())
    story.append(t2)
    story.append(Spacer(1, 8))

    story.append(Paragraph("On-site test status:", S["h1"]))

    left_status = [
        Paragraph("<b>Test-bench flow confirmation:</b>", S["small"]),
        Spacer(1, 4),
        Paragraph(
            "This gear pump cannot meet the test condition: <b>17.2 MPa</b>",
            S["small"]
        ),
        Spacer(1, 4),
        Paragraph(
            "→ The factory test bench can no longer build/load pressure.",
            S["small"]
        ),
    ]
    disp = img(asset("p2_displays"), max_w=55 * mm, max_h=70 * mm)
    status_tbl = Table(
        [[left_status, disp]],
        colWidths=[content_w * 0.55, content_w * 0.45],
    )
    status_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(status_tbl)

    story.append(Paragraph("Analysis of key contradiction:", S["h1"]))
    story.append(Paragraph(
        'Retest results show that the <u>flow rate is significantly lower than the rated value</u>.',
        S["body"]
    ))

    story.append(Paragraph("IV. Disassembly Analysis", S["h1"]))

    np_img = img(asset("p2_nameplate"), max_w=48 * mm, max_h=28 * mm)
    wear_img = img(asset("p2_wear"), max_w=48 * mm, max_h=28 * mm)
    bore_img = img(asset("p2_bore"), max_w=48 * mm, max_h=32 * mm)

    desc1 = Paragraph(
        "<b>Nameplate information:</b><br/>"
        "Model: SGP1-R9647D (15CC)<br/>"
        "Production date: Oct 2025<br/>"
        "Product No.: 04801",
        S["td_left"]
    )
    desc2 = Paragraph("Eccentric wear marks on the mounting pilot (spigot)", S["td_left"])
    desc3 = Paragraph(
        "Gear pump disassembled; secondary bore sweeping of the intermediate body → internal leakage",
        S["td_left"]
    )

    disasm = Table(
        [
            [
                Paragraph("No.", S["th"]),
                Paragraph("Returned Product Condition", S["th"]),
                Paragraph("Description", S["th"]),
            ],
            [Paragraph("1", S["td"]), np_img, desc1],
            [Paragraph("2", S["td"]), wear_img, desc2],
            [Paragraph("3", S["td"]), bore_img, desc3],
        ],
        colWidths=[content_w * 0.08, content_w * 0.40, content_w * 0.52],
    )
    disasm.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.7, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F5F5F5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(disasm)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This indicates severe internal leakage (internal leak) wear inside the pump. "
        "However, the airtightness test did not find external leakage (external leak).",
        S["body"]
    ))

    # ---- Page 3 (matches original) ----
    story.append(PageBreak())
    # Original document numbers this section as 四 again; keep original numbering.
    story.append(Paragraph(
        "IV. Analysis of Reasons for Discrepancy Between Failure Symptoms and Test Results",
        S["h1"]
    ))
    story.append(Paragraph(
        'Based on the contradictory phenomenon of “low flow but no external leakage” above, '
        "our analysis is as follows:",
        S["body"]
    ))
    story.append(Paragraph(
        "1. Differences exist between the failure operating conditions and the static test "
        "→ no oil-leakage phenomenon observed.",
        S["item"]
    ))
    story.append(Paragraph(
        "2. Root-cause inference (key point): Severely low flow without external leakage is "
        "typical of internal pump wear. Eccentric wear marks on the mounting pilot suggest "
        "the gear pump was subjected to radial force, causing secondary internal bore sweeping, "
        "which resulted in “no flow” during the return-to-factory test.",
        S["item"]
    ))
    story.append(Paragraph(
        "3. The “oil leakage” reported by your company may involve “misjudgment” or other “causes.”",
        S["item"]
    ))

    story.append(Paragraph("V. Conclusion", S["h1"]))
    story.append(Paragraph(
        "1. Current product status: Per our retest, the pump’s airtightness is currently "
        "qualified (no external leakage), but performance (flow) is unqualified.",
        S["item"]
    ))
    story.append(Paragraph(
        "2. Consistency with customer feedback: The current product status (low flow) is "
        "completely inconsistent with your company’s earlier feedback that “no abnormal "
        "operating conditions were found.” The customer’s statement of “no abnormal conditions” "
        "while claiming oil leakage is logically contradictory to the “severe internal leakage "
        "(insufficient performance)” measured by us.",
        S["item"]
    ))
    story.append(Paragraph(
        "3. Recommended judgment: Field misjudgment or inaccurate description of operating "
        "conditions cannot be ruled out. The fundamental failure mode of this pump is caused "
        "by internal wear, rather than simple external seal failure alone.",
        S["item"]
    ))

    story.append(Paragraph("The above concludes this report.", S["closing"]))
    story.append(Paragraph("Best regards,", S["closing"]))
    story.append(Spacer(1, 8))

    # Company seal (preserve original stamp image)
    seal = img(asset("p3_seal"), max_w=38 * mm, max_h=38 * mm)
    seal_note = Paragraph(
        "<font size='8' color='#666666'>Tianjin Shimadzu Hydraulic Co., Ltd.<br/>"
        "Quality Assurance Department</font>",
        S["meta"]
    )
    seal_tbl = Table(
        [["", [seal, seal_note]]],
        colWidths=[content_w * 0.55, content_w * 0.45],
    )
    seal_tbl.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(seal_tbl)

    def on_page(c: canvas.Canvas, doc_):
        c.saveState()
        c.setFont("DejaVu", 8)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(PAGE_W / 2, 10 * mm, f"{doc_.page} / 3")
        c.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
