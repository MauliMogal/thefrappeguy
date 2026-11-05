import frappe
from frappe.model.document import Document
from frappe.website.utils import clear_cache

from thefrappeguy.content import SLUG_RE, copy_issues


class ExplainerSeries(Document):
	def validate(self):
		self.slug = (self.slug or "").strip().lower()
		issues = []
		if not SLUG_RE.match(self.slug):
			issues.append("Slug: use lowercase letters, numbers and single hyphens.")
		for field, label in (("title", "Title"), ("description", "Description"), ("asked_by", "Who usually asks"), ("decision", "What the reader can decide"), ("sections", "Section titles")):
			issues += copy_issues(self.get(field), label)
		if issues:
			frappe.throw("<br>".join(issues), title="Fix these before saving")

	def on_update(self):
		clear_cache()
