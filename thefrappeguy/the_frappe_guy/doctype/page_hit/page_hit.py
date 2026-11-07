from frappe.model.document import Document


class PageHit(Document):
	"""One page view, counted without cookies (D-196). No IP address, no user agent and no visitor id is stored:
	`visitor` is a one-way hash of address, browser and a random code that changes every day, so it counts
	different visitors within one day and can never be traced back or joined across days."""
