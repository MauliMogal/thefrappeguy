"""ERPNext I, five parts with real screens from The Coffee Company's site (D-216 to D-222, Stage 8, 8 Nov 2026).

Adds the screen shot and the chain and capability diagrams to Explainer Panel, syncs the ERPNext I section titles
and description from content.py, creates or updates the five parts from data/r2_erpnext_1.json and publishes them.
Every part is saved through Explainer.validate, so every brand check runs. R1 Part 1's one-record diagram now says
the order promises the bags (D-221), so Frappe 101 and ERPNext I agree."""

import json

import frappe

from thefrappeguy.content import SERIES


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_panel")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_series")

	for s in SERIES:
		if s["slug"] == "erpnext" and frappe.db.exists("Explainer Series", "erpnext"):
			frappe.db.set_value("Explainer Series", "erpnext", {"sections": s["sections"], "description": s["description"]})

	with open(frappe.get_app_path("thefrappeguy", "data", "r2_erpnext_1.json"), encoding="utf-8") as f:
		data = json.load(f)
	for e in data["explainers"]:
		panels = e.pop("panels")
		if frappe.db.exists("Explainer", e["slug"]):
			doc = frappe.get_doc("Explainer", e["slug"])
			doc.update(e)
		else:
			doc = frappe.get_doc({"doctype": "Explainer", **e, "published": 1})
		doc.set("panels", [])
		for row in panels:
			doc.append("panels", row)
		doc.save(ignore_permissions=True)

	if frappe.db.exists("Explainer", "what-is-an-erp"):
		doc = frappe.get_doc("Explainer", "what-is-an-erp")
		changed = False
		for p in doc.panels:
			if p.diagram_labels and "Stock: one bag less" in p.diagram_labels:
				p.diagram_labels = p.diagram_labels.replace("Stock: one bag less", "Stock: bags promised")
				changed = True
		if changed:
			doc.save(ignore_permissions=True)
	frappe.db.commit()
