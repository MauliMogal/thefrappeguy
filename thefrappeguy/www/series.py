import frappe

from thefrappeguy.content import explainer_list, series_map


def get_context(context):
	slug = (frappe.form_dict.slug or "").strip().lower()
	series = series_map().get(slug)
	if not series:
		raise frappe.PageDoesNotExistError
	context.series = series
	context.explainers = explainer_list(series=slug)
	context.page_title = series.title
	context.page_description = series.description
	context.nav = "explainers"
	context.og_image = f"/assets/thefrappeguy/og/og-series-{slug}.png"
