from thefrappeguy.content import explainer_list, series_map
from thefrappeguy.structured import home_ld

no_cache = 0
sitemap = 0


def get_context(context):
	# Start here (D-208): the first release's parts, in story order, as plain links.
	context.start_series = series_map().get("frappe-101")
	context.start = explainer_list(series="frappe-101") if context.start_series else []
	context.og_image = "/assets/thefrappeguy/og/og-home.png"
	context.json_ld = home_ld()
