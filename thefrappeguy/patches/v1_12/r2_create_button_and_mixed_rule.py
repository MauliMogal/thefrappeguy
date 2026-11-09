"""Site 1.12.1 (D-224, 9 Nov 2026): two ERPNext I fixes, reloaded from data/r2_erpnext_1.json.

Part 1 gains the real Create menu on an open quote (Q-68). Part 3 gains two panels: the 50-bag rule counts each
item on its own, so 30 Ethiopian plus 30 House Blend get no discount, unless Mixed Conditions is ticked (Q-69,
tried on the demo site). Every part is saved through Explainer.validate, so every brand check runs."""

import json

import frappe


def execute():
	with open(frappe.get_app_path("thefrappeguy", "data", "r2_erpnext_1.json"), encoding="utf-8") as f:
		data = json.load(f)
	for e in data["explainers"]:
		if e["slug"] not in ("the-order-that-starts-it-all", "cafe-prices-and-online-prices"):
			continue
		if not frappe.db.exists("Explainer", e["slug"]):
			continue
		panels = e.pop("panels")
		doc = frappe.get_doc("Explainer", e["slug"])
		doc.update(e)
		doc.set("panels", [])
		for row in panels:
			doc.append("panels", row)
		doc.save(ignore_permissions=True)
	frappe.db.commit()
