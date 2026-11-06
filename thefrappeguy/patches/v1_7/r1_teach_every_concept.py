"""R1 Frappe 101 rewritten to teach every concept (D-174, D-176 to D-184, Mauli, 6 Nov 2026).

Five parts instead of three: What is an ERP? (new), Who is behind this?, Why it is open source,
What if we want to leave? (new), Everything Frappe makes. The three live addresses stay. Every part is saved
through Explainer.validate, so every brand check runs. A new part is published when the release's first live part
is, so the release never shows a gap. The Frappe 101 and ERPNext I section titles follow story.md 3.2 (D-177)."""

import json

import frappe

from thefrappeguy.content import SERIES


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_panel")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_series")

	for s in SERIES:
		if s["slug"] in ("frappe-101", "erpnext") and frappe.db.exists("Explainer Series", s["slug"]):
			frappe.db.set_value("Explainer Series", s["slug"], {"sections": s["sections"], "description": s["description"]})

	path = frappe.get_app_path("thefrappeguy", "data", "r1_stage6.json")
	with open(path, encoding="utf-8") as f:
		data = json.load(f)

	# Part numbers change (Who is behind this? becomes Part 2), so park the live ones first: each number is used once.
	for name in frappe.get_all("Explainer", filters={"series": "frappe-101"}, pluck="name"):
		frappe.db.set_value("Explainer", name, "part", 100 + (frappe.db.get_value("Explainer", name, "part") or 0))

	live = frappe.db.get_value("Explainer", "who-is-behind-this", "published") if frappe.db.exists(
		"Explainer", "who-is-behind-this") else 0

	for e in data["explainers"]:
		panels = e.pop("panels")
		if frappe.db.exists("Explainer", e["slug"]):
			doc = frappe.get_doc("Explainer", e["slug"])
			doc.update(e)
		else:
			doc = frappe.get_doc({"doctype": "Explainer", **e, "published": live})
		doc.set("panels", [])
		for row in panels:
			doc.append("panels", row)
		doc.save(ignore_permissions=True)
	frappe.db.commit()
