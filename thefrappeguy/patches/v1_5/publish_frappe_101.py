"""Publishes R1 Frappe 101 (Mauli, 5 Nov 2026). Same as ticking Published on each part in the desk:
it saves through Explainer.validate, so every brand check runs and Published on is set."""

import frappe

PARTS = ("who-is-behind-this", "why-it-is-open-source", "everything-frappe-makes")


def execute():
	for slug in PARTS:
		if not frappe.db.exists("Explainer", slug):
			continue
		doc = frappe.get_doc("Explainer", slug)
		if doc.published:
			continue
		doc.published = 1
		doc.save(ignore_permissions=True)
	frappe.db.commit()
