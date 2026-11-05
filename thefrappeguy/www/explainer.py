import os

import frappe
from frappe.utils import md_to_html

from thefrappeguy.content import series_map, story_nav


def get_context(context):
	slug = (frappe.form_dict.slug or "").strip().lower()
	if not slug or not frappe.db.exists("Explainer", {"name": slug, "published": 1}):
		raise frappe.PageDoesNotExistError
	doc = frappe.get_doc("Explainer", slug)
	series = series_map().get(doc.series) or frappe._dict(title=doc.series, slug=doc.series, scene="ink")
	context.doc = doc
	context.series = series
	context.body_html = md_to_html(doc.body or "")
	context.page_title = doc.title
	context.page_description = doc.dek
	context.og_type = "article"
	context.nav = "explainers"
	generated = frappe.get_app_path("thefrappeguy", "public", "og", "explainers", f"{slug}.png")
	if doc.og_image:
		context.og_image = doc.og_image
	elif os.path.exists(generated):
		context.og_image = f"/assets/thefrappeguy/og/explainers/{slug}.png"
	else:
		context.og_image = f"/assets/thefrappeguy/og/og-series-{series.slug}.png"
	context.prev_part, context.next_part = story_nav(slug)
