"""Puts the ten topics in story order with their product colours (D-114, D-116), and numbers any existing explainers as parts."""

import frappe

from thefrappeguy.patches.v1_1.ten_series import execute as sync_series


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_series")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	sync_series()
	# Explainers written before parts existed: number them in publishing order within each topic.
	for series in frappe.get_all("Explainer Series", pluck="name"):
		rows = frappe.get_all(
			"Explainer", filters={"series": series}, fields=["name", "part"], order_by="published_on asc, creation asc"
		)
		for i, r in enumerate(rows, start=1):
			if not r.part or r.part < 1:
				frappe.db.set_value("Explainer", r.name, "part", i, update_modified=False)
	frappe.db.commit()
