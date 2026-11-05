"""Builds the social profile kit: one avatar and one banner per platform, at each platform's own size.

Composed from the app's CSS, logo files and character exports, like build_assets.py. Nothing is drawn.
Sizes were read from each platform's help pages and edit screens on 5 Nov 2026 (D-124).

    CHROME=/path/to/chrome python3 tools/build_social.py OUTDIR
"""

import asyncio
import os
import pathlib
import sys

from PIL import Image, ImageDraw
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "thefrappeguy" / "public"

N = {}
for line in (ROOT / "thefrappeguy" / "characters.py").read_text().splitlines():
	line = line.strip()
	if line.startswith('"') and "(" in line:
		N[line.split('"')[1]] = float(line.split(",")[3])


def u(rel):
	return (PUB / rel).as_uri()


HEADLINE = "Learn Frappe the easy way."
SUB = "Short comic explainers on ERPNext, Frappe Cloud and the rest of Frappe."
URL = "thefrappeguy.com"

# Each banner: canvas size, the band the platform always shows (x, y, w, h), where the text sits,
# where the two characters stand, and how tall a large pose stands (fig, px).
BANNERS = {
	# YouTube: 2560 x 1440 recommended. Desktop shows the full-width band 2560 x 423 (at this scale);
	# phones show only the centre 1546 x 423 safe area, so the text lives there.
	"youtube": dict(w=2560, h=1440, band=(0, 508, 2560, 423), text=(507, 540, 1546, 360), align="center",
		size=(84, 36, 30), ishita=330, deepak=330, fig=392, logo=0, sub=True, gap=26),
	# X: 1500 x 500. The profile photo covers the lower left, so text sits top left and characters on the right.
	"x": dict(w=1500, h=500, band=(0, 0, 1500, 500), text=(72, 36, 520, 280), align="left",
		size=(64, 26, 26), ishita=640, deepak=70, fig=450, logo=150, sub=False, gap=22),
	# LinkedIn Page: 1512 x 256. The Page logo covers the left 23% from about 40% of the height down (checked on the live Page),
	# so nothing important sits there.
	"linkedin": dict(w=1512, h=256, band=(0, 0, 1512, 256), text=(555, 24, 670, 200), align="center",
		size=(44, 18, 19), ishita=405, deepak=100, fig=246, logo=0, sub=True, gap=12),
	# Reddit: cover photo at least 1280 x 384; built at 1920 x 576 (same 10:3). Avatar sits lower left.
	"reddit": dict(w=1920, h=576, band=(0, 0, 1920, 576), text=(96, 56, 700, 320), align="left",
		size=(76, 30, 32), ishita=880, deepak=110, fig=520, logo=190, sub=False, gap=26),
}

CSS = f"""<link rel="stylesheet" href="{u('css/tfg-comic.css')}"><link rel="stylesheet" href="{u('css/site.css')}">
<style>html,body{{margin:0;background:transparent}}
.art{{position:relative;overflow:hidden;background:#FAF8F2;font-family:var(--font-sans);color:#000}}
.band{{position:absolute}}
.ch{{position:absolute;bottom:0;width:auto;z-index:1}}
.tbl{{position:absolute;left:0;right:0;background:#E4CAB9;border-top:4px solid #000;z-index:2}}
.txt{{position:absolute;z-index:3;display:flex;flex-direction:column;justify-content:center}}
.txt h1{{margin:0;font-weight:800;letter-spacing:-.025em;line-height:1.08}}
.txt p{{margin:0;font-weight:500;color:#4E4B45;line-height:1.3}}
.txt b{{font-weight:700;color:#000}}</style>"""


def banner(spec):
	w, h = spec["w"], spec["h"]
	bx, by, bw, bh = spec["band"]
	tx, ty, tw, th = spec["text"]
	s1, s2, s3 = spec["size"]
	fig = spec["fig"]
	table_top = by + bh - round(bh * 0.075)
	gap = spec["gap"]
	logo = f'<img src="{u("logo/tfg-logo.svg")}" style="width:{spec["logo"]}px;margin-bottom:{gap * 1.4:.0f}px" alt="">' if spec["logo"] else ""
	align = "center" if spec["align"] == "center" else "flex-start"
	return f"""<!doctype html><html><head><meta charset="utf-8">{CSS}</head><body>
<div class="art" style="width:{w}px;height:{h}px">
<div class="band" style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px">
  <img class="ch" src="{u('img/cl-ishita-thinking.webp')}" style="left:{spec['ishita']}px;height:{fig * N['cl-ishita-thinking']:.0f}px" alt="">
  <img class="ch" src="{u('img/dr-coffee.webp')}" style="right:{spec['deepak']}px;height:{fig * N['dr-coffee']:.0f}px" alt="">
</div>
<div class="tbl" style="top:{table_top}px;bottom:0"></div>
<div class="txt" style="left:{tx}px;top:{ty}px;width:{tw}px;height:{th}px;align-items:{align};text-align:{spec['align']}">
  {logo}<h1 style="font-size:{s1}px">{HEADLINE}</h1>
  {f'<p style="font-size:{s2}px;margin-top:{gap}px">{SUB}</p>' if spec["sub"] else ""}
  <p style="font-size:{s3}px;margin-top:{gap}px"><b>{URL}</b></p>
</div></div></body></html>"""


def avatar(out):
	"""Head and steaming mug from Character/Right/Deepak/coffee on paper, padded so a circle crop keeps both (D-025, D-034)."""
	src = Image.open(PUB / "img" / "dr-coffee.webp").convert("RGBA")
	side, x0, y0 = 700, -70, -50
	bg = Image.new("RGBA", (side, side), (250, 248, 242, 255))
	bg.alpha_composite(src, (-x0, -y0))
	bg = bg.convert("RGB")
	for size in (800, 400):
		bg.resize((size, size), Image.LANCZOS).save(out / f"avatar-{size}.png", optimize=True)


async def main(out):
	out.mkdir(parents=True, exist_ok=True)
	avatar(out)
	async with async_playwright() as p:
		browser = await p.chromium.launch(executable_path=os.environ.get("CHROME") or None)
		for name, spec in BANNERS.items():
			html = out / f"banner-{name}.html"
			html.write_text(banner(spec))
			page = await browser.new_page(viewport={"width": spec["w"], "height": spec["h"]})
			await page.goto(html.as_uri())
			await page.evaluate("document.fonts.ready")
			await page.wait_for_timeout(400)
			await page.locator(".art").screenshot(path=str(out / f"banner-{name}.png"))
			await page.close()
			html.unlink()
		# YouTube watermark: the compact mark, 150 x 150, transparent around it.
		page = await browser.new_page(viewport={"width": 150, "height": 150})
		mark = out / "watermark.html"
		mark.write_text(f'<html><body style="margin:0;background:transparent;display:grid;place-items:center;height:150px"><img src="{u("logo/tfg-mark.svg")}" style="height:132px"></body></html>')
		await page.goto(mark.as_uri())
		await page.wait_for_timeout(300)
		mark.unlink()
		await page.screenshot(path=str(out / "youtube-watermark-150.png"), omit_background=True)
		await browser.close()
	# YouTube banner as JPEG keeps it well under the 6 MB limit.
	Image.open(out / "banner-youtube.png").convert("RGB").save(out / "banner-youtube.jpg", quality=92)
	(out / "banner-youtube.png").unlink()


if __name__ == "__main__":
	asyncio.run(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "tools" / "out" / "social")))
