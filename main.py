"""Draw the 22 November 2026 world-news infographic (1024x1024 PNG).

One image, six stories from Sunday 22 November 2026, each verified
against multiple news sources the same day:
  1. cargo ship Sparta II on fire in the Gulf of Finland
  2. two oil tankers struck near the Strait of Hormuz
  3. COP31 climate talks in Antalya go into a second overtime day
  4. Iran claims a missile hit a US F-16; US Central Command denies it
  5. cost-of-living protests clash with police in Strasbourg
  6. magnitude 6.7 earthquake in Peru's Junin region

Layout: navy date header, gold rule, a 2x3 grid of story panels.
Every panel has a tag, a headline, a short factual summary and a
small illustration drawn from plain PIL shapes (no photos, so no
garbled text). Pure standard library + Pillow; no network; the
output is byte-identical on every run.
"""
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024
PAPER = (250, 249, 246)
NAVY = (13, 38, 68)
GOLD = (198, 162, 60)
INK = (22, 22, 22)
SOFT = (88, 94, 102)
EDGE = (212, 208, 201)
WHITE = (255, 255, 255)
SKY = (223, 232, 240)

REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    """Load a TrueType font at the requested size."""
    return ImageFont.truetype(path, size)


def split_lines(draw, words, fnt, limit):
    """Greedy word wrap: returns lines that fit inside limit pixels."""
    fitted = []
    current = ""
    for piece in words:
        trial = piece if not current else current + " " + piece
        if draw.textlength(trial, font=fnt) <= limit:
            current = trial
        else:
            if current:
                fitted.append(current)
            current = piece
    if current:
        fitted.append(current)
    return fitted


def wrap_text(draw, text, fnt, limit):
    return split_lines(draw, text.split(), fnt, limit)


# ---------------------------------------------------------------- drawings
# Each sketch draws inside the box (bx, by) .. (bx+bw, by+bh) given to it.
# They use only rectangles, polygons, ellipses and lines.

def sketch_ship(d, bx, by, bw, bh, accent):
    """A cargo ship with flames above the deck and smoke rising."""
    sea_y = by + bh - 26
    d.line([(bx, sea_y), (bx + bw, sea_y)], fill=(120, 150, 175), width=3)
    d.line([(bx + 8, sea_y + 10), (bx + bw - 8, sea_y + 10)],
           fill=(150, 175, 195), width=3)
    d.polygon([(bx + 12, sea_y - 26), (bx + bw - 12, sea_y - 26),
               (bx + bw - 22, sea_y), (bx + 22, sea_y)],
              fill=(52, 68, 86))
    for cx in (bx + 26, bx + 52, bx + 78):
        d.rectangle([cx, sea_y - 44, cx + 20, sea_y - 26], fill=accent)
    d.polygon([(bx + 58, sea_y - 44), (bx + 66, sea_y - 66),
               (bx + 74, sea_y - 44)], fill=(232, 116, 28))
    d.polygon([(bx + 84, sea_y - 44), (bx + 90, sea_y - 62),
               (bx + 96, sea_y - 44)], fill=(240, 178, 44))
    d.ellipse([bx + 60, by + 2, bx + 78, by + 20], fill=(150, 156, 162))
    d.ellipse([bx + 76, by + 12, bx + 92, by + 28], fill=(170, 175, 180))


def sketch_tankers(d, bx, by, bw, bh, accent):
    """Two oil tankers on open water under a low sun."""
    d.ellipse([bx + bw - 34, by + 4, bx + bw - 8, by + 30],
              fill=(240, 178, 44))
    sea_y = by + bh - 30
    d.polygon([(bx + 6, sea_y - 16), (bx + 56, sea_y - 16),
               (bx + 50, sea_y), (bx + 12, sea_y)], fill=(52, 68, 86))
    d.rectangle([bx + 40, sea_y - 30, bx + 48, sea_y - 16], fill=accent)
    d.polygon([(bx + 62, sea_y - 12), (bx + 108, sea_y - 12),
               (bx + 102, sea_y + 2), (bx + 68, sea_y + 2)],
              fill=(90, 104, 120))
    d.rectangle([bx + 84, sea_y - 24, bx + 90, sea_y - 12], fill=accent)
    d.line([(bx, sea_y + 12), (bx + bw, sea_y + 12)],
           fill=(120, 150, 175), width=3)
    d.line([(bx + 10, sea_y + 20), (bx + bw - 10, sea_y + 20)],
           fill=(150, 175, 195), width=3)


def sketch_globe(d, bx, by, bw, bh, accent):
    """A globe with a thermometer beside it: climate talks running late."""
    cx, cy, r = bx + 44, by + 46, 38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(58, 124, 180))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 70, 110), width=2)
    d.arc([cx - r + 10, cy - r, cx + r - 10, cy + r], 90, 270,
          fill=(120, 190, 130), width=5)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(120, 190, 130), width=4)
    tx = bx + 96
    d.rounded_rectangle([tx, by + 8, tx + 16, by + 66], radius=8,
                        fill=WHITE, outline=accent, width=3)
    d.ellipse([tx - 3, by + 60, tx + 19, by + 82], fill=(200, 48, 48))
    d.rectangle([tx + 5, by + 22, tx + 11, by + 62], fill=(232, 116, 28))
    d.line([(bx + 8, by + bh - 8), (bx + bw - 8, by + bh - 8)],
           fill=EDGE, width=2)


def sketch_jet(d, bx, by, bw, bh, accent):
    """A fighter jet with a missile streak crossing the sky."""
    d.polygon([(bx + 4, by + 52), (bx + 62, by + 30), (bx + 96, by + 42),
               (bx + 62, by + 58), (bx + 24, by + 64)],
              fill=(70, 84, 100))
    d.polygon([(bx + 40, by + 42), (bx + 52, by + 16), (bx + 60, by + 42)],
              fill=(90, 104, 120))
    d.polygon([(bx + 40, by + 56), (bx + 50, by + 76), (bx + 58, by + 56)],
              fill=(90, 104, 120))
    d.line([(bx + 78, by + 12), (bx + 98, by + 22)], fill=accent, width=5)
    d.ellipse([bx + 94, by + 18, bx + 104, by + 28], fill=accent)
    d.line([(bx + 4, by + 84), (bx + 38, by + 84)], fill=EDGE, width=2)
    d.line([(bx + 46, by + 84), (bx + 78, by + 84)], fill=EDGE, width=2)
    d.line([(bx + 86, by + 84), (bx + 102, by + 84)], fill=EDGE, width=2)


def sketch_crowd(d, bx, by, bw, bh, accent):
    """A line of demonstrators holding placards."""
    base = by + bh - 18
    for i, px in enumerate((bx + 8, bx + 32, bx + 56, bx + 80)):
        d.ellipse([px, by + 26, px + 20, by + 46], fill=(70, 84, 100))
        d.rectangle([px + 1, by + 48, px + 19, base], fill=(110, 122, 136))
    d.line([(bx + 18, by + 8), (bx + 18, by + 30)], fill=INK, width=3)
    d.rectangle([bx + 4, by + 2, bx + 42, by + 18], fill=accent)
    d.line([(bx + 68, by + 10), (bx + 68, by + 32)], fill=INK, width=3)
    d.rectangle([bx + 52, by + 4, bx + 92, by + 20], fill=(240, 178, 44))
    d.line([(bx, base + 6), (bx + bw, base + 6)], fill=EDGE, width=2)


def sketch_quake(d, bx, by, bw, bh, accent):
    """Andean peaks with a crack and a seismograph trace."""
    d.polygon([(bx + 4, by + bh - 22), (bx + 34, by + 18),
               (bx + 64, by + bh - 22)], fill=(90, 104, 120))
    d.polygon([(bx + 44, by + bh - 22), (bx + 82, by + 6),
               (bx + 118, by + bh - 22)], fill=(70, 84, 100))
    d.polygon([(bx + 28, by + 26), (bx + 34, by + 18), (bx + 40, by + 26),
               (bx + 36, by + 30), (bx + 30, by + 30)], fill=WHITE)
    crack = [(bx + 74, by + 22), (bx + 80, by + 34), (bx + 74, by + 44),
             (bx + 82, by + 56), (bx + 76, by + 68)]
    d.line(crack, fill=accent, width=4, joint="curve")
    d.line([(bx + 6, by + bh - 8), (bx + 30, by + bh - 8),
            (bx + 38, by + bh - 16), (bx + 46, by + bh - 2),
            (bx + 54, by + bh - 8), (bx + 118, by + bh - 8)],
           fill=(200, 48, 48), width=2, joint="curve")


# ---------------------------------------------------------------- stories
# (tag, accent colour, headline, summary, sketch function)

STORIES = [
    ("GULF OF FINLAND", (146, 90, 16),
     "Sparta II ablaze after drone strike",
     "All 16 crew evacuated; the vessel drifts into Finnish waters.",
     sketch_ship),
    ("STRAIT OF HORMUZ", (178, 34, 34),
     "Two oil tankers struck near Oman",
     "Two tankers hit near Khasab as Iran tensions rise; US escorts nearby.",
     sketch_tankers),
    ("CLIMATE", (22, 122, 74),
     "COP31 talks into second overtime day",
     "No deal in Antalya; fossil fuels divide talks. EU: \u201cgood deal or no deal\u201d.",
     sketch_globe),
    ("GULF TENSIONS", (27, 77, 158),
     "Iran claims F-16 hit; US denies it",
     "Tehran says a missile hit the jet; US Central Command says all intact.",
     sketch_jet),
    ("FRANCE", (120, 53, 153),
     "Cost-of-living clashes in Strasbourg",
     "Masked demonstrators clash with police in the sixth weekend of marches.",
     sketch_crowd),
    ("PERU", (21, 94, 117),
     "Magnitude 6.7 quake shakes Junin",
     "Strong tremor in the Andean Junin region; 15 injured, no deaths.",
     sketch_quake),
]


def build():
    """Compose the full 1024x1024 image and return it."""
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    d = ImageDraw.Draw(img)

    # Header: navy band, gold rule, date and day line.
    d.rectangle([0, 0, CANVAS_W, 168], fill=NAVY)
    d.rectangle([0, 168, CANVAS_W, 174], fill=GOLD)
    date_font = load(BOLD, 70)
    sub_font = load(REGULAR, 26)
    d.text((48, 28), "22 NOVEMBER 2026", font=date_font, fill=WHITE)
    d.text((48, 114), "The world in one day  \u00b7  Sunday",
           font=sub_font, fill=(205, 216, 230))

    # Panel grid: 2 columns, 3 rows.
    gx, gy = 32, 198
    gw, gh = 464, 236
    gapx, gapy = 32, 24
    tag_font = load(BOLD, 19)
    head_font = load(BOLD, 27)
    sum_font = load(REGULAR, 20)

    for idx, (tag, accent, head, summary, sketch) in enumerate(STORIES):
        col, row = idx % 2, idx // 2
        x0 = gx + col * (gw + gapx)
        y0 = gy + row * (gh + gapy)
        x1, y1 = x0 + gw, y0 + gh
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=WHITE,
                            outline=EDGE, width=2)
        d.rectangle([x0, y0 + 14, x0 + 8, y1 - 14], fill=accent)

        # Text block on the left, illustration on the right.
        tx = x0 + 26
        text_w = 304
        d.text((tx, y0 + 18), tag, font=tag_font, fill=accent)
        head_lines = wrap_text(d, head, head_font, text_w)
        yy = y0 + 50
        for line in head_lines[:3]:
            d.text((tx, yy), line, font=head_font, fill=INK)
            yy += 33
        sum_lines = wrap_text(d, summary, sum_font, text_w)
        yy = y0 + 50 + 3 * 33 + 8
        for line in sum_lines[:3]:
            d.text((tx, yy), line, font=sum_font, fill=SOFT)
            yy += 25

        # Illustration panel on the right.
        ix = x0 + gw - 134
        iy = y0 + 22
        d.rounded_rectangle([ix, iy, x0 + gw - 14, y0 + gh - 18],
                            radius=10, fill=SKY)
        sketch(d, ix + 8, iy + 12, 104, gh - 52, accent)

    # Footer with the reporting sources.
    foot_font = load(REGULAR, 18)
    d.text((32, CANVAS_H - 34),
           "Sources: Reuters  \u00b7  AP  \u00b7  AFP  \u00b7  BBC  \u00b7  NYT",
           font=foot_font, fill=SOFT)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    picture = build()
    picture.save(os.path.join(out_dir, "entry.png"))
    print("saved entry.png")


if __name__ == "__main__":
    main()
