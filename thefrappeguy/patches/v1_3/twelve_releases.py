"""Twelve releases (D-142, D-145): ERPNext becomes three releases, Pricing follows Frappe Cloud, and every release
carries the line and section titles the roadmap shows. /series/erpnext stays as ERPNext I, so no address moves."""

import frappe

from thefrappeguy.patches.v1_1.ten_series import execute as sync_series


def execute():
	frappe.reload_doc("the_frappe_guy", "doctype", "explainer_series")
	sync_series()
