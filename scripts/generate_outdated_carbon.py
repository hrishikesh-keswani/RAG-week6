"""Generate the planted outdated Carbon Reduction Plan (v1.0, 2023)."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parents[1] / "documents" / "Carbon_Old_2050.pdf"

NAVY = HexColor("#0B3D5C")
TEAL = HexColor("#1B6B73")
RULE = HexColor("#C5D4DC")
AMBER = HexColor("#8A5A00")
AMBER_BG = HexColor("#FFF4D6")
ROW = HexColor("#F4F8FA")


def styles():
    base = getSampleStyleSheet()
    return {
        "banner": ParagraphStyle(
            "banner",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=AMBER,
            leading=12,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=HexColor("#333333"),
            leading=14,
            spaceAfter=2,
        ),
        "h": ParagraphStyle(
            "h",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=TEAL,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13.5,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13.5,
            leftIndent=14,
            spaceAfter=3,
        ),
        "th": ParagraphStyle(
            "th",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=HexColor("#FFFFFF"),
        ),
        "td": ParagraphStyle(
            "td",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=HexColor("#666666"),
        ),
    }


def table(header, rows, col_widths):
    s = styles()
    data = [[Paragraph(h, s["th"]) for h in header]]
    for row in rows:
        data.append([Paragraph(c, s["td"]) for c in row])
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
                ("BACKGROUND", (0, 1), (-1, -1), ROW),
                ("GRID", (0, 0), (-1, -1), 0.4, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def story():
    s = styles()
    w = 170 * mm
    elems = [
        Paragraph(
            "DOCUMENT STATUS: SUPERSEDED &nbsp;&nbsp;|&nbsp;&nbsp; "
            "Version 1.0 &nbsp;&nbsp;|&nbsp;&nbsp; Effective 12 March 2023 "
            "&nbsp;&nbsp;|&nbsp;&nbsp; Replaced by Carbon Reduction Plan dated "
            "10 October 2025",
            s["banner"],
        ),
        Spacer(1, 8),
        Paragraph("Carbon Reduction Plan (v1.0, superseded)", s["title"]),
        Paragraph(
            "<b>Supplier name:</b> Coforge Limited &amp; All International "
            "Locations (including Coforge U.K Limited)",
            s["meta"],
        ),
        Paragraph("<b>Publication date:</b> 12 March 2023", s["meta"]),
        Paragraph("<b>Document ID:</b> CARBON-POL-2023-V1.0", s["meta"]),
        Paragraph(
            "<i>This version remains in the policy archive. A later plan "
            "was issued in October 2025. Do not treat this copy as the "
            "current commitment unless a later document is unavailable.</i>",
            s["meta"],
        ),
        Paragraph("Commitment to Achieving Net Zero", s["h"]),
        Paragraph(
            "Coforge Limited and other Global Business Operations, including "
            "Coforge U.K. Limited are committed to achieve Net Zero emission "
            "<b>by 2050</b>. Coforge U.K. Limited is a wholly owned subsidiary "
            "of Coforge Limited.",
            s["body"],
        ),
        Paragraph("Baseline Emissions Footprint", s["h"]),
        Paragraph(
            "Baseline emissions are a record of the greenhouse gases that "
            "have been produced in the past and were produced prior to the "
            "introduction of any strategies to reduce emissions. Baseline "
            "emissions are the reference point against which emissions "
            "reduction can be measured.",
            s["body"],
        ),
        Paragraph(
            "<b>Baseline Year: 2023–2024 (India operations)</b>", s["body"]
        ),
        Paragraph(
            "The baseline emission calculations were done for our operations "
            "in India which is the most significant part of the business. We "
            "have already taken significant initiatives to reduce the carbon "
            "footprint and continue the process.",
            s["body"],
        ),
        Paragraph(
            "Baseline year emissions – Total (tCO2e) – FY24", s["body"]
        ),
        table(
            ["EMISSIONS", "India"],
            [
                ["Scope 1", "413"],
                ["Scope 2", "8,688"],
                ["Scope 3", "5,543"],
                ["Total emissions", "14,644"],
            ],
            [w * 0.55, w * 0.45],
        ),
        Spacer(1, 8),
        Paragraph(
            "<b>Baseline Year: 2023–2024 (UK operations)</b>", s["body"]
        ),
        Paragraph(
            "Coforge is committed to demonstrate strong green credentials and "
            "achieve net zero emissions in years to come. In comparison to "
            "India operations, international business operations are smaller, "
            "and headcount is significantly lower.",
            s["body"],
        ),
        Paragraph(
            "To support our carbon footprint management journey, we have "
            "partnered with \"Carbon Footprint\" who have comprehensive "
            "experience in this area. From 2022, all international business "
            "operations (outside India) are included in carbon emissions "
            "assessment calculations. The baseline assessment undertaken "
            "follows the principles outlined by the Greenhouse Gas Protocol "
            "and the UK Government's Guidelines on Greenhouse Gas reporting.",
            s["body"],
        ),
        Paragraph("Baseline year emissions: FY24 Total (tCO2e)", s["body"]),
        table(
            ["EMISSIONS", "UK"],
            [
                ["Scope 1", "0*"],
                ["Scope 2", "22.38"],
                ["Scope 3", "892.00"],
                ["Total emissions", "914.38"],
            ],
            [w * 0.55, w * 0.45],
        ),
        Spacer(1, 6),
        Paragraph(
            "*There is no Scope 1 (Direct) emission in the UK as no offices "
            "in these locations use natural gas, oil, LPG or have any owned "
            "vehicles.",
            s["body"],
        ),
        Paragraph("Current year emissions: FY25", s["h"]),
        Paragraph(
            "Reporting Year: 1 April 2024 – 31 March 2025", s["body"]
        ),
        table(
            ["EMISSIONS", "India", "UK"],
            [
                ["Scope 1", "1,265", "0*"],
                ["Scope 2", "6,344", "2.90"],
                ["Scope 3", "29,836", "850.05"],
                ["Total emissions", "37,445", "852.95"],
            ],
            [w * 0.4, w * 0.3, w * 0.3],
        ),
        Spacer(1, 6),
        Paragraph(
            "*There is no Scope 1 (Direct) related emission in the UK as no "
            "offices in these locations use natural gas, oil, LPG or have any "
            "owned vehicles. Only potential source of emission is backup "
            "diesel generators. However, we reported no emissions as they "
            "have not been used. India has approximately 20,000 people "
            "across multiple campuses and constitutes lion’s share of our "
            "employees and therefore, is the biggest emissions contributor.",
            s["body"],
        ),
        Paragraph("Emissions Reduction Targets", s["h"]),
        Paragraph(
            "Coforge is a fast-growing IT services firm, and the business has "
            "grown over 100% in the past 4 years. The growth in the business "
            "has led to an increase in headcount and operations across the "
            "globe. As an organisation, we acknowledge that this could lead "
            "to increase in absolute emissions, directly proportionate to the "
            "increase in headcount and business operations. However, as an "
            "organisation, we are committed to assessing our carbon emissions "
            "and target to have zero carbon emissions <b>by 2050</b>.",
            s["body"],
        ),
        Paragraph(
            "We aim to achieve our target by taking active steps through "
            "carbon sequestration and use of renewable energy technologies, "
            "such as solar.",
            s["body"],
        ),
        Paragraph(
            "<b>India location</b> – Since FY24, when the baseline emissions "
            "were assessed, there has been a continuous focus on emission "
            "reduction and focused interventions to ensure that the scope of "
            "emissions is controlled despite the growth of our business "
            "operations. Several of our pilot carbon reduction initiatives "
            "were conducted in our India operations.",
            s["body"],
        ),
        Paragraph(
            "<b>International locations (including the UK)</b> – In 2022, we "
            "conducted emission assessment for all international business "
            "operations, including the UK. We are looking to undertake "
            "multiple initiatives to control these emissions, such as "
            "reducing the need for air-travel where possible, given that it "
            "is a significant contributor to our emissions for international "
            "locations. We are continually assessing our operations for "
            "consolidation of resources to reduce the negative impact on the "
            "environment.",
            s["body"],
        ),
        Paragraph("Carbon Reduction Initiatives", s["h"]),
        Paragraph(
            "In alignment with our goal to be “net-zero by 2050”, we have "
            "undertaken the following initiatives and are actively "
            "integrating carbon reduction plans in our global operations:",
            s["body"],
        ),
        Paragraph(
            "1. Coforge has obtained certain global certifications that allow "
            "us to reduce our overall carbon emissions across our operations:",
            s["body"],
        ),
        Paragraph(
            "• Environment, Health, and Safety Management System has been "
            "implemented in conformance to ISO 14001:2015 and ISO 45001:2018 "
            "standards.",
            s["bullet"],
        ),
        Paragraph(
            "• Coforge owns USGBC (US Green Building Council)-rated Platinum "
            "green campuses.",
            s["bullet"],
        ),
        Paragraph(
            "2. We are committed to the utilization of clean fuel and a "
            "transition to renewable energy in our operations. This covers a "
            "wide variety of our operations, including transportation, "
            "cafeteria operations and electricity consumption.",
            s["body"],
        ),
        Paragraph(
            "• 100% conversion of company cabs and buses to Compressed "
            "Natural Gas (CNG).",
            s["bullet"],
        ),
        Paragraph(
            "• Introduce electric vehicle fleets (for employees’ transport "
            "system) and target <b>5% integration by 2028 and ~25% by "
            "2032</b>.",
            s["bullet"],
        ),
        Paragraph(
            "• 100% utilization of Piped Natural Gas (PNG) in cafeteria "
            "operations.",
            s["bullet"],
        ),
        Paragraph(
            "• Procure <b>5% green energy</b>, contributing to total energy "
            "consumption <b>by 2025</b> and achieve <b>~25% by 2030</b>.",
            s["bullet"],
        ),
        Paragraph(
            "• Support transition to 100% renewable energy <b>by 2050</b> by "
            "committing to the RE100 global initiative. Through this, we "
            "pledge to have 100% of our electricity sourced from renewable "
            "sources.",
            s["bullet"],
        ),
        Paragraph(
            "• Engage in community programs to generate renewable energy.",
            s["bullet"],
        ),
        Paragraph(
            "3. Coforge has also committed to interventions with relation to "
            "sustainable building and energy management initiatives in our "
            "operations. We have undertaken several pilot initiatives at our "
            "main campus in India, including the following:",
            s["body"],
        ),
        Paragraph(
            "• Passive solar architecture for provision of natural day "
            "lighting in the building.",
            s["bullet"],
        ),
        Paragraph(
            "• Use of double-glazed, high efficiency reflective glass to "
            "reduce the solar heat gain by 8% to 10%.",
            s["bullet"],
        ),
        Paragraph(
            "• Rooftop solar energy generation system of 75 KWp and "
            "solar-based external area lighting systems to reduce the "
            "consumption of power grid.",
            s["bullet"],
        ),
        Paragraph(
            "• Sensor-based lighting system to optimize energy efficiency.",
            s["bullet"],
        ),
        Paragraph(
            "• Use of low embodied building material in construction, i.e., "
            "fly ash bricks, to reduce the overall carbon footprint of the "
            "building.",
            s["bullet"],
        ),
        Paragraph(
            "• Use of LEDs as replacement of T-5 and LCDs to reduce "
            "electricity consumption.",
            s["bullet"],
        ),
        Paragraph("• Solar water heating system in cafeteria.", s["bullet"]),
        Paragraph(
            "4. We aim to improve employee engagement and awareness on "
            "sustainability and energy efficiency. We are taking the "
            "following steps for the same:",
            s["body"],
        ),
        Paragraph(
            "• Conduct one mandatory and two voluntary training sessions "
            "annually for all employees to foster a culture of "
            "sustainability.",
            s["bullet"],
        ),
        Paragraph(
            "• Empower employees with knowledge and skills to implement "
            "energy-saving practices and reduce carbon footprint through "
            "education and incentive programs.",
            s["bullet"],
        ),
        Paragraph(
            "Coforge has already implemented several of these carbon "
            "reduction initiatives at our India locations and is actively "
            "integrating these in our UK operations as well. In addition to "
            "the above initiatives, at UK premise, Coforge adheres with Waste "
            "Electrical and Electronic Equipment (WEEE) compliance standards, "
            "which ensures that Coforge responsibly manages electronic waste, "
            "promotes recycling, and follows proper disposal methods for "
            "electronic equipment, thus reducing its carbon footprint and "
            "environmental impact.",
            s["body"],
        ),
        Paragraph("Declaration and Sign Off", s["h"]),
        Paragraph(
            "This Carbon Reduction Plan has been completed in accordance with "
            "PPN 06/21 and associated guidance and reporting standard for "
            "Carbon Reduction Plans. Emissions have been reported and "
            "recorded in accordance with the published reporting standard for "
            "Carbon Reduction Plans and the GHG Reporting Protocol corporate "
            "standard and uses the appropriate Government emission conversion "
            "factors for greenhouse gas company reporting.",
            s["body"],
        ),
        Paragraph(
            "Scope 1 and Scope 2 emissions have been reported in accordance "
            "with SECR requirements, and the required subset of Scope 3 "
            "emissions have been reported in accordance with the published "
            "reporting standard for Carbon Reduction Plans and the Corporate "
            "Value Chain (Scope 3) Standard.",
            s["body"],
        ),
        Paragraph(
            "This Carbon Reduction Plan has been reviewed and signed off by "
            "the board of directors (or equivalent management body).",
            s["body"],
        ),
        Paragraph(
            "<b>Signed on behalf of the Supplier:</b><br/>John Speight<br/>"
            "President and Head of Europe (EVP)",
            s["body"],
        ),
    ]
    return elems


def add_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AMBER_BG)
    canvas.rect(0, A4[1] - 16 * mm, A4[0], 16 * mm, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(
        18 * mm,
        A4[1] - 10 * mm,
        "SUPERSEDED  |  Carbon Reduction Plan v1.0  |  12 March 2023  |  "
        "Net Zero target in this copy: 2050",
    )
    canvas.setStrokeColor(RULE)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFillColor(HexColor("#666666"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 9 * mm, "Coforge Limited  |  CARBON-POL-2023-V1.0")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="Carbon Reduction Plan (v1.0, superseded)",
        author="Coforge Limited",
        subject="Outdated carbon policy planted for RAG data-quality lab",
    )
    doc.build(story(), onFirstPage=add_page, onLaterPages=add_page)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
