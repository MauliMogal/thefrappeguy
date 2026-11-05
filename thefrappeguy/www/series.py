import os

import frappe

from thefrappeguy.content import explainer_list, series_map


def get_context(context):
	slug = (frappe.form_dict.slug or "").strip().lower()
	series = series_map().get(slug)
	if not series:
		raise frappe.PageDoesNotExistError
	context.series = series
	slugs = list(series_map())
	i = slugs.index(slug)
	context.topic_no = i + 1
	context.next_series = series_map().get(slugs[i + 1]) if i + 1 < len(slugs) else None
	context.explainers = explainer_list(series=slug)
	total = len([t for t in (series.sections or "").splitlines() if t.strip()])
	context.series_complete = bool(total) and len(context.explainers) >= total
	context.page_title = series.title
	context.page_description = series.description
	context.nav = "explainers"
	# Releases added in 1.3 have no share image until tools/build_assets.py is run again; fall back to the home image.
	og = f"og/og-series-{slug}.png"
	exists = os.path.exists(frappe.get_app_path("thefrappeguy", "public", og))
	context.og_image = f"/assets/thefrappeguy/{og}" if exists else "/assets/thefrappeguy/og/og-home.png"
