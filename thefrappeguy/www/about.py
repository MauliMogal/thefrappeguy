def get_context(context):
	context.page_title = "About"
	context.page_description = "What The Frappe Guy is, the team in the story, and who writes it."
	context.nav = "about"

	# Profiles set up in Stage 3 (D-126). Handles as in D-100.
	context.socials = [
		("LinkedIn", "https://www.linkedin.com/company/thefrappeguy", "The Frappe Guy"),
		("YouTube", "https://www.youtube.com/@TheFrappeGuy", "@TheFrappeGuy"),
		("Instagram", "https://www.instagram.com/thefrappeguy", "@thefrappeguy"),
		("X", "https://x.com/TheFrappeGuy", "@TheFrappeGuy"),
		("Reddit", "https://www.reddit.com/user/TheFrappeGuy", "u/TheFrappeGuy"),
	]
