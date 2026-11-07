"""R1 pre-launch fixes (D-192, Mauli, 7 Nov 2026).

Part 1 panel 5 no longer contradicts panels 2 and 9; Part 4 panel 3 no longer makes leaving an ERP sound free;
no cast member uses the library's Left `doubtful` pose, which points out of the frame; Part 5 panel 16 is a close-up,
so Joseph is not clipped. Panels are reloaded from data/r1_stage6.json and saved through Explainer.validate, so every
brand check runs. Published state and part numbers are left as they are live."""

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
