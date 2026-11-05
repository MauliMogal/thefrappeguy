def get_context(context):
	context.page_title = "About"
	context.page_description = "What The Frappe Guy is, who asks the questions, and who writes the explainers."
	context.nav = "about"
	context.cast = [
		("cl-ishita-thinking", "Ishita", "Runs a company. Asks if this will run hers."),
		("cl-raju-thinking", "Raju", "Sells for a living. Promises a little too much."),
		("cl-saara-thinking", "Sara", "Numbers first. Asks you to prove it."),
		("cl-jammy-thinking", "Joseph", "Writes the code. Asks about the Framework, tells bad jokes."),
		("cl-suman-thinking", "Salman", "New to all of this. Asks what everyone wonders."),
	]

	# Filled in when each profile is set up (Stage 3). Empty URLs are hidden. Handles as in D-100.
	context.socials = [
		("LinkedIn", "", "The Frappe Guy"),
		("YouTube", "", "@TheFrappeGuy"),
		("Instagram", "", "@thefrappeguy"),
		("X", "", "@TheFrappeGuy"),
		("Reddit", "", "u/TheFrappeGuy"),
	]
