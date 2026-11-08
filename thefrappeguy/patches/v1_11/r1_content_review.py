"""R1 content review fixes (D-214, Mauli, 8 Nov 2026).

Part 1 panel 17 gives payroll to Frappe HR, not ERPNext. Part 2 panel 17 says how to visit the farm. Part 3 gains a
panel that answers "Is it free?". Part 4 no longer says Frappe Cloud does the setup, gains a panel on taking your
records with you, is straight about changing partners and points to the cost chapter. Part 5 explains CRM, names the
Frappe Framework and drops the builders' diagram, the WHOA and the stack caption. Panels are reloaded from
data/r1_stage6.json and saved through Explainer.validate, so every brand check runs. Published state and part
numbers are left as they are live."""

import json

import frappe


def execute():
	path = frappe.get_app_path("thefrappeguy", "data", "r1_stage6.json")
	with open(path, encoding="utf-8") as f:
		data = json.load(f)

	for e in data["explainers"]:
		if not frappe.db.exists("Explainer", e["slug"]):
			continue
		doc = frappe.get_doc("Explainer", e["slug"])
		doc.set("panels", [])
		for row in e["panels"]:
			doc.append("panels", row)
		doc.save(ignore_permissions=True)
	frappe.db.commit()
