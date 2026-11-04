import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, validate_email_address


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def ask(question=None, area=None, full_name=None, email=None, may_publish=0, website=None):
	"""Saves a question from /ask as a Question record. `website` is a hidden trap field for bots."""
	if website:
		return {"ok": True}

	question = (question or "").strip()
	if len(question) < 10:
		frappe.throw("Write your question in a sentence or two, then send it.")
	if len(question) > 4000:
		frappe.throw("That's a long one. Please keep it under 4,000 characters.")

	email = (email or "").strip()
	if email and not validate_email_address(email):
		frappe.throw("That email address doesn't look right. Check it, or leave it empty.")

	if area and not frappe.db.exists("Explainer Series", area):
		area = None

	frappe.get_doc(
		{
			"doctype": "Question",
			"question": question,
			"area": area,
			"full_name": (full_name or "").strip()[:140],
			"email": email,
			"may_publish": cint(may_publish),
		}
	).insert(ignore_permissions=True)
	return {"ok": True}
