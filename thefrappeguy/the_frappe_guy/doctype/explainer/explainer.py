import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.website.utils import clear_cache

from thefrappeguy.content import SLUG_RE, copy_issues, word_count


class Explainer(Document):
	def validate(self):
		issues = []
		self.slug = (self.slug or "").strip().lower()
		if not SLUG_RE.match(self.slug):
			issues.append("Slug: use lowercase letters, numbers and single hyphens, like what-is-a-doctype.")

		for field, label in (
			("title", "Title"),
			("dek", "One line under the title"),
			("question", "Asker's bubble"),
			("answer", "Deepak's bubble"),
			("body", "Article"),
			("takeaway", "Takeaway"),
		):
			issues += copy_issues(self.get(field), label)

		for field, label in (("question", "Asker's bubble"), ("answer", "Deepak's bubble")):
			if word_count(self.get(field)) > 20:
				issues.append(f"{label}: {word_count(self.get(field))} words. Bubbles hold 20 at most.")

		if self.answer and "!" in self.answer:
			issues.append("Deepak's bubble: Deepak never uses exclamation marks.")
		if self.deepak_pose == "dr-listen" and self.answer:
			issues.append("Deepak is listening in this pose, so he can't speak. Pick another pose or clear his bubble.")
		if self.deepak_pose in ("dr-no-idea", "dr-tierd") and self.published:
			issues.append("This pose is never the answer panel. Pick another Deepak pose.")

		if issues:
			frappe.throw("<br>".join(issues), title="Fix these before saving")

		if self.published and not self.published_on:
			self.published_on = today()

	def on_update(self):
		clear_cache()

	def on_trash(self):
		clear_cache()
