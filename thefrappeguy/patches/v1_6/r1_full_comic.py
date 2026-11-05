"""R1 Frappe 101 becomes a full comic (D-166, Mauli, 5 Nov 2026). Replaces the panels of the three R1 parts
with the full-comic panels from data/r1_full_comic.json. Each part is saved through Explainer.validate, so every
brand check runs; Published stays as it is."""

import json

import frappe


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_panel")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	path = frappe.get_app_path("thefrappeguy", "data", "r1_full_comic.json")
	with open(path, encoding="utf-8") as f:
		data = json.load(f)
	for e in data["explainers"]:
		if not frappe.db.exists("Explainer", e["slug"]):
			continue
		doc = frappe.get_doc("Explainer", e["slug"])
		doc.set("panels", [])
		for row in e["panels"]:
			doc.append("panels", row)
		doc.environment = e["environment"]
		doc.takeaway = e["takeaway"]
		doc.save(ignore_permissions=True)
	frappe.db.commit()
