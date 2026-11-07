"""Private page counts for Mauli (D-196). System Managers only; never cached, never indexed, not in the sitemap."""

import frappe
from frappe.utils import add_days, today

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/stats"
		raise frappe.Redirect
	if "System Manager" not in frappe.get_roles():
		raise frappe.PermissionError

	days = frappe.utils.cint(frappe.form_dict.get("days")) or 30
	days = days if days in (1, 7, 30, 90, 365) else 30
	since = add_days(today(), -(days - 1))
	def grouped(field, n=15):
		# field comes from this file, never from the request
		return frappe.db.sql(
			f"""select `{field}`, count(*) as views, count(distinct visitor) as people from `tabPage Hit`
			where day >= %s group by `{field}` order by views desc limit {int(n)}""", since, as_dict=True)

	context.days = days
	context.choices = (1, 7, 30, 90, 365)
	context.views = frappe.db.count("Page Hit", {"day": [">=", since]})
	context.people = frappe.db.sql("select count(distinct day, visitor) from `tabPage Hit` where day >= %s", since)[0][0]
	context.daily = frappe.db.sql(
		"""select day, count(*) as views, count(distinct visitor) as people from `tabPage Hit`
		where day >= %s group by day order by day desc""", since, as_dict=True)
	context.peak = max([d.views for d in context.daily] or [1])
	context.pages = grouped("path")
	context.sources = grouped("source")
	context.campaigns = [c for c in grouped("campaign") if c.campaign]
	context.devices = grouped("device", 3)
	context.signups = frappe.db.count("Subscriber", {"creation": [">=", since]})
	context.questions = frappe.db.count("Question", {"creation": [">=", since]})
	context.page_title = "Stats"
	context.no_index = 1
