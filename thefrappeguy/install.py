import frappe

from thefrappeguy.content import SERIES


def after_install():
	seed_series()
	frappe.db.commit()


def after_migrate():
	seed_series()


def seed_series():
	"""Creates the six series if they don't exist. Never overwrites edits made in the desk."""
	for i, s in enumerate(SERIES):
		if frappe.db.exists("Explainer Series", s["slug"]):
			continue
		frappe.get_doc({"doctype": "Explainer Series", "sort_order": i + 1, **s}).insert(ignore_permissions=True)
