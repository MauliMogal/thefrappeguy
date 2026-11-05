"""Loads R1 Frappe 101 (three comic-first parts) as unpublished drafts. Never overwrites a part that already exists,
so edits made in the desk stay. A part goes live only when someone ticks Published."""

import json

import frappe


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_panel")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	path = frappe.get_app_path("thefrappeguy", "data", "r1_frappe_101.json")
	with open(path, encoding="utf-8") as f:
		data = json.load(f)
	for e in data["explainers"]:
		if frappe.db.exists("Explainer", e["slug"]):
			continue
		if frappe.db.exists("Explainer", {"series": e["series"], "part": e["part"]}):
			continue
		doc = frappe.get_doc({"doctype": "Explainer", **e})
		doc.insert(ignore_permissions=True)
	frappe.db.commit()
