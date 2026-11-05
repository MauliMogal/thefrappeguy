import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.website.utils import clear_cache

from thefrappeguy.characters import CHARACTERS
from thefrappeguy.content import SLUG_RE, copy_issues, word_count

# Figma component names to the display names approved in D-022
DISPLAY = {"Saara": "Sara", "Jammy": "Joseph", "Suman": "Salman"}


class Explainer(Document):
	def validate(self):
		issues = []
		self.slug = (self.slug or "").strip().lower()
		if not SLUG_RE.match(self.slug):
			issues.append("Slug: use lowercase letters, numbers and single hyphens, like what-is-a-doctype.")

		# A comic-first part (D-157) fills the single-panel fields from its panels, for the card, feed and search.
		if self.panels:
			issues += self.check_panels()
			self.fill_from_panels()

		for field, label in (
			("title", "Title"),
			("dek", "One line under the title"),
			("so_far", "So far"),
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

		if (self.part or 0) < 1:
			issues.append("Part: number the parts of a story from 1.")
		elif self.series and frappe.db.exists(
			"Explainer", {"series": self.series, "part": self.part, "name": ["!=", self.name or ""]}
		):
			issues.append(f"Part: this topic already has a Part {self.part}. Each part number is used once per story.")

		if issues:
			frappe.throw("<br>".join(issues), title="Fix these before saving")

		# "Asked by" always matches the character in the panel, so the page never names the wrong person.
		if self.cast_pose in CHARACTERS:
			name = CHARACTERS[self.cast_pose][0]
			self.asked_by = DISPLAY.get(name, name)

		if not self.preview_key:
			self.preview_key = frappe.generate_hash(length=16)

		if self.published and not self.published_on:
			self.published_on = today()

	def check_panels(self):
		"""The comic grammar, panel by panel: 2 bubbles at most (a caption counts), 20 words each,
		no exclamation marks from The Frappe Guy, and a listening pose never speaks."""
		issues = []
		for p in self.panels:
			n = f"Panel {p.idx}"
			for field, label in (
				("caption", "caption"),
				("thought", "thought"),
				("left_bubble", "left bubble"),
				("right_bubble", "The Frappe Guy's bubble"),
				("text", "text"),
			):
				issues += copy_issues(p.get(field), f"{n}, {label}")
			speech = [p.get(k) for k in ("caption", "thought", "left_bubble", "right_bubble") if p.get(k)]
			if len(speech) > 2:
				issues.append(f"{n}: {len(speech)} bubbles. A panel holds 2 at most, and a caption counts as one.")
			for field in ("caption", "thought", "left_bubble", "right_bubble"):
				if word_count(p.get(field)) > 20:
					issues.append(f"{n}: a bubble has {word_count(p.get(field))} words. Bubbles hold 20 at most.")
			if p.right_bubble and not p.right_pose:
				issues.append(f"{n}: The Frappe Guy has a bubble but is not in the panel.")
			if p.right_bubble and "!" in p.right_bubble:
				issues.append(f"{n}: The Frappe Guy never uses exclamation marks.")
			if p.right_pose == "dr-listen" and p.right_bubble:
				issues.append(f"{n}: The Frappe Guy is listening in this pose, so he can't speak.")
			if p.right_pose in ("dr-no-idea", "dr-tierd") and p.right_bubble:
				issues.append(f"{n}: this pose never gives the answer. Pick another pose.")
			if p.left_pose and not p.left_pose.startswith("cl-"):
				issues.append(f"{n}: the left side is for the cast. The Frappe Guy answers from the right.")
		return issues

	def fill_from_panels(self):
		first = self.panels[0]
		self.cast_pose = first.left_pose
		self.question = first.left_bubble or first.thought or self.title
		if not self.deepak_pose:
			self.deepak_pose = next((p.right_pose for p in self.panels if p.right_pose and p.right_bubble), "dr-coffee")
		self.answer = ""
		self.body = "\n\n".join((p.text or "").strip() for p in self.panels if p.text)

	def on_update(self):
		clear_cache()

	def on_trash(self):
		clear_cache()
