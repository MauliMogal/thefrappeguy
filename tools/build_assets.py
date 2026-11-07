"""Regenerates the favicon, the share images and the public brand book PDF.

Everything is composed from the app's own CSS, logo files and character exports. Nothing is drawn.

    pip install playwright pillow && playwright install chromium
    python3 tools/build_assets.py                  # favicon + share images
    python3 tools/build_assets.py --pdf URL        # also prints URL/brand to the brand book PDF

Share images for explainers come from tools/explainers.json. Add an entry, run the script, commit the PNG.\nEvery card carries the character credit (brand core); series cards read the release list from content.py.
"""

import argparse
import os
import asyncio
import json
import pathlib

from PIL import Image
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "thefrappeguy" / "public"
OUT = ROOT / "tools" / "out"

N = {}  # character --n values, from the registry
for line in (ROOT / "thefrappeguy" / "characters.py").read_text().splitlines():
	line = line.strip()
	if line.startswith('"') and "(" in line:
		key = line.split('"')[1]
		N[key] = float(line.split(",")[3])

# The twelve releases, read from the app itself so the cards never drift from the site (D-193).
# content.py imports frappe only for helpers; a stub is enough to read its constants.
import sys
import types

sys.modules.setdefault("frappe", types.ModuleType("frappe"))
sys.path.insert(0, str(ROOT))
from thefrappeguy.content import CREDIT, SERIES  # noqa: E402

SERIES = {s["slug"]: s for s in SERIES}


def u(rel):
	return (PUB / rel).as_uri()


def char(key, style):
	return f'<img class="tfg-char" src="{u("img/" + key + ".webp")}" alt="" data-side="{"right" if key.startswith("dr-") else "left"}" style="--n:{N[key]};{style}">'


HEAD = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{u('css/tfg-comic.css')}"><link rel="stylesheet" href="{u('css/site.css')}">
<style>html,body{{margin:0;background:transparent}} .art{{position:relative;width:1200px;height:630px;overflow:hidden;font-family:var(--font-sans)}}
.art h1{{margin:0}} .url{{position:absolute;left:64px;bottom:48px;font:700 22px/28px var(--font-sans);letter-spacing:-.01em}}</style></head><body>"""


def credit(color="#4E4B45", bottom=24):
	"""The character credit every public asset carries (brand core), bottom left, above the art."""
	return (f'<p style="position:absolute;left:64px;bottom:{bottom}px;z-index:9;margin:0;font:500 15px/20px var(--font-sans);'
		f'color:{color}">{CREDIT}</p>')


def page_home():
	# The headline is About's own line, not the hero, which is still under review (D-166). It says what the site is
	# and claims nothing about The Frappe Guy's character (brand core: never call ourselves honest).
	panel = (
		'<figure class="tfg-panel" style="--letter:23px">'
		f'<img class="tfg-scenery" src="{u("img/env-cafeteria.webp")}" alt="">'
		+ char("cl-ishita-thinking", "--fig:58%;--x:5%")
		+ char("dr-coffee", "--fig:58%;--x:7%")
		+ '<p class="tfg-bubble" data-tail="left" style="left:4%;top:4%;--w:40%;--tail-x:62%">Will this actually run my company?</p>'
		+ '<p class="tfg-bubble" data-tail="right" style="right:4%;top:4%;--w:47%;--tail-x:52%">Tell me what you sell. I\'ll show you how one order moves through ERPNext.</p>'
		+ '<div class="tfg-table"></div></figure>'
	)
	return f"""{HEAD}<div class="art" style="background:#FAF8F2;color:#000">
<img src="{u('logo/tfg-logo.svg')}" style="position:absolute;left:64px;top:56px;width:180px" alt="">
<h1 style="position:absolute;left:64px;top:170px;width:500px;font:800 54px/60px var(--font-sans);letter-spacing:-.02em">Frappe, explained in small comic scenes.</h1>
<div style="position:absolute;right:64px;top:100px;width:520px">{panel}</div>
<p class="url" style="margin:0;bottom:56px">thefrappeguy.com</p>{credit()}</div></body></html>"""


def page_series(slug):
	x = SERIES[slug]
	title, scene, pose, desc = x["title"], x["scene"], x.get("pose") or "dr-thinking", x["description"]
	no = list(SERIES).index(slug) + 1
	ink = scene == "ink"
	logo = "logo/tfg-logo-reverse.svg" if ink else "logo/tfg-logo.svg"
	size = 68 if len(title) <= 16 else 54
	return f"""{HEAD}<div class="art tfg-scene" data-scene="{scene}">
<span class="tfg-dot" style="left:720px;top:90px;--d:22px"></span><span class="tfg-dot" data-dot="blue" style="left:770px;top:132px;--d:13px"></span>
<img src="{u(logo)}" style="position:absolute;left:64px;top:56px;width:180px" alt="">
<div style="position:absolute;left:64px;top:170px;width:640px;display:flex;flex-direction:column;align-items:flex-start;gap:20px">
<span class="tfg-tag" style="--tag-size:34px">Release {no} of {len(SERIES)}</span>
<h1 style="font:800 {size}px/{size + 4}px var(--font-sans);letter-spacing:-.025em">{title}</h1>
<p style="width:560px;margin:0;font:500 24px/32px var(--font-sans)">{desc}</p></div>
{char(pose, "--fig:600px;--x:60px;--y:-70px")}
<p class="url" style="margin:0;bottom:56px">thefrappeguy.com</p>{credit("#FAF8F2" if ink else "#000")}</div></body></html>"""


def page_brand():
	return f"""{HEAD}<div class="art" style="background:#000;color:#FAF8F2">
<div style="position:absolute;left:64px;top:72px"><span class="tfg-tag" style="--tag-size:34px">Brand book</span></div>
<h1 style="position:absolute;left:64px;top:156px;width:640px;font:800 72px/78px var(--font-sans);letter-spacing:-.025em">How The Frappe Guy looks, <span style="color:#E8BE5F">sounds</span> and behaves</h1>
{char("dr-coffee", "--fig:600px;--x:80px;--y:-60px")}
<img src="{u('logo/tfg-logo-reverse.svg')}" style="position:absolute;left:64px;bottom:56px;width:170px" alt="">{credit("#FAF8F2")}</div></body></html>"""


def page_explainer(e):
	title, series_title, pose = e["title"], e["series_title"], e.get("pose", "dr-book")
	tag = f"{series_title} · Part {e['part']}" if e.get("part") else series_title
	size = 104 if len(title) <= 22 else 84
	return f"""{HEAD}<div class="art" style="background:#FAF8F2;color:#000">
<div style="position:absolute;left:64px;top:72px"><span class="tfg-tag" style="--tag-size:36px">{tag}</span></div>
<h1 style="position:absolute;left:64px;top:150px;width:660px;font:700 {size}px/{size - 4}px var(--font-hand);color:#000">{title}</h1>
<p style="position:absolute;left:64px;top:410px;margin:0;font:600 20px/26px var(--font-sans);letter-spacing:.08em;color:#6B675F">THE FRAPPE GUY · {series_title.upper()}</p>
{char(pose, "--fig:560px;--x:70px;--y:-64px")}
<div class="tfg-table" style="height:52px;--bw:4px"></div>
<img src="{u('logo/tfg-logo.svg')}" style="position:absolute;left:64px;bottom:76px;width:150px" alt="">{credit("#000", 15)}</div></body></html>"""


async def shoot(browser, html, path):
	OUT.mkdir(parents=True, exist_ok=True)
	src = OUT / (path.stem + ".html")
	src.write_text(html)
	page = await browser.new_page(viewport={"width": 1200, "height": 630})
	await page.goto(src.as_uri())
	await page.evaluate("document.fonts.ready")
	await page.wait_for_timeout(300)
	await page.locator(".art").screenshot(path=str(path))
	await page.close()


async def favicon(browser):
	pngs = {}
	for size, svg in ((16, "favicon-16.svg"), (32, "favicon-32.svg"), (48, "favicon-32.svg")):
		page = await browser.new_page(viewport={"width": size, "height": size})
		# Load from a file, not set_content: Chrome blocks file:// images on about:blank, which left the
		# 16 px icon blank in 1.1 and 1.2 (D-125). Wait for the image, then refuse to save an empty icon.
		src = OUT / f"fav-{size}.html"
		src.write_text(f'<html><body style="margin:0;background:transparent"><img id="i" src="{u("icons/" + svg)}" style="display:block;width:{size}px;height:{size}px"></body></html>')
		await page.goto(src.as_uri())
		await page.evaluate("document.getElementById('i').decode()")
		p = OUT / f"fav-{size}.png"
		await page.screenshot(path=str(p), omit_background=True)
		img = Image.open(p).convert("RGBA")
		if img.getchannel("A").getextrema()[1] == 0:
			raise SystemExit(f"favicon {size}px rendered blank")
		pngs[size] = img
		await page.close()
	pngs[16].save(PUB / "icons" / "favicon-16.png")
	pngs[32].save(PUB / "icons" / "favicon-32.png")
	pngs[48].save(PUB / "icons" / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[pngs[16], pngs[32]])


async def main(pdf_url):
	OUT.mkdir(parents=True, exist_ok=True)
	async with async_playwright() as p:
		browser = await p.chromium.launch(executable_path=os.environ.get("CHROME") or None)
		await favicon(browser)
		(PUB / "og" / "explainers").mkdir(parents=True, exist_ok=True)
		await shoot(browser, page_home(), PUB / "og" / "og-home.png")
		await shoot(browser, page_brand(), PUB / "og" / "og-brand.png")
		for slug in SERIES:
			await shoot(browser, page_series(slug), PUB / "og" / f"og-series-{slug}.png")
		for e in json.loads((ROOT / "tools" / "explainers.json").read_text()):
			await shoot(browser, page_explainer(e), PUB / "og" / "explainers" / f"{e['slug']}.png")
		if pdf_url:
			page = await browser.new_page()
			await page.goto(pdf_url.rstrip("/") + "/brand", wait_until="networkidle")
			await page.emulate_media(media="print")
			await page.pdf(
				path=str(PUB / "brand" / "the-frappe-guy-brand-book.pdf"),
				format="A4",
				print_background=True,
				margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
			)
		await browser.close()


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("--pdf", help="Base URL of a running site, to print /brand to the PDF")
	asyncio.run(main(ap.parse_args().pdf))
