def get_context(context):
	context.page_title = "About"
	context.page_description = "Who The Frappe Guy is, who asks the questions, and who runs this site."
	context.nav = "about"
	context.cast = [
		("cl-ishita-thinking", "Ishita", "Runs a company. Asks if this will run hers."),
		("cl-raju-thinking", "Raju", "Sells for a living. Promises a little too much."),
		("cl-saara-thinking", "Sara", "Numbers first. Asks you to prove it."),
		("cl-jammy-thinking", "Joseph", "Writes the code. Asks about the Framework, tells bad jokes."),
		("cl-suman-thinking", "Salman", "New to all of this. Asks what everyone wonders."),
	]

	# Filled in when each profile is live (launch phase 4). Empty URLs are hidden.
	context.socials = [
		("LinkedIn", "", "The Frappe Guy"),
		("YouTube", "", "@thefrappeguy"),
		("Instagram", "", "@thefrappeguy"),
		("X", "", "@thefrappeguy"),
		("Reddit", "https://www.reddit.com/user/thefrappeguy/", "u/thefrappeguy"),
	]
