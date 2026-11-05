import os

import frappe
from frappe.utils import md_to_html
from markupsafe import Markup

from thefrappeguy.content import series_map, story_nav
from thefrappeguy.jinja import tfg_bubble, tfg_caption, tfg_char, tfg_panel, tfg_thought


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
	context.beats = beats(doc) if doc.panels else []
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
