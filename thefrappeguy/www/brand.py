def get_context(context):
	context.page_title = "Brand book"
	context.page_description = "How The Frappe Guy looks, sounds and behaves. The rules are public; the character files are not."
	context.og_image = "/assets/thefrappeguy/og/og-brand.png"
	context.pdf = "/assets/thefrappeguy/brand/the-frappe-guy-brand-book.pdf"
	# Topic colours come from each product's logo on frappe.io/products (D-114). Panels use a softer tint.
	context.scenes = [
		("ink", "#171717", "Frappe 101"),
		("blue", "#0089FF", "ERPNext"),
		("cyan", "#00BAF4", "Frappe Cloud"),
		("yellow", "#E8BE5F", "Pricing"),
		("mint", "#06B58B", "HR and Payroll"),
		("magenta", "#EF0BF5", "CRM"),
		("violet", "#7D3DFF", "Helpdesk"),
		("grey", "#7B808A", "Framework"),
		("green", "#0E7159", "Learning"),
		("orange", "#F08A3C", "Raven"),
	]
	context.neutrals = [
		("Ink", "#000000"),
		("Paper", "#FAF8F2"),
		("White", "#FFFFFF"),
		("Highlight", "#E8BE5F"),
		("Table", "#E4CAB9"),
	]
	context.toc = [
		("core", "Brand core"),
		("characters", "Characters"),
		("comic", "Comic grammar"),
		("look", "Logo, colour and type"),
		("templates", "Templates"),
		("voice", "Voice"),
		("usage", "Usage rules"),
	]
