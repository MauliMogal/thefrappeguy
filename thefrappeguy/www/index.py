from thefrappeguy.content import explainer_list
from thefrappeguy.structured import home_ld

no_cache = 0
sitemap = 0


def get_context(context):
	context.explainers = explainer_list(limit=3, latest=True)
	context.og_image = "/assets/thefrappeguy/og/og-home.png"
	context.json_ld = home_ld()
