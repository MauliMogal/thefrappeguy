def get_context(context):
	context.page_title = "About"
	context.page_description = "What The Frappe Guy is, the team in the story, and who writes it."
	context.nav = "about"

	# Filled in when each profile is set up (Stage 3). Empty URLs are hidden. Handles as in D-100.
	context.socials = [
		("LinkedIn", "", "The Frappe Guy"),
		("YouTube", "", "@TheFrappeGuy"),
		("Instagram", "", "@thefrappeguy"),
		("X", "", "@TheFrappeGuy"),
		("Reddit", "", "u/TheFrappeGuy"),
	]
