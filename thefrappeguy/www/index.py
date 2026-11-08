from thefrappeguy.structured import home_ld

no_cache = 0
sitemap = 0


def get_context(context):
	context.og_image = "/assets/thefrappeguy/og/og-home.png"
	context.json_ld = home_ld()
