"""
Debtrex Solutions — Setup Guide PDF Builder
Generates a professional setup guide for the Debtrex Solutions website.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.flowables import HRFlowable, Flowable
from reportlab.pdfgen import canvas

OUTPUT = r"C:\Users\Polix\OneDrive\Desktop\DETREX SOLUTIONS\Debtrex_Setup_Guide.pdf"

# === BRAND COLORS ===
NAVY = HexColor("#0B2545")
NAVY_DEEP = HexColor("#061734")
GREEN = HexColor("#13A66B")
GREEN_DARK = HexColor("#0E8856")
GREEN_SOFT = HexColor("#E6F6EE")
BG = HexColor("#F7F9FC")
BG_MUTED = HexColor("#EEF2F7")
TEXT = HexColor("#1A2B49")
TEXT_MUTED = HexColor("#5C6B85")
BORDER = HexColor("#E2E8F0")
WARN_BG = HexColor("#FFF4E5")
WARN = HexColor("#B85C00")
CODE_BG = HexColor("#0F1B2E")
CODE_FG = HexColor("#E6F1FF")

# === STYLES ===
styles = getSampleStyleSheet()

def s(name, **kw):
    base = {"name": name, "fontName": "Helvetica", "fontSize": 11, "leading": 16, "textColor": TEXT}
    base.update(kw)
    return ParagraphStyle(**base)

S_TITLE = s("DTitle", fontName="Helvetica-Bold", fontSize=34, leading=40, textColor=white, alignment=TA_LEFT)
S_SUBTITLE = s("DSubtitle", fontName="Helvetica", fontSize=16, leading=22, textColor=HexColor("#B7D5FF"), alignment=TA_LEFT)
S_COVER_META = s("DCoverMeta", fontName="Helvetica", fontSize=11, leading=16, textColor=HexColor("#94B1D3"), alignment=TA_LEFT)
S_H1 = s("DH1", fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=NAVY, spaceBefore=4, spaceAfter=10)
S_H2 = s("DH2", fontName="Helvetica-Bold", fontSize=15, leading=20, textColor=NAVY, spaceBefore=16, spaceAfter=8)
S_H3 = s("DH3", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=6)
S_BODY = s("DBody", fontSize=10.5, leading=15.5, alignment=TA_LEFT, spaceAfter=8)
S_BODY_JUST = s("DBodyJ", fontSize=10.5, leading=15.5, alignment=TA_JUSTIFY, spaceAfter=8)
S_BULLET = s("DBullet", fontSize=10.5, leading=15, spaceAfter=4)
S_CODE = s("DCode", fontName="Courier", fontSize=9, leading=13, textColor=CODE_FG, alignment=TA_LEFT)
S_CALLOUT = s("DCallout", fontSize=10, leading=14.5, textColor=WARN, spaceBefore=2, spaceAfter=2)
S_CALLOUT_TITLE = s("DCalloutTitle", fontName="Helvetica-Bold", fontSize=10.5, leading=14.5, textColor=WARN)
S_TOC = s("DTOC", fontSize=10.5, leading=18)
S_TOC_NUM = s("DTOCNum", fontName="Helvetica-Bold", fontSize=10.5, leading=18, textColor=GREEN_DARK)
S_FOOT = s("DFoot", fontSize=8.5, leading=12, textColor=TEXT_MUTED)
S_CHIP = s("DChip", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=white, alignment=TA_CENTER)
S_PAGEHEAD = s("DPageHead", fontSize=8.5, leading=11, textColor=TEXT_MUTED, alignment=TA_LEFT)


# === PAGE TEMPLATE (header/footer) ===
def header_footer(canv, doc):
    canv.saveState()
    # Header band
    if doc.page > 1:
        canv.setFillColor(BG)
        canv.rect(0, LETTER[1] - 0.55*inch, LETTER[0], 0.55*inch, fill=1, stroke=0)
        canv.setFillColor(NAVY)
        canv.setFont("Helvetica-Bold", 10.5)
        canv.drawString(0.6*inch, LETTER[1] - 0.32*inch, "Debtrex Solutions")
        canv.setFillColor(TEXT_MUTED)
        canv.setFont("Helvetica", 9)
        canv.drawString(0.6*inch, LETTER[1] - 0.46*inch, "Website Setup & Deployment Guide")
        # Brand mark
        canv.setFillColor(NAVY)
        canv.roundRect(LETTER[0] - 0.85*inch, LETTER[1] - 0.42*inch, 0.25*inch, 0.25*inch, 4, fill=1, stroke=0)
        canv.setFillColor(GREEN)
        canv.roundRect(LETTER[0] - 0.78*inch, LETTER[1] - 0.36*inch, 0.13*inch, 0.13*inch, 2, fill=1, stroke=0)
        # Divider
        canv.setStrokeColor(BORDER)
        canv.setLineWidth(0.5)
        canv.line(0.6*inch, LETTER[1] - 0.58*inch, LETTER[0] - 0.6*inch, LETTER[1] - 0.58*inch)

    # Footer
    canv.setFillColor(TEXT_MUTED)
    canv.setFont("Helvetica", 8.5)
    canv.drawString(0.6*inch, 0.4*inch, "© 2026 Debtrex Solutions LLC — Internal Setup Documentation")
    canv.drawRightString(LETTER[0] - 0.6*inch, 0.4*inch, f"Page {doc.page}")
    canv.restoreState()


# === CUSTOM FLOWABLES ===
class CodeBlock(Flowable):
    """Dark code block with monospace text."""
    def __init__(self, code, width=None):
        super().__init__()
        self.code = code
        self.lines = code.split("\n")
        self.line_height = 13
        self.padding = 12
        self.width = width or 6.7*inch
        self.height = len(self.lines) * self.line_height + self.padding * 2

    def draw(self):
        c = self.canv
        c.setFillColor(CODE_BG)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        c.setFillColor(CODE_FG)
        c.setFont("Courier", 9)
        y = self.height - self.padding - 9
        for line in self.lines:
            c.drawString(self.padding, y, line)
            y -= self.line_height


class Callout(Flowable):
    """Warning / info callout box."""
    def __init__(self, title, body, kind="warn", width=None):
        super().__init__()
        self.title = title
        self.body = body
        self.kind = kind
        self.width = width or 6.7*inch
        self.padding = 14
        # Approx height (single-flow rendering)
        self._title_h = 14
        self._body_lines = self._wrap(body, 90)
        self._body_h = len(self._body_lines) * 13
        self.height = self.padding * 2 + self._title_h + 6 + self._body_h

    def _wrap(self, text, width):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= width:
                cur = (cur + " " + w).strip()
            else:
                lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

    def draw(self):
        c = self.canv
        bg = WARN_BG if self.kind == "warn" else GREEN_SOFT
        border = HexColor("#F1D6A8") if self.kind == "warn" else HexColor("#B7E1C8")
        accent = WARN if self.kind == "warn" else GREEN_DARK

        c.setFillColor(bg)
        c.setStrokeColor(border)
        c.setLineWidth(1)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        # Left accent bar
        c.setFillColor(accent)
        c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        # Title
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 10.5)
        y = self.height - self.padding - 4
        c.drawString(self.padding + 4, y, self.title)
        # Body
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 10)
        y -= 18
        for line in self._body_lines:
            c.drawString(self.padding + 4, y, line)
            y -= 13


class Divider(Flowable):
    def __init__(self, width=None, color=BORDER, thickness=0.5, space=10):
        super().__init__()
        self.width = width or 6.7*inch
        self.color = color
        self.thickness = thickness
        self.height = space * 2
        self.space = space
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space, self.width, self.space)


class SectionNumber(Flowable):
    """Chip showing 'Section N' beside the heading."""
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.width = 1.4*inch
        self.height = 22
    def draw(self):
        c = self.canv
        c.setFillColor(GREEN_SOFT)
        c.roundRect(0, 0, 1.0*inch, 18, 9, fill=1, stroke=0)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(10, 5, f"SECTION {self.n}")


# === COVER PAGE (drawn directly on canvas via onFirstPage) ===
def draw_cover(c, doc):
    # Navy background
    c.setFillColor(NAVY_DEEP)
    c.rect(0, 0, LETTER[0], LETTER[1], fill=1, stroke=0)
    # Green accent corner
    c.setFillColor(GREEN)
    c.rect(0, LETTER[1] - 0.35*inch, LETTER[0], 0.35*inch, fill=1, stroke=0)
    # Brand mark
    c.setFillColor(white)
    c.roundRect(0.6*inch, LETTER[1] - 1.5*inch, 0.55*inch, 0.55*inch, 8, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.74*inch, LETTER[1] - 1.32*inch, "D")
    # Brand text
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1.3*inch, LETTER[1] - 1.18*inch, "DEBTREX SOLUTIONS")
    c.setFillColor(HexColor("#94B1D3"))
    c.setFont("Helvetica", 10)
    c.drawString(1.3*inch, LETTER[1] - 1.36*inch, "Internal Documentation")

    # Title block (center-ish)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 42)
    c.drawString(0.6*inch, LETTER[1] - 3.4*inch, "Website Setup")
    c.drawString(0.6*inch, LETTER[1] - 4.0*inch, "& Deployment Guide")

    # Subtitle
    c.setFillColor(HexColor("#B7D5FF"))
    c.setFont("Helvetica", 14)
    c.drawString(0.6*inch, LETTER[1] - 4.5*inch, "From files on disk to a live, compliant lead funnel")

    # Accent strip
    c.setFillColor(GREEN)
    c.rect(0.6*inch, LETTER[1] - 4.85*inch, 2.0*inch, 0.04*inch, fill=1, stroke=0)

    # Card with meta
    c.setFillColor(HexColor("#0E2444"))
    c.roundRect(0.6*inch, 1.6*inch, LETTER[0] - 1.2*inch, 2.2*inch, 10, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.85*inch, 1.6*inch + 1.85*inch, "WHAT'S INSIDE")

    items = [
        ("01", "Prerequisites & accounts you'll need"),
        ("02", "Local testing & directory structure"),
        ("03", "Vercel deployment (free tier works)"),
        ("04", "GoHighLevel webhook configuration"),
        ("05", "Meta Pixel + Conversions API setup"),
        ("06", "Domain, DNS, and SSL"),
        ("07", "Pre-launch compliance checklist"),
        ("08", "Testing, monitoring & troubleshooting"),
    ]
    y = 1.6*inch + 1.5*inch
    for num, label in items:
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(0.85*inch, y, num)
        c.setFillColor(white)
        c.setFont("Helvetica", 10)
        c.drawString(1.15*inch, y, label)
        y -= 0.18*inch

    # Footer band on cover
    c.setFillColor(HexColor("#94B1D3"))
    c.setFont("Helvetica", 9)
    c.drawString(0.6*inch, 1.0*inch, "VERSION 1.0  ·  JANUARY 2026")
    c.drawString(0.6*inch, 0.78*inch, "FOR INTERNAL USE  ·  CONTAINS CONFIGURATION INSTRUCTIONS")
    c.setFillColor(GREEN)
    c.rect(0, 0, LETTER[0], 0.15*inch, fill=1, stroke=0)


# === CONTENT BUILDERS ===
def para(text, style=None):
    return Paragraph(text, style or S_BODY)

def bullets(items, style=None):
    style = style or S_BULLET
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=8, value="•") for t in items],
        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=10, bulletColor=GREEN_DARK
    )

def numbered(items, style=None):
    style = style or S_BULLET
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=8) for t in items],
        bulletType="1", leftIndent=20, bulletFontName="Helvetica-Bold", bulletColor=GREEN_DARK
    )

def section_heading(num, title):
    return KeepTogether([
        SectionNumber(num),
        Spacer(1, 4),
        Paragraph(title, S_H1),
        HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=10),
    ])


# === BUILD ===
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=LETTER,
        leftMargin=0.6*inch, rightMargin=0.6*inch,
        topMargin=0.85*inch, bottomMargin=0.7*inch,
        title="Debtrex Solutions — Website Setup Guide",
        author="Debtrex Solutions"
    )

    story = []

    # ========== COVER (drawn by onFirstPage callback) ==========
    # First page is intentionally empty — cover art is drawn by draw_cover.
    # Spacer + PageBreak forces flow onto page 2 where real content begins.
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # ========== TABLE OF CONTENTS ==========
    story.append(Paragraph("Table of Contents", S_H1))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=14))

    toc_items = [
        ("1.", "What You Have", "4"),
        ("2.", "Accounts & Prerequisites", "5"),
        ("3.", "Directory Structure", "6"),
        ("4.", "Local Testing", "7"),
        ("5.", "Configure Your IDs", "8"),
        ("6.", "Deploy to Vercel", "10"),
        ("7.", "Set Environment Variables", "12"),
        ("8.", "Connect Your Domain", "13"),
        ("9.", "GoHighLevel Webhook Setup", "14"),
        ("10.", "Meta Pixel & Conversions API", "15"),
        ("11.", "End-to-End Lead Test", "17"),
        ("12.", "Pre-Launch Compliance Checklist", "18"),
        ("13.", "Going Live", "19"),
        ("14.", "Monitoring & Maintenance", "20"),
        ("15.", "Troubleshooting", "21"),
        ("16.", "Quick Reference Card", "22"),
    ]
    toc_data = [[Paragraph(num, S_TOC_NUM), Paragraph(title, S_TOC), Paragraph(page, S_TOC)] for num, title, page in toc_items]
    toc_table = Table(toc_data, colWidths=[0.5*inch, 5.5*inch, 0.6*inch])
    toc_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ========== SECTION 1: WHAT YOU HAVE ==========
    story.append(section_heading(1, "What You Have"))
    story.append(para(
        "This guide walks you through deploying the Debtrex Solutions website from local files to a live, "
        "fully compliant lead funnel. By the end you will have a public-facing site with a multi-step quiz, "
        "consent-gated Meta Pixel tracking, server-side Conversions API events, and leads flowing into your "
        "GoHighLevel CRM in real time."
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph("The site you are deploying includes:", S_H3))
    story.append(bullets([
        "<b>Landing page</b> (index.html) with hero, education, FAQ, and CTAs",
        "<b>Educational advertorial</b> (advertorial.html) for Meta-friendly pre-quiz traffic",
        "<b>7-step qualification quiz</b> (quiz.html) with TCPA consent capture",
        "<b>Thank-you page</b> with tier-aware messaging and Meta Lead event firing",
        "<b>4 legal pages</b>: Privacy Policy, Terms of Service, Disclosures, Cookie Policy",
        "<b>US-only cookie consent banner</b> honoring GPC signal (CCPA/CPRA compliant)",
        "<b>Serverless API</b> (api/lead.js) that forwards to GHL + fires Meta CAPI server-side",
        "<b>SEO setup</b>: sitemap.xml, robots.txt, OpenGraph cards, JSON-LD structured data",
    ]))

    story.append(Spacer(1, 8))
    story.append(Callout(
        "Estimated setup time",
        "Plan for 2–3 hours end-to-end if you already have a Meta Pixel and GoHighLevel account. Add 1 hour if you need to create those accounts first. The actual code deployment takes about 10 minutes — most of the time is in configuration and testing.",
        kind="info"
    ))
    story.append(PageBreak())

    # ========== SECTION 2: PREREQUISITES ==========
    story.append(section_heading(2, "Accounts & Prerequisites"))
    story.append(para("Before you start, make sure you have access to the following:"))

    prereq_data = [
        ["Account", "Purpose", "Cost"],
        ["Vercel", "Static hosting + serverless functions (where the site lives)", "Free tier OK"],
        ["GoHighLevel", "CRM, lead routing, dialer, automation", "Existing plan"],
        ["Meta Business Manager", "Ad account, Pixel, Conversions API access token", "Free"],
        ["Domain registrar", "Your custom domain (e.g. debtrexsolutions.com)", "~$12/year"],
        ["Node.js 18+", "Local CLI for vercel command (npm install -g vercel)", "Free"],
        ["GitHub (optional)", "Source control + auto-deploy on push", "Free"],
    ]
    t = Table(prereq_data, colWidths=[1.5*inch, 3.6*inch, 1.6*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, BG]),
        ("LINEBELOW", (0,0), (-1,0), 1.5, GREEN),
        ("LINEBELOW", (0,1), (-1,-2), 0.3, BORDER),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Information to collect before you begin", S_H3))
    story.append(bullets([
        "<b>Meta Pixel ID</b> — from Events Manager (e.g. 1234567890123456)",
        "<b>Meta CAPI access token</b> — Events Manager → Settings → Conversions API → Generate access token",
        "<b>GoHighLevel inbound webhook URL</b> — Automation → Workflows → Webhook trigger",
        "<b>Your production domain</b> — e.g. https://debtrexsolutions.com",
        "<b>Company state of incorporation</b> — for the Terms of Service governing-law clause",
        "<b>Business email addresses</b> — privacy@, legal@, compliance@, hello@",
    ]))
    story.append(PageBreak())

    # ========== SECTION 3: DIRECTORY STRUCTURE ==========
    story.append(section_heading(3, "Directory Structure"))
    story.append(para("Here's what should be in your project folder before deployment:"))
    story.append(Spacer(1, 4))
    story.append(CodeBlock(
"""DETREX SOLUTIONS/
├── index.html              Landing page
├── advertorial.html        Educational pre-quiz article
├── quiz.html               7-step qualification quiz
├── thank-you.html          Tier-aware confirmation
├── privacy.html            Privacy Policy (CCPA/state laws)
├── terms.html              Terms of Service
├── disclosures.html        FTC TSR + program disclosures
├── cookie-policy.html      Cookie disclosures
├── sitemap.xml             Search engine sitemap
├── robots.txt              Crawler rules
├── package.json            Node project config
├── vercel.json             Hosting config + security headers
├── api/
│   └── lead.js             Serverless lead receiver + Meta CAPI
├── css/
│   └── styles.css          Full design system
└── js/
    ├── main.js             Landing page interactions
    ├── quiz.js             Multi-step quiz logic + tier scoring
    ├── cookies.js          US/CCPA consent banner
    └── meta-pixel.js       Consent-gated Pixel loader"""
    ))
    story.append(Spacer(1, 12))
    story.append(Callout(
        "Don't rename folders",
        "The api/ folder is recognized by Vercel as serverless functions. The css/ and js/ paths are referenced from every HTML file. Renaming any of these breaks the site.",
        kind="warn"
    ))
    story.append(PageBreak())

    # ========== SECTION 4: LOCAL TESTING ==========
    story.append(section_heading(4, "Local Testing"))
    story.append(para("Before deploying, verify everything works on your machine."))

    story.append(Paragraph("Option A — Quick static preview (no API)", S_H3))
    story.append(para("Open any .html file directly in your browser by double-clicking. This works for everything except the serverless /api/lead endpoint — quiz submissions will fail silently, but you can verify layout, navigation, the cookie banner, and the quiz UI."))

    story.append(Paragraph("Option B — Full local stack with Vercel CLI (recommended)", S_H3))
    story.append(para("This runs the site exactly as it will run in production, including the serverless function."))
    story.append(Spacer(1, 4))
    story.append(CodeBlock(
"""# Install Vercel CLI globally (one-time)
npm install -g vercel

# In the project directory:
cd "C:\\Users\\YourName\\Path\\To\\DETREX SOLUTIONS"

# Log in (first time only)
vercel login

# Run local dev server
vercel dev"""
    ))
    story.append(para("Then open <b>http://localhost:3000</b> in your browser. The site runs on a real serverless runtime."))

    story.append(Paragraph("What to verify locally", S_H3))
    story.append(bullets([
        "Landing page loads without console errors",
        "All nav links work (How It Works, FAQ, Take Assessment)",
        "Cookie banner appears on first load",
        "\"Manage Preferences\" modal opens and toggles work",
        "Quiz steps advance one-by-one with auto-advance on radio choice",
        "Step 7 won't submit unless TCPA consent box is checked",
        "All 4 legal pages render correctly",
        "Footer \"Do Not Sell or Share\" link triggers the alert",
    ]))
    story.append(PageBreak())

    # ========== SECTION 5: CONFIGURE YOUR IDS ==========
    story.append(section_heading(5, "Configure Your IDs"))
    story.append(para("Two values must be set in your code before going live. These are the only required edits."))

    story.append(Paragraph("5.1  Meta Pixel ID", S_H3))
    story.append(para("Open <b>js/meta-pixel.js</b> in your editor. Near the top, find:"))
    story.append(CodeBlock("const META_PIXEL_ID = 'REPLACE_WITH_META_PIXEL_ID';"))
    story.append(para("Replace the placeholder with your actual Pixel ID:"))
    story.append(CodeBlock("const META_PIXEL_ID = '1234567890123456';"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.2  Webhook endpoint (already set)", S_H3))
    story.append(para("Open <b>js/quiz.js</b> and verify the WEBHOOK_URL points to your serverless endpoint:"))
    story.append(CodeBlock("const WEBHOOK_URL = '/api/lead';"))
    story.append(para("Leave this as-is unless you are <b>not</b> deploying the serverless function — in that case, replace with your GoHighLevel webhook URL directly (note: you'll lose Meta CAPI deduplication)."))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.3  Update domain references", S_H3))
    story.append(para("Search across the project for <b>debtrexsolutions.com</b> and replace with your actual domain in these files:"))
    story.append(bullets([
        "sitemap.xml (top of file + every &lt;loc&gt; tag)",
        "robots.txt (Sitemap line)",
        "All HTML files (canonical and OpenGraph URLs)",
    ]))
    story.append(para("If you're keeping debtrexsolutions.com, skip this step."))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.4  Governing law in Terms", S_H3))
    story.append(para("Open <b>terms.html</b>, find Section 14, and replace <b>[STATE]</b> with your company's state of incorporation:"))
    story.append(CodeBlock(
"""<!-- Before -->
These Terms are governed by the laws of the State of [STATE]

<!-- After -->
These Terms are governed by the laws of the State of Delaware"""
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.5  Add OG image and logo", S_H3))
    story.append(para("Create an <b>assets/</b> folder in your project root and add two images:"))
    story.append(bullets([
        "<b>assets/og-image.png</b> — 1200×630px, used in social-media link previews",
        "<b>assets/og-advertorial.png</b> — 1200×630px, for the advertorial page preview",
        "<b>assets/logo.png</b> — square logo, used in JSON-LD structured data",
    ]))
    story.append(Callout(
        "These are optional but recommended",
        "Without OG images, links shared on Facebook, Twitter, iMessage, etc. will render with generic browser metadata. With them, you control how your brand appears in every shared link.",
        kind="info"
    ))
    story.append(PageBreak())

    # ========== SECTION 6: DEPLOY TO VERCEL ==========
    story.append(section_heading(6, "Deploy to Vercel"))
    story.append(para("Vercel hosts the static site and runs the serverless /api/lead function. The free tier (Hobby plan) handles thousands of leads per month at no cost."))

    story.append(Paragraph("6.1  Create a Vercel account", S_H3))
    story.append(numbered([
        "Go to <b>vercel.com</b> and click \"Sign Up\".",
        "Sign in with GitHub, GitLab, Bitbucket, or email.",
        "Confirm your email if prompted.",
    ]))

    story.append(Paragraph("6.2  Deploy via CLI (fastest)", S_H3))
    story.append(CodeBlock(
"""# In your project directory
cd "C:\\Users\\YourName\\Path\\To\\DETREX SOLUTIONS"

# Deploy to a preview URL
vercel

# When prompted:
#   Set up and deploy?           Y
#   Which scope?                 (your personal account)
#   Link to existing project?    N
#   What's your project's name?  debtrex-solutions
#   In which directory?          ./
#   Override settings?           N

# Once preview deploy succeeds, push to production:
vercel --prod"""
    ))
    story.append(para("You'll get a URL like <b>https://debtrex-solutions.vercel.app</b> immediately. The site is live."))
    story.append(Spacer(1, 6))

    story.append(Paragraph("6.3  Deploy via GitHub (recommended for ongoing changes)", S_H3))
    story.append(numbered([
        "Create a new GitHub repository named <b>debtrex-solutions-site</b>.",
        "Push the project folder to the repo.",
        "On Vercel, click <b>New Project</b> → <b>Import Git Repository</b>.",
        "Select your repo and click <b>Deploy</b>.",
        "Every git push to <b>main</b> automatically deploys to production.",
        "Every push to other branches creates a preview URL for testing.",
    ]))

    story.append(Spacer(1, 8))
    story.append(Callout(
        "Don't commit secrets",
        "Never commit your Meta CAPI access token or GHL webhook URL to git. Those live in Vercel environment variables (next section), not in code.",
        kind="warn"
    ))
    story.append(PageBreak())

    # ========== SECTION 7: ENVIRONMENT VARIABLES ==========
    story.append(section_heading(7, "Set Environment Variables"))
    story.append(para("These keep your sensitive values out of the browser-visible code. The serverless function reads them at runtime."))

    story.append(Paragraph("Where to set them", S_H3))
    story.append(numbered([
        "Vercel dashboard → your project → <b>Settings</b> tab → <b>Environment Variables</b>",
        "Add each of the variables below",
        "Set scope to <b>Production</b>, <b>Preview</b>, and <b>Development</b> (all three)",
        "After adding, redeploy (Deployments tab → ⋯ → Redeploy)",
    ]))

    env_data = [
        ["Variable Name", "Value", "Required?"],
        ["GHL_WEBHOOK_URL", "Your full GoHighLevel inbound webhook URL", "Yes"],
        ["META_PIXEL_ID", "e.g. 1234567890123456", "For CAPI"],
        ["META_CAPI_ACCESS_TOKEN", "Long token from Events Manager → CAPI", "For CAPI"],
        ["META_TEST_EVENT_CODE", "TEST12345 (testing only — remove for production)", "Testing only"],
        ["ALLOWED_ORIGIN", "https://debtrexsolutions.com", "Recommended"],
    ]
    t = Table(env_data, colWidths=[1.9*inch, 3.4*inch, 1.4*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Courier-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, BG]),
        ("LINEBELOW", (0,0), (-1,0), 1.5, GREEN),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Callout(
        "After changing env vars",
        "Vercel does NOT auto-redeploy when you change env vars. Go to the Deployments tab, click the ⋯ menu next to your latest deployment, and choose Redeploy. New env values only apply after redeploy.",
        kind="warn"
    ))
    story.append(PageBreak())

    # ========== SECTION 8: DOMAIN ==========
    story.append(section_heading(8, "Connect Your Domain"))
    story.append(para("By default your site lives at debtrex-solutions.vercel.app. To use your custom domain:"))

    story.append(numbered([
        "Vercel dashboard → your project → <b>Settings</b> → <b>Domains</b>.",
        "Type your domain (e.g. <b>debtrexsolutions.com</b>) and click <b>Add</b>.",
        "Vercel will display DNS records to configure at your registrar.",
        "Log in to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.).",
        "Add the DNS records exactly as Vercel shows them.",
        "Wait 5–30 minutes for DNS propagation. Vercel auto-provisions an SSL certificate.",
    ]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Typical DNS records you'll add", S_H3))
    dns_data = [
        ["Type", "Name", "Value"],
        ["A", "@", "76.76.21.21"],
        ["CNAME", "www", "cname.vercel-dns.com"],
    ]
    t = Table(dns_data, colWidths=[1.0*inch, 1.5*inch, 4.2*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Courier"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, BG]),
    ]))
    story.append(t)

    story.append(Spacer(1, 12))
    story.append(Callout(
        "Use Vercel's actual records",
        "These values can change. Always copy the records directly from Vercel's domain settings page — don't rely on this guide. The values above are accurate at time of writing but Vercel updates them periodically.",
        kind="info"
    ))
    story.append(PageBreak())

    # ========== SECTION 9: GHL WEBHOOK ==========
    story.append(section_heading(9, "GoHighLevel Webhook Setup"))
    story.append(para("This is what receives every quiz submission and routes it to your closers."))

    story.append(Paragraph("9.1  Create the inbound webhook trigger", S_H3))
    story.append(numbered([
        "GHL sub-account → <b>Automation</b> → <b>Workflows</b> → <b>Create Workflow</b>.",
        "Name it: <b>Debtrex Website Lead Intake</b>.",
        "Add trigger: <b>Webhook</b> → <b>Inbound Webhook</b>.",
        "GHL generates a webhook URL. Copy it.",
        "Paste it into the <b>GHL_WEBHOOK_URL</b> environment variable in Vercel.",
    ]))

    story.append(Paragraph("9.2  Map incoming fields", S_H3))
    story.append(para("Send a test lead through your quiz (or use Postman). After the test fires, GHL will show all the fields available for mapping:"))
    story.append(bullets([
        "<b>full_name</b> → Contact Name",
        "<b>phone</b> → Contact Phone (use the +1 country code, /api/lead sends digits)",
        "<b>email</b> → Contact Email",
        "<b>state</b> → Custom field: State",
        "<b>debt_amount</b> → Custom field: Debt Range",
        "<b>tier</b> → Custom field: Lead Tier (A/B/C/D)",
        "<b>sla_minutes</b> → Custom field: SLA Minutes",
        "<b>utm_source</b>, <b>utm_campaign</b>, etc. → Attribution fields",
        "<b>tcpa_consent</b> + <b>consent_timestamp</b> + <b>consent_text</b> → store for legal compliance",
    ]))

    story.append(Paragraph("9.3  Add routing logic by tier", S_H3))
    story.append(bullets([
        "<b>Tier A</b> → Add tag \"Tier A\", assign to top closer, trigger immediate dial within 20 minutes",
        "<b>Tier B</b> → Add tag \"Tier B\", standard dial queue (30–45 min SLA)",
        "<b>Tier C</b> → Add tag \"Tier C\", scheduled callback or nurture flow",
        "<b>Tier D</b> → Add tag \"Disqualified\", educational email drip only",
    ]))
    story.append(PageBreak())

    # ========== SECTION 10: META PIXEL + CAPI ==========
    story.append(section_heading(10, "Meta Pixel & Conversions API"))
    story.append(para("The site fires Meta's <b>Lead</b> event from two sources — the browser Pixel and the server-side Conversions API. Both use the same event_id so Meta deduplicates."))

    story.append(Paragraph("10.1  Get your Pixel ID", S_H3))
    story.append(numbered([
        "Meta Business Manager → <b>Events Manager</b>.",
        "Select your Pixel (or create one named \"Debtrex Solutions Site\").",
        "Copy the Pixel ID from the top of the page.",
        "Paste it into <b>js/meta-pixel.js</b> (line ~11) AND into the <b>META_PIXEL_ID</b> env var on Vercel.",
    ]))

    story.append(Paragraph("10.2  Generate your CAPI access token", S_H3))
    story.append(numbered([
        "Events Manager → your Pixel → <b>Settings</b> tab.",
        "Scroll to <b>Conversions API</b> → <b>Generate access token</b>.",
        "Copy the token (you'll only see it once — store it safely).",
        "Paste into the <b>META_CAPI_ACCESS_TOKEN</b> env var on Vercel. Redeploy.",
    ]))

    story.append(Paragraph("10.3  Verify in Test Events", S_H3))
    story.append(numbered([
        "Events Manager → your Pixel → <b>Test Events</b> tab.",
        "Copy the <b>Test Event Code</b> at the top (e.g. TEST12345).",
        "Add it as the <b>META_TEST_EVENT_CODE</b> env var on Vercel. Redeploy.",
        "Submit a test lead through your live quiz.",
        "Within 60 seconds you should see two Lead events arrive — one labeled <b>Browser</b> and one <b>Server</b>.",
        "Confirm they have the SAME event_id and are <b>deduplicated</b> (Meta shows a green badge).",
        "<b>Remove the META_TEST_EVENT_CODE env var when done</b> — leaving it in keeps events in test mode.",
    ]))

    story.append(Spacer(1, 8))
    story.append(Callout(
        "Why both Pixel and CAPI?",
        "iOS privacy changes and ad blockers drop 20–40% of browser Pixel events. CAPI fires server-side and bypasses that entirely. Using both with deduplication gives you near-complete attribution data without double-counting.",
        kind="info"
    ))
    story.append(PageBreak())

    # ========== SECTION 11: END-TO-END TEST ==========
    story.append(section_heading(11, "End-to-End Lead Test"))
    story.append(para("Before driving any paid traffic, run this complete test to verify the full pipeline works."))

    story.append(numbered([
        "Open your live site (e.g. https://debtrexsolutions.com).",
        "Accept marketing cookies in the consent banner (so the Pixel loads).",
        "Click \"Take Free Assessment\" → step through the quiz with real-but-test values.",
        "On step 7 use a real phone and email YOU control (you'll need to verify the call).",
        "Check the TCPA consent box. Click \"See My Options\".",
        "Confirm you land on the thank-you page with personalized greeting.",
        "<b>Verify GHL</b>: open your workflow → check that the test lead arrived with all fields mapped.",
        "<b>Verify Meta</b>: Events Manager → Test Events → confirm Browser + Server Lead events show as deduplicated.",
        "<b>Verify routing</b>: if Tier A, confirm your dialer queued the call within the SLA.",
        "<b>Verify cookies</b>: clear cookies, reload, reject cookies → quiz still submits but Pixel does not fire.",
        "<b>Verify GPC</b>: enable Global Privacy Control in your browser, visit the site → no banner shown, Pixel auto-disabled.",
    ]))

    story.append(Spacer(1, 6))
    story.append(Callout(
        "Don't test with throwaway data",
        "GHL workflows are live the moment they're saved. A junk test lead with a real phone number could end up actually dialed. Use your own phone, and tell your closers a test is incoming before you submit.",
        kind="warn"
    ))
    story.append(PageBreak())

    # ========== SECTION 12: COMPLIANCE CHECKLIST ==========
    story.append(section_heading(12, "Pre-Launch Compliance Checklist"))
    story.append(para("Run through this list before pointing any paid traffic at the site. Most items take 2 minutes to verify but cost thousands if missed."))

    def check_item(text):
        return Paragraph(f"☐ &nbsp;&nbsp; {text}", S_BULLET)

    story.append(Paragraph("TCPA & Consent", S_H3))
    for item in [
        "Consent checkbox is <b>unchecked by default</b> on step 7 of the quiz.",
        "Consent text states \"express written consent\" and lists call/SMS/email channels.",
        "Consent text says \"consent is not a condition of any purchase.\"",
        "Consent text includes STOP/opt-out language.",
        "Privacy Policy and Terms links are present in the consent block.",
        "Server stores consent_text and consent_timestamp with every lead.",
    ]:
        story.append(check_item(item))

    story.append(Paragraph("FTC TSR (Debt Relief Telemarketing Sales Rule)", S_H3))
    for item in [
        "Disclosures page explicitly states no upfront fees before debt resolution.",
        "Disclosures page explains credit impact, tax implications, creditor lawsuit risk.",
        "No \"guaranteed savings\" or \"erase debt\" language anywhere on the site.",
        "No claim of government affiliation or government debt program.",
        "Disclaimer band visible on landing page.",
    ]:
        story.append(check_item(item))

    story.append(Paragraph("State Privacy Laws (CCPA + multistate)", S_H3))
    for item in [
        "\"Do Not Sell or Share My Personal Information\" link in every footer.",
        "Cookie banner functioning, GPC signal honored automatically.",
        "Cookie Policy page lists all categories and specific cookies.",
        "Privacy Policy Section 7a covers California opt-out rights.",
        "Sensitive personal information (debt/income) explicitly addressed in Privacy Policy.",
    ]:
        story.append(check_item(item))

    story.append(Paragraph("Meta Ad Compliance", S_H3))
    for item in [
        "No banned phrases on landing page: \"erase debt\", \"guaranteed savings\", \"government relief\", \"instant approval\", \"lock in savings\", \"stop collections immediately\".",
        "Advertorial reads as educational article, not sales page.",
        "All claims qualified with \"may\", \"could\", \"explore\" — no absolutes.",
        "No urgency countdowns, fake testimonials, or fake approvals.",
    ]:
        story.append(check_item(item))

    story.append(PageBreak())

    # ========== SECTION 13: GOING LIVE ==========
    story.append(section_heading(13, "Going Live"))
    story.append(para("When all compliance items pass and your test lead completed the full pipeline successfully:"))

    story.append(numbered([
        "Remove <b>META_TEST_EVENT_CODE</b> from Vercel env vars and redeploy.",
        "Submit <b>sitemap.xml</b> to Google Search Console (https://search.google.com/search-console).",
        "Verify domain ownership in Meta Business Manager → Brand Safety → Domains.",
        "Set up uptime monitoring (UptimeRobot free tier, ping every 5 minutes).",
        "Set up Vercel deployment notifications to your phone/Slack.",
        "Brief your closers: tier A SLAs are 15–20 minutes during business hours.",
        "Start with a small Meta campaign: <b>$50–$100/day, 3 ad sets, 3 creatives each</b>.",
        "Use UTM parameters on every ad: utm_source=meta, utm_medium=cpc, utm_campaign=name, utm_content=ad_id",
        "Monitor for the first 48 hours: cost per lead, contact rate, qualification rate, no Meta account warnings.",
    ]))

    story.append(Spacer(1, 8))
    story.append(Callout(
        "Start with $50/day. Not $500.",
        "Per the strategy doc, your first week of paid traffic is for learning what converts — not aggressive scaling. Small budgets reveal what's broken; big budgets compound the damage.",
        kind="warn"
    ))
    story.append(PageBreak())

    # ========== SECTION 14: MONITORING ==========
    story.append(section_heading(14, "Monitoring & Maintenance"))

    story.append(Paragraph("Daily (first 30 days)", S_H3))
    story.append(bullets([
        "Vercel logs — check for failed lead submissions",
        "Meta Events Manager — confirm Lead events firing, deduplication healthy",
        "GHL — verify leads arriving within seconds of submission",
        "Sales team — confirm SLAs being met by tier",
        "Cost per qualified lead vs. cost per submitted lead",
    ]))

    story.append(Paragraph("Weekly", S_H3))
    story.append(bullets([
        "Meta ad account health — no warnings, restrictions, or appeals pending",
        "Backend partner feedback — lead quality, retention, complaints",
        "Compliance review — random call recording QA from any new closers",
        "Update creatives — Meta penalizes fatigued creatives quickly in this vertical",
    ]))

    story.append(Paragraph("Monthly", S_H3))
    story.append(bullets([
        "Review Privacy/Terms/Disclosures — update if any service or compliance change",
        "Refresh OG images and advertorial content (Meta favors recently-updated pages)",
        "Audit which utm_source / utm_campaign combos produce best retention (not just enrollment)",
        "Rotate Meta CAPI access token if your security policy requires",
    ]))

    story.append(Paragraph("Where to find logs", S_H3))
    story.append(bullets([
        "<b>Vercel</b> → project → Deployments → click deployment → Functions tab → click <b>api/lead</b>",
        "<b>Meta</b> → Events Manager → your Pixel → Overview (real-time event volume + dedup rate)",
        "<b>GHL</b> → Automation → Workflows → your workflow → Execution Logs",
    ]))
    story.append(PageBreak())

    # ========== SECTION 15: TROUBLESHOOTING ==========
    story.append(section_heading(15, "Troubleshooting"))

    issues = [
        ("Quiz submits but no lead in GHL",
         "Check Vercel function logs (api/lead). If you see 'no_ghl_url' the env var isn't set — add GHL_WEBHOOK_URL and redeploy. If GHL responds with non-200, test the webhook URL directly in Postman."),
        ("Meta events not firing",
         "Open browser console on the live thank-you page after accepting cookies — look for fbq errors. If 'pixel not loaded', the Pixel ID env var or js/meta-pixel.js value is missing. If 'cors error', check that ALLOWED_ORIGIN matches your domain exactly (with https://, no trailing slash)."),
        ("Lead events fire twice (no dedup)",
         "Browser and server events have different event_id values. Confirm js/quiz.js generates event_id, stores it in sessionStorage, AND sends it in the payload. Confirm api/lead.js reads lead.event_id and includes it in the CAPI request. Check Meta Test Events — matching event_id values will show a 'Deduplicated' badge."),
        ("Cookie banner shows on every page load",
         "User's browser is blocking localStorage. Check that the site is served from a real domain (not file:// or localhost with strict mode). LocalStorage is required for consent persistence."),
        ("CCPA opt-out doesn't disable Pixel",
         "Confirm js/cookies.js loads BEFORE js/meta-pixel.js in every HTML page. The Pixel listens for the 'debtrex:consent' event — if the order is wrong, the event fires before the listener attaches."),
        ("Vercel deploy fails",
         "Check that package.json is valid JSON. Check the api/lead.js file uses module.exports = async (req, res) => ... (not export default). Confirm Node 18+ in package.json engines."),
        ("OG image not showing in link previews",
         "Facebook caches OG data aggressively. Use Facebook's Sharing Debugger (developers.facebook.com/tools/debug) to force a refresh after adding/changing the og:image."),
        ("Meta ad account warned or restricted",
         "Stop spending. Review your active ads against the banned-language list in Section 12. Most restrictions clear in 24–72 hours after compliant creatives replace flagged ones. Always have backup creatives ready."),
    ]
    for title, body in issues:
        story.append(Paragraph(title, S_H3))
        story.append(para(body))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ========== SECTION 16: QUICK REFERENCE ==========
    story.append(section_heading(16, "Quick Reference Card"))
    story.append(para("Keep this page open during setup."))

    story.append(Paragraph("Files you must edit before going live", S_H3))
    ref_data = [
        ["File", "Change", "Value"],
        ["js/meta-pixel.js", "Pixel ID", "Your Meta Pixel ID"],
        ["terms.html §14", "Governing state", "Your state of incorporation"],
        ["sitemap.xml", "All loc URLs", "Your production domain"],
        ["robots.txt", "Sitemap line", "Your production domain"],
        ["*.html canonical/OG", "URLs", "Your production domain"],
    ]
    t = Table(ref_data, colWidths=[1.7*inch, 1.5*inch, 3.4*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Courier"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, BG]),
    ]))
    story.append(t)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Vercel environment variables", S_H3))
    story.append(CodeBlock(
"""GHL_WEBHOOK_URL          = https://services.leadconnectorhq.com/hooks/...
META_PIXEL_ID            = 1234567890123456
META_CAPI_ACCESS_TOKEN   = EAAxxxxxxxxxxxxxxxxxxxxxx
META_TEST_EVENT_CODE     = TEST12345   (remove for production)
ALLOWED_ORIGIN           = https://debtrexsolutions.com"""
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Critical URLs", S_H3))
    story.append(bullets([
        "<b>Vercel dashboard</b>: https://vercel.com/dashboard",
        "<b>Meta Events Manager</b>: https://business.facebook.com/events_manager",
        "<b>Meta Test Events</b>: Events Manager → your Pixel → Test Events tab",
        "<b>FB Sharing Debugger</b>: https://developers.facebook.com/tools/debug/",
        "<b>Google Search Console</b>: https://search.google.com/search-console",
    ]))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>This guide covers the technical setup. For ongoing compliance, partner vetting, "
        "creative strategy, and operational management, refer back to the original "
        "Debtrex Solutions strategy and compliance documents.</i>",
        S_FOOT
    ))

    # ========== BUILD ==========
    doc.build(story, onFirstPage=draw_cover, onLaterPages=header_footer)
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build()
