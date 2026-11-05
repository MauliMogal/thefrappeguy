"""Moves the site from six series to ten (D-103): renames Basics to Frappe 101, retitles and recolours the rest, adds the new ones."""

import frappe

from thefrappeguy.content import RENAMED_SERIES, SERIES


def execute():
	for old, new in RENAMED_SERIES.items():
		if frappe.db.exists("Explainer Series", old) and not frappe.db.exists("Explainer Series", new):
			frappe.rename_doc("Explainer Series", old, new, force=True)
			frappe.db.set_value("Explainer Series", new, "slug", new)
		elif frappe.db.exists("Explainer Series", old):
			for name in frappe.get_all("Explainer", filters={"series": old}, pluck="name"):
				frappe.db.set_value("Explainer", name, "series", new)
			frappe.delete_doc("Explainer Series", old, force=True)

	for i, s in enumerate(SERIES):
		values = {"sort_order": i + 1, **{k: v for k, v in s.items() if k != "slug"}}
		if frappe.db.exists("Explainer Series", s["slug"]):
			frappe.db.set_value("Explainer Series", s["slug"], values)
		else:
			frappe.get_doc({"doctype": "Explainer Series", "slug": s["slug"], **values}).insert(ignore_permissions=True)
	frappe.db.commit()
