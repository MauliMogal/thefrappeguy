def get_context(context):
	context.page_title = "Brand book"
	context.page_description = "How The Frappe Guy looks, sounds and behaves. The rules are public; the character files are not."
	context.og_image = "/assets/thefrappeguy/og/og-brand.png"
	context.pdf = "/assets/thefrappeguy/brand/the-frappe-guy-brand-book.pdf"
	context.scenes = [
		("tangerine", "#F0A25A", "Frappe 101"),
		("sky", "#4B93E9", "Frappe Cloud"),
		("periwinkle", "#7883E9", "ERPNext"),
		("lilac", "#B391E6", "HR and Payroll"),
		("mustard", "#F5C57D", "CRM"),
		("teal", "#5FC4B4", "Helpdesk"),
		("lime", "#B7CF67", "LMS"),
		("pink", "#EE9CC6", "Raven"),
		("sage", "#789B7A", "Framework"),
		("salmon", "#F37E7E", "Pricing"),
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
