"""Build a standalone A5 print poster; no website files are changed."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tmp' / 'pdf-deps'))

import fitz
import qrcode
import zxingcpp
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

URL = 'https://www.gopaltea.store/'
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / 'gopal-tea-stall-qr-a5.pdf'
PNG = OUT / 'gopal-tea-stall-qr-a5.png'
W, H = 148 * mm, 210 * mm
CREAM = HexColor('#FFF8E9')
COFFEE = HexColor('#23160F')
GOLD = HexColor('#D8A928')
RED = HexColor('#B51225')
MUTED = HexColor('#6B513A')

pdfmetrics.registerFont(TTFont('Hindi', 'C:/Windows/Fonts/mangal.ttf', shapable=True))
pdfmetrics.registerFont(TTFont('HindiBold', 'C:/Windows/Fonts/mangalb.ttf', shapable=True))
c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle('Gopal Chai Service - Website QR - A5 stall poster')
c.setAuthor('Gopal Chai Service')

def text(content, top_mm, size, color, font='Hindi'):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(W / 2, H - top_mm * mm, content, shaping=True)

# Cream paper with a rich, compact brand header.
c.setFillColor(CREAM)
c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(COFFEE)
c.rect(0, H - 64 * mm, W, 64 * mm, fill=1, stroke=0)
c.setFillColor(RED)
c.rect(0, H - 2 * mm, W, 2 * mm, fill=1, stroke=0)
c.setStrokeColor(GOLD)
c.setLineWidth(.7)
c.rect(4 * mm, 4 * mm, W - 8 * mm, H - 8 * mm, fill=0, stroke=1)

logo_size = 33 * mm
c.drawImage(str(ROOT / 'images/brand/gopal-chai-logo-v1.png'),
            (W - logo_size) / 2, H - 40 * mm, logo_size, logo_size,
            preserveAspectRatio=True, mask='auto')
text('गोपाल चाय सर्विस', 49, 25, CREAM, 'HindiBold')
text('चाय का स्वाद, देसी मेहमाननवाज़ी', 58, 10, HexColor('#F4CE72'))

text('हमारी वेबसाइट देखें', 76, 21, RED, 'HindiBold')
text('अपने फोन का कैमरा खोलें और स्कैन करें', 85, 10, MUTED)

# QR is real vector geometry, with four modules of white quiet zone.
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4)
qr.add_data(URL)
qr.make(fit=True)
matrix = qr.get_matrix()
count = len(matrix)
qr_size = 78 * mm
qr_x, qr_y = (W - qr_size) / 2, H - 170 * mm
c.setFillColor(HexColor('#FFFFFF'))
c.rect(qr_x, qr_y, qr_size, qr_size, fill=1, stroke=0)
module = qr_size / count
c.setFillColor(HexColor('#000000'))
for row, values in enumerate(matrix):
    for col, filled in enumerate(values):
        if filled:
            c.rect(qr_x + col * module, qr_y + (count - row - 1) * module,
                   module, module, fill=1, stroke=0)
c.linkURL(URL, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), relative=0)

# Corner marks stay outside the white quiet zone.
c.setStrokeColor(GOLD)
c.setLineWidth(1.3)
offset, arm = 2.5 * mm, 7 * mm
for x, dx in [(qr_x - offset, 1), (qr_x + qr_size + offset, -1)]:
    for y, dy in [(qr_y - offset, 1), (qr_y + qr_size + offset, -1)]:
        c.line(x, y, x + dx * arm, y)
        c.line(x, y, x, y + dy * arm)

text('www.gopaltea.store', 181, 17, COFFEE, 'Helvetica-Bold')
text('चाय की वैरायटी  •  आयोजन की तस्वीरें  •  बुकिंग', 190, 9.1, MUTED)
c.setStrokeColor(HexColor('#D4B884'))
c.setLineWidth(.5)
c.line(22 * mm, H - 194.5 * mm, W - 22 * mm, H - 194.5 * mm)
text('बुकिंग / WhatsApp : 94149 39839', 201, 10, COFFEE, 'HindiBold')
c.showPage()
c.save()

# Render the final PDF itself for print PNG and QA.
doc = fitz.open(PDF)
page = doc[0]
page.get_pixmap(dpi=300, alpha=False).save(PNG)
preview = ROOT / 'tmp' / 'pdfs' / 'stall-poster-preview.png'
preview.parent.mkdir(parents=True, exist_ok=True)
page.get_pixmap(dpi=120, alpha=False).save(preview)
decoded = zxingcpp.read_barcodes(Image.open(PNG))
assert any(result.text == URL for result in decoded), 'QR must decode from rendered poster'
smaller = Image.open(PNG)
smaller.thumbnail((740, 1050))
assert any(result.text == URL for result in zxingcpp.read_barcodes(smaller)), 'QR must also decode at reduced size'
assert len(doc) == 1
assert abs(page.rect.width - W) < .1 and abs(page.rect.height - H) < .1
report = {'url': URL, 'page_mm': [148, 210], 'png_px': Image.open(PNG).size,
          'dpi': 300, 'qr_mm': 78, 'quiet_zone_modules': 4,
          'decoded_from_final_poster': [r.text for r in decoded],
          'decoded_at_reduced_size': True}
(ROOT / 'tmp' / 'pdfs' / 'stall-poster-checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
print(PDF)
print(PNG)
