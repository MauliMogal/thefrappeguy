"""The Coffee Company's real Frappe Cloud address (D-215, Mauli, 8 Nov 2026).

Part 5's one-site diagram shows thecoffeecompany.m.frappe.cloud, the site created on Frappe Cloud for the story.
Panels are reloaded from data/r1_stage6.json and saved through Explainer.validate. Safe to run after
v1_11.r1_content_review: it loads the same file."""

from thefrappeguy.patches.v1_11.r1_content_review import execute as reload_r1


def execute():
	reload_r1()
