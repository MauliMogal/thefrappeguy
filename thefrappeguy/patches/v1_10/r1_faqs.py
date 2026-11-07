"""Questions people ask for the five R1 parts (D-206), loaded through Explainer.validate."""

import json

import frappe


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_faq")
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer")
	with open(frappe.get_app_path("thefrappeguy", "data", "r1_faq.json")) as f:
		faqs = json.load(f)["faqs"]
	for slug, rows in faqs.items():
		if not frappe.db.exists("Explainer", slug):
			continue
		doc = frappe.get_doc("Explainer", slug)
		doc.set("faqs", [{"question": q, "answer": a} for q, a in rows])
		doc.flags.ignore_permissions = True
		doc.save()
	frappe.db.commit()
