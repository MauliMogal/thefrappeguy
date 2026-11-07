import frappe
from frappe.model.document import Document
from frappe.utils import today
from frappe.website.utils import clear_cache

from thefrappeguy.characters import CHARACTERS
from thefrappeguy.content import DIAGRAM_TEMPLATES, SLUG_RE, copy_issues, parse_diagram, word_count

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

		issues += self.check_faqs()

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

	def check_faqs(self):
		"""Questions people ask (D-206): 5 at most, a question of 15 words, an answer of 60, the same copy rules as the comic."""
		issues = []
		if len(self.faqs or []) > 5:
			issues.append(f"Questions: {len(self.faqs)}. Keep 5 at most, the ones readers actually ask.")
		for q in self.faqs or []:
			n = f"Question {q.idx}"
			issues += copy_issues(q.question, n)
			issues += copy_issues(q.answer, f"{n}, answer")
			if word_count(q.question) > 15:
				issues.append(f"{n}: {word_count(q.question)} words. 15 at most.")
			if word_count(q.answer) > 60:
				issues.append(f"{n}, answer: {word_count(q.answer)} words. 60 at most.")
			if q.question and not q.question.strip().endswith("?"):
				issues.append(f"{n}: end it with a question mark.")
		return issues

	def check_panels(self):
		"""The comic grammar, panel by panel: 2 bubbles at most (a caption counts), 20 words each,
		no exclamation marks from The Frappe Guy, and a listening pose never speaks.
		Full comic (D-166, D-168): small panels hold 6 words per item, one sticker per part,
		wide panels stay silent, and a pose with the table drawn in needs the table.
		Stage 6 (D-180): a caption alone in its panel may hold 30 words, and a diagram panel has no characters,
		one caption at most and labels of 4 words, 16 at most."""
		issues = []
		stickers = [p.idx for p in self.panels if p.sticker]
		if len(stickers) > 1:
			issues.append(f"Stickers on panels {', '.join(map(str, stickers))}. One sticker per part at most.")
		for p in self.panels:
			n = f"Panel {p.idx}"
			shot = p.shot or "medium"
			if shot == "diagram":
				if p.left_pose or p.right_pose:
					issues.append(f"{n}: a diagram has no characters. Clear the poses.")
				if p.thought or p.left_bubble or p.right_bubble:
					issues.append(f"{n}: a diagram holds one caption and no bubbles.")
				if p.diagram_template not in DIAGRAM_TEMPLATES:
					issues.append(f"{n}: pick a diagram template.")
				groups = parse_diagram(p.diagram_labels)
				labels = [g["title"] for g in groups] + [x for g in groups for x in g["items"]]
				if not groups:
					issues.append(f"{n}: add the diagram labels, a # title line and - item lines.")
				if len(labels) > 16:
					issues.append(f"{n}: {len(labels)} diagram labels. 16 at most.")
				for label in labels:
					if word_count(label) > 4:
						issues.append(f"{n}: the label '{label}' has {word_count(label)} words. Labels hold 4 at most.")
				issues += copy_issues(p.diagram_labels, f"{n}, diagram labels")
			elif not p.left_pose and not p.right_pose:
				issues.append(f"{n}: pick at least one character.")
			if p.left_bubble and not p.left_pose:
				issues.append(f"{n}: the left bubble needs someone on the left.")
			if p.thought and not p.left_pose:
				issues.append(f"{n}: thoughts belong to the cast member on the left.")
			if shot == "small":
				for field in ("caption", "thought", "left_bubble", "right_bubble"):
					if word_count(p.get(field)) > 6:
						issues.append(f"{n}: small panels hold 6 words per item; this one has {word_count(p.get(field))}.")
			if shot == "wide" and any(p.get(k) for k in ("caption", "thought", "left_bubble", "right_bubble")):
				issues.append(f"{n}: wide panels stay silent. On a phone they are too short to read (D-168).")
			if shot == "flat":
				for pose in (p.left_pose, p.right_pose):
					if pose in CHARACTERS and CHARACTERS[pose][4]:
						issues.append(f"{n}: {pose} has a table drawn in, so it can't sit on a flat ground.")
			if p.sticker == "ww" and shot not in ("flat", "close"):
				issues.append(f"{n}: W W goes on a close-up.")
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
				# A caption alone in its panel is narration and may hold 30 words (G1, D-180).
				limit = 30 if field == "caption" and len(speech) == 1 else 20
				if word_count(p.get(field)) > limit:
					issues.append(f"{n}: a bubble has {word_count(p.get(field))} words. This one holds {limit} at most.")
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
		first = next((p for p in self.panels if p.left_pose), self.panels[0])
		if first.left_pose:
			self.cast_pose = first.left_pose
		self.question = first.left_bubble or first.thought or self.title
		if not self.deepak_pose:
			self.deepak_pose = next((p.right_pose for p in self.panels if p.right_pose and p.right_bubble), "dr-coffee")
		self.answer = ""
		texts = [(p.text or "").strip() for p in self.panels if p.text]
		# A full comic has no text between panels, so the feed, search and card read the comic's own words.
		self.body = "\n\n".join(texts) if texts else self.transcript()

	def transcript(self):
		"""The comic as plain text, panel by panel: captions, thoughts and who said what."""
		lines = []
		for p in self.panels:
			left = DISPLAY.get(CHARACTERS[p.left_pose][0], CHARACTERS[p.left_pose][0]) if p.left_pose in CHARACTERS else ""
			if p.caption:
				lines.append(p.caption.strip())
			if (p.shot or "") == "diagram":
				for g in parse_diagram(p.diagram_labels):
					lines.append(f"{g['title']}: " + "; ".join(g["items"]) + ".")
			if p.thought:
				lines.append(f"{left} thinks: {p.thought.strip()}")
			if p.left_bubble:
				lines.append(f"{left}: {p.left_bubble.strip()}")
			if p.right_bubble:
				lines.append(f"The Frappe Guy: {p.right_bubble.strip()}")
		return "\n\n".join(lines) or self.title

	def on_update(self):
		clear_cache()

	def on_trash(self):
		clear_cache()
