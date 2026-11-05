app_name = "thefrappeguy"
app_title = "The Frappe Guy"
app_publisher = "Mauli Mogal"
app_description = "thefrappeguy.com: Frappe, explained simply."
app_email = "hello@thefrappeguy.com"
app_license = "mit"

# The site is the app's own www pages; "/" renders www/index.html.
home_page = "index"

website_route_rules = [
	{"from_route": "/explainers/<slug>", "to_route": "explainer"},
	{"from_route": "/series/<slug>", "to_route": "series"},
]

# Old addresses that moved (D-103)
website_redirects = [
	{"source": "/series/basics", "target": "/series/frappe-101", "redirect_http_status": 301},
]

# rss.xml, sitemap.xml, robots.txt, favicon.ico and site.webmanifest
page_renderer = ["thefrappeguy.renderers.FeedRenderer"]

# Shared values for every page: series list, base URL, asset version
update_website_context = ["thefrappeguy.content.website_context"]

jinja = {
	"methods": [
		"thefrappeguy.jinja.tfg_char",
		"thefrappeguy.jinja.tfg_bubble",
		"thefrappeguy.jinja.tfg_panel",
		"thefrappeguy.jinja.tfg_canonical",
		"thefrappeguy.jinja.tfg_read_minutes",
	]
}

after_install = "thefrappeguy.install.after_install"
after_migrate = "thefrappeguy.install.after_migrate"

# Privacy page: questions are kept for 12 months, then deleted.
scheduler_events = {"daily": ["thefrappeguy.install.delete_old_questions"]}
