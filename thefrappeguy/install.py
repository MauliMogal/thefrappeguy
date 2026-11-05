import frappe
from frappe.utils import add_months, now_datetime

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


def delete_old_questions():
	"""Deletes questions older than 12 months, as the Privacy page promises. Runs daily."""
	cutoff = add_months(now_datetime(), -12)
	for name in frappe.get_all("Question", filters={"creation": ["<", cutoff]}, pluck="name"):
		frappe.delete_doc("Question", name, ignore_permissions=True, force=True)
	frappe.db.commit()
