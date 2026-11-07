"""Generates the test images for promptfooconfig-vision.yaml (ground truth is known exactly).
Run once:  python3 make_vision_fixtures.py     (needs: pip3 install pillow)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures_vision")
os.makedirs(OUT, exist_ok=True)


def font(size):
    return ImageFont.load_default(size=size)


def save(img, name, **kw):
    img.save(os.path.join(OUT, name), **kw)


# 1. Sign (OCR, big text)
img = Image.new("RGB", (900, 300), (20, 60, 140))
d = ImageDraw.Draw(img)
d.rounded_rectangle([20, 20, 880, 280], 30, outline="white", width=8)
d.text((450, 110), "OPEN 24 HOURS", fill="white", font=font(90), anchor="mm")
d.text((450, 220), "Mon - Sun", fill=(200, 220, 255), font=font(48), anchor="mm")
save(img, "sign.png")

# 2. Receipt (OCR + numbers) in PNG / JPEG / WebP / small
img = Image.new("RGB", (560, 520), "white")
d = ImageDraw.Draw(img)
d.text((280, 40), "CORNER CAFE", fill="black", font=font(44), anchor="mm")
rows = [("Coffee", "3.50"), ("Sandwich", "7.25"), ("Water", "1.20")]
y = 120
for n, p in rows:
    d.text((50, y), n, fill="black", font=font(36))
    d.text((510, y), p, fill="black", font=font(36), anchor="ra")
    y += 60
d.line([50, y + 10, 510, y + 10], fill="black", width=3)
d.text((50, y + 40), "TOTAL", fill="black", font=font(40))
d.text((510, y + 40), "11.95", fill="black", font=font(40), anchor="ra")
d.text((280, 450), "Thank you!", fill=(90, 90, 90), font=font(30), anchor="mm")
save(img, "receipt.png")
save(img, "receipt.jpg", quality=35)
save(img, "receipt.webp", quality=80)
save(img.resize((280, 260), Image.LANCZOS), "receipt_small.png")

# 3. Terminal screenshot
img = Image.new("RGB", (1000, 260), (22, 22, 26))
d = ImageDraw.Draw(img)
lines = [
    ("$ cp backup.tar /mnt/usb/", (230, 230, 230)),
    ("cp: error writing '/mnt/usb/backup.tar': No space left on device", (255, 120, 120)),
    ("ERROR: disk full (code 28)", (255, 80, 80)),
]
for i, (t, c) in enumerate(lines):
    d.text((30, 40 + i * 70), t, fill=c, font=font(30))
save(img, "terminal.png")

# 4. Shapes: 5 red circles, 3 blue squares
img = Image.new("RGB", (800, 420), "white")
d = ImageDraw.Draw(img)
slots = [(x, y) for y in (110, 300) for x in (100, 270, 440, 610)]
order = [0, 3, 1, 6, 4, 2, 7, 5]  # fixed shuffle
kinds = ["c", "c", "s", "c", "s", "c", "s", "c"]
for slot_i, kind in zip(order, kinds):
    cx, cy = slots[slot_i]
    if kind == "c":
        d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(220, 30, 30))
    else:
        d.rectangle([cx - 50, cy - 50, cx + 50, cy + 50], fill=(30, 60, 220))
save(img, "shapes.png")

# 5. Traffic light (green lit)
img = Image.new("RGB", (300, 520), (200, 200, 200))
d = ImageDraw.Draw(img)
d.rounded_rectangle([90, 30, 210, 490], 25, fill=(25, 25, 25))
for cy, col in zip((110, 260, 410), ((80, 0, 0), (80, 70, 0), (0, 220, 60))):
    d.ellipse([110, cy - 40, 190, cy + 40], fill=col)
save(img, "traffic.png")

# 6. Bar chart: Jan 40, Feb 70, Mar 55
img = Image.new("RGB", (600, 420), "white")
d = ImageDraw.Draw(img)
d.line([60, 360, 560, 360], fill="black", width=3)
d.text((300, 25), "Monthly sales (units)", fill="black", font=font(28), anchor="mm")
for i, (m, v) in enumerate([("Jan", 40), ("Feb", 70), ("Mar", 55)]):
    x0 = 100 + i * 160
    d.rectangle([x0, 360 - v * 4, x0 + 100, 360], fill=(50, 120, 200))
    d.text((x0 + 50, 360 - v * 4 - 22), str(v), fill="black", font=font(28), anchor="mm")
    d.text((x0 + 50, 385), m, fill="black", font=font(28), anchor="mm")
save(img, "bar_chart.png")

# 7. Table
img = Image.new("RGB", (640, 300), "white")
d = ImageDraw.Draw(img)
data = [("Name", "Age", "City"), ("Ana", "31", "Porto"), ("Bruno", "47", "Lisbon"), ("Clara", "25", "Faro")]
for r, row in enumerate(data):
    for c, cell in enumerate(row):
        x, y = 20 + c * 200, 20 + r * 65
        d.rectangle([x, y, x + 200, y + 65], outline="black", width=2,
                    fill=(225, 225, 225) if r == 0 else "white")
        d.text((x + 100, y + 33), cell, fill="black", font=font(32), anchor="mm")
save(img, "table.png")

# 8. Spatial: red square left, blue circle right
img = Image.new("RGB", (600, 300), "white")
d = ImageDraw.Draw(img)
d.rectangle([80, 90, 200, 210], fill=(220, 30, 30))
d.ellipse([400, 90, 520, 210], fill=(30, 60, 220))
save(img, "spatial.png")

# 9. Flow diagram: Download -> Convert -> Upload
img = Image.new("RGB", (900, 220), "white")
d = ImageDraw.Draw(img)
for i, t in enumerate(["Download", "Convert", "Upload"]):
    x0 = 30 + i * 300
    d.rounded_rectangle([x0, 60, x0 + 220, 160], 15, outline="black", width=4, fill=(235, 245, 255))
    d.text((x0 + 110, 110), t, fill="black", font=font(36), anchor="mm")
    if i < 2:
        ax = x0 + 230
        d.line([ax, 110, ax + 55, 110], fill="black", width=5)
        d.polygon([(ax + 70, 110), (ax + 50, 95), (ax + 50, 125)], fill="black")
save(img, "flow.png")

# 10. Analog clock showing 3:00
img = Image.new("RGB", (420, 420), "white")
d = ImageDraw.Draw(img)
cx = cy = 210
d.ellipse([20, 20, 400, 400], outline="black", width=8)
for h in range(12):
    a = math.radians(h * 30 - 90)
    d.line([cx + 160 * math.cos(a), cy + 160 * math.sin(a), cx + 180 * math.cos(a), cy + 180 * math.sin(a)],
           fill="black", width=5)
for h, (tx, ty) in {12: (210, 70), 3: (350, 210), 6: (210, 350), 9: (70, 210)}.items():
    d.text((tx, ty), str(h), fill="black", font=font(34), anchor="mm")
d.line([cx, cy, cx + 70, cy], fill="black", width=12)   # hour hand -> 3
d.line([cx, cy, cx, cy - 105], fill="black", width=7)    # minute hand -> 12
d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill="black")
save(img, "clock.png")

# 11. Wi-Fi card
img = Image.new("RGB", (800, 340), (250, 245, 230))
d = ImageDraw.Draw(img)
d.text((400, 60), "Cafe Aurora", fill=(120, 60, 20), font=font(56), anchor="mm")
d.text((60, 160), "Wi-Fi network:  CafeAurora_Guest", fill="black", font=font(36))
d.text((60, 240), "Password:  blue-fox-77", fill="black", font=font(40))
save(img, "wifi_card.png")

# 12. Boarding pass
img = Image.new("RGB", (800, 360), (235, 240, 250))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 800, 70], fill=(10, 60, 130))
d.text((30, 35), "BOARDING PASS", fill="white", font=font(38), anchor="lm")
d.text((40, 110), "Flight TP1234", fill="black", font=font(40))
d.text((40, 180), "LISBON  ->  PORTO", fill="black", font=font(40))
d.text((40, 250), "Gate B7", fill="black", font=font(40))
d.text((400, 250), "Boarding 18:45", fill="black", font=font(40))
save(img, "boarding_pass.png")

# 13. Nearly blank image (hallucination trap)
img = Image.new("RGB", (500, 300), "white")
ImageDraw.Draw(img).ellipse([245, 145, 252, 152], fill=(190, 190, 190))
save(img, "blank.png")

print("fixtures written to", OUT)