"""The three ERPNext releases are called ERPNext 1, 2 and 3 (D-203, Mauli, 7 Nov 2026). The long names wrapped
badly in "Other releases" and on the home grid; each release's description still says what it covers."""

import frappe

TITLES = {"erpnext": "ERPNext 1", "erpnext-stock": "ERPNext 2", "erpnext-accounts": "ERPNext 3"}


def execute():
	for slug, title in TITLES.items():
		if frappe.db.exists("Explainer Series", slug):
			frappe.db.set_value("Explainer Series", slug, "title", title, update_modified=False)
	frappe.db.commit()
