import os
from html import escape

import frappe
from frappe.utils import md_to_html
from markupsafe import Markup

from thefrappeguy.content import series_map, story_nav
from thefrappeguy.jinja import tfg_bubble, tfg_caption, tfg_char, tfg_diagram, tfg_panel, tfg_thought
from thefrappeguy.structured import explainer_ld


def get_context(context):
	slug = (frappe.form_dict.slug or "").strip().lower()
	if not slug or not frappe.db.exists("Explainer", slug):
		raise frappe.PageDoesNotExistError
	doc = frappe.get_doc("Explainer", slug)

	# An unpublished part opens only with its preview key, is never cached, and is never indexed.
	key = (frappe.form_dict.preview or "").strip()
	context.is_preview = False
	if not doc.published:
		if not key or not doc.preview_key or key != doc.preview_key:
			raise frappe.PageDoesNotExistError
		context.is_preview = True
		context.no_cache = 1

	series = series_map().get(doc.series) or frappe._dict(title=doc.series, slug=doc.series, scene="ink")
	context.doc = doc
	context.series = series
	context.body_html = md_to_html(doc.body or "")
	full_comic = bool(doc.panels) and not any((p.text or "").strip() for p in doc.panels)
	context.comic = comic(doc) if full_comic else None
	context.comic_sources = comic_sources(doc) if full_comic else []
	context.beats = beats(doc) if doc.panels and not full_comic else []
	context.page_title = doc.title
	context.page_description = doc.dek
	context.og_type = "article"
	context.nav = "explainers"
	generated = frappe.get_app_path("thefrappeguy", "public", "og", "explainers", f"{slug}.png")
	og_series = frappe.get_app_path("thefrappeguy", "public", "og", f"og-series-{series.slug}.png")
	if doc.og_image:
		context.og_image = doc.og_image
	elif os.path.exists(generated):
		context.og_image = f"/assets/thefrappeguy/og/explainers/{slug}.png"
	elif os.path.exists(og_series):
		context.og_image = f"/assets/thefrappeguy/og/og-series-{series.slug}.png"
	else:
		context.og_image = "/assets/thefrappeguy/og/og-home.png"

	if not context.is_preview:
		context.json_ld = explainer_ld(doc, series, context.og_image)

	if context.is_preview:
		context.prev_part, context.next_part = draft_nav(doc, series)
	else:
		context.prev_part, context.next_part = story_nav(slug)


def draft_nav(doc, series):
	"""Previous and next part within the release, drafts included, each with its own preview key."""
	rows = frappe.get_all(
		"Explainer",
		filters={"series": doc.series},
		fields=["name", "title", "part", "published", "preview_key", "series"],
		order_by="part asc",
	)
	for r in rows:
		r.url = f"/explainers/{r.name}" + ("" if r.published else f"?preview={r.preview_key}")
		r.series_title = series.title
		r.scene = series.scene
	names = [r.name for r in rows]
	i = names.index(doc.name)
	return (rows[i - 1] if i > 0 else None), (rows[i + 1] if i + 1 < len(rows) else None)


def beats(doc):
	"""Panel, text, panel, text (D-157). Each panel is placed by the registry's --n, one --fig per panel."""
	env = doc.environment if doc.environment and doc.environment != "none" else None
	out = []
	for p in doc.panels:
		speech = sum(1 for k in ("caption", "thought", "left_bubble", "right_bubble") if p.get(k))
		fig = "60%" if speech >= 2 else "64%"
		off = 13 if p.caption else 0
		inner = Markup("")
		if p.right_pose:
			inner += tfg_char(p.left_pose, f"--fig:{fig};--x:5%") + tfg_char(p.right_pose, f"--fig:{fig};--x:4%")
		else:
			inner += tfg_char(p.left_pose, f"--fig:{fig};--x:10%")
		inner += tfg_caption(p.caption)
		inner += tfg_thought(p.thought, f"right:4%;top:{off + 6}%;--w:50%;--letter:4.2cqw")
		inner += tfg_bubble(p.left_bubble, "left", f"left:3%;top:{3 + off}%;--w:47%;--tail-x:64%")
		rtop = p.right_bubble_top or (f"{13 + off}%" if p.left_bubble else f"{4 + off}%")
		rw = p.right_bubble_width or "47%"
		inner += tfg_bubble(p.right_bubble, "right", f"right:3%;top:{rtop};--w:{rw};--tail-x:58%")
		sources = [s.strip() for s in (p.sources or "").splitlines() if s.strip()]
		out.append(
			frappe._dict(
				panel=tfg_panel(inner, env),
				text=Markup(md_to_html(p.text or "")),
				sources=[(s, s.replace("https://", "").replace("http://", "")) for s in sources],
			)
		)
	return out


# ---- Full comic (D-166, D-168, D-172): the panels carry everything; sources follow the last panel ----

# Shot defaults: fig (how tall a large pose stands, as a share of panel height), x and y offsets.
SHOTS = {
	"medium": {"fig": None, "x": "8%", "y": "0%"},
	"close": {"fig": "104%", "x": "5%", "y": "-16%"},
	"flat": {"fig": "112%", "x": "6%", "y": "-30%"},
	"small": {"fig": "76%", "x": "10%", "y": "0%"},
	"wide": {"fig": "128%", "x": "6%", "y": "-30%"},
	"diagram": {"fig": None, "x": "8%", "y": "0%"},
	"screen": {"fig": None, "x": "8%", "y": "0%"},
}


def screen_panel(p, lazy=False):
	"""A real screen from The Coffee Company's site (D-216): caption on top, the screen below, tap for full size."""
	load = ' loading="lazy"' if lazy else ""
	src = escape(p.screen_image or "")
	cap = Markup(f'<p class="tfg-screen-cap">{escape(p.caption)}</p>') if p.caption else Markup("")
	img = Markup(
		f'<a class="tfg-screen" href="{src}" target="_blank" rel="noopener">'
		f'<img src="{src}" alt="{escape(p.screen_alt or "")}" decoding="async"{load}></a>'
	)
	return Markup('<figure class="tfg-panel" data-shot="screen">') + cap + img + Markup("</figure>")


def comic_panel(p, env, lazy=False):
	if p.shot == "screen":
		return screen_panel(p, lazy)
	shot = p.shot if p.shot in SHOTS else "medium"
	d = SHOTS[shot]
	items = sum(1 for k in ("caption", "thought", "left_bubble", "right_bubble") if p.get(k))
	both = p.left_bubble and p.right_bubble
	# A long reply sits higher and both figures stand a little lower, so it never covers a face (D-184).
	long_reply = both and len(p.right_bubble.split()) > 11
	fig = d["fig"] or ("52%" if long_reply else "56%" if both else "60%" if items >= 2 else "64%")
	y = d["y"]
	# Panels below the first screen load as the reader scrolls to them (D-195).
	load = ' loading="lazy"' if lazy else ""
	full = shot in ("close", "flat")
	inner = Markup("")
	if shot in ("medium", "close", "small") and env and not p.plain_paper:
		inner += Markup(f'<img class="tfg-scenery" src="/assets/thefrappeguy/img/{env}.webp" alt="" decoding="async"{load}>')
	if p.sticker == "ww":
		inner += Markup('<img class="tfg-sticker st-ww" src="/assets/thefrappeguy/img/st-ww.webp" alt="W W">')
	if p.left_pose and p.right_pose:
		inner += tfg_char(p.left_pose, f"--fig:{fig};--x:5%;--y:{y}", lazy, full) + tfg_char(p.right_pose, f"--fig:{fig};--x:4%;--y:{y}", lazy, full)
	elif p.left_pose:
		inner += tfg_char(p.left_pose, f"--fig:{fig};--x:{d['x']};--y:{y}", lazy, full)
	elif p.right_pose:
		inner += tfg_char(p.right_pose, f"--fig:{fig};--x:{d['x']};--y:{y}", lazy, full)
	if p.sticker == "whoa":
		inner += Markup(f'<img class="tfg-sticker st-whoa" src="/assets/thefrappeguy/img/st-whoa.webp" alt="WHOA!"{load}>')
	if shot == "diagram":
		inner += tfg_diagram(p.diagram_template, p.diagram_labels)

	stack = Markup("")
	if p.caption:
		# A caption alone in its panel is narration (G1, D-180): full width, a little larger.
		narration = items == 1 and len(p.caption.split()) > 14 and shot != "diagram"
		stack += Markup(f'<p class="tfg-caption{" is-narration" if narration else ""}">{escape(p.caption)}</p>')
	lone_left = p.left_pose and not p.right_pose
	# One speaks while the other listens: the bubble may use two thirds of the width (D-184).
	solo = bool(p.left_pose and p.right_pose) and bool(p.left_bubble) != bool(p.right_bubble)
	if p.left_bubble:
		stack += bubble(p.left_bubble, "left", "is-across" if lone_left else "is-wide" if solo else "")
	if p.thought:
		stack += tfg_thought(p.thought)
	if p.right_bubble:
		cls = ("is-reply is-high" if long_reply else "is-reply") if p.left_bubble else "is-wide" if solo else ""
		stack += bubble(p.right_bubble, "right", cls)
	if stack:
		inner += Markup(f'<div class="tfg-stack{" has-cap" if p.caption else ""}">') + stack + Markup("</div>")
	if shot not in ("flat", "diagram"):
		inner += Markup('<div class="tfg-table"></div>')
	dg = f' data-dg="{escape(p.diagram_template)}"' if shot == "diagram" and p.diagram_template else ""
	return Markup(f'<figure class="tfg-panel" data-shot="{shot}"{dg}>') + inner + Markup("</figure>")


def bubble(text, side, cls=""):
	long = " data-long" if len(text.split()) > 14 else ""
	klass = f"tfg-bubble {cls}".strip()
	return Markup(f'<p class="{klass}" data-tail="{side}"{long}>{escape(text)}</p>')


def comic(doc):
	"""Panels in order; consecutive panels that share a row name sit side by side."""
	env = doc.environment if doc.environment and doc.environment != "none" else None
	out, rows = Markup(""), list(doc.panels)
	i = 0
	while i < len(rows):
		row = (rows[i].row or "").strip()
		if row:
			group = Markup("")
			while i < len(rows) and (rows[i].row or "").strip() == row:
				group += comic_panel(rows[i], env, lazy=i >= 2)
				i += 1
			out += Markup('<div class="comic-row">') + group + Markup("</div>")
		else:
			out += comic_panel(rows[i], env, lazy=i >= 2)
			i += 1
	return out


def comic_sources(doc):
	seen = []
	for p in doc.panels:
		for s in (p.sources or "").splitlines():
			s = s.strip()
			if s and s not in seen:
				seen.append(s)
	return [(s, s.replace("https://", "").replace("http://", "")) for s in seen]
