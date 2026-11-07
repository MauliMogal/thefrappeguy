"""The three ERPNext releases are called ERPNext I, II and III, and each description starts with what the
release covers (D-205, Mauli, 7 Nov 2026). Replaces the 1, 2, 3 names of v1_9.short_erpnext_titles."""

import frappe

from thefrappeguy.content import SERIES

SLUGS = ("erpnext", "erpnext-stock", "erpnext-accounts")


def execute():
	for s in SERIES:
		if s["slug"] in SLUGS and frappe.db.exists("Explainer Series", s["slug"]):
			frappe.db.set_value(
				"Explainer Series",
				s["slug"],
				{"title": s["title"], "description": s["description"]},
				update_modified=False,
			)
	frappe.db.commit()
