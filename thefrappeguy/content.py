"""Series, explainers and the brand's copy rules, shared by pages, feeds and DocTypes."""

import re

import frappe

from thefrappeguy import __version__
from thefrappeguy.characters import CHARACTERS

CREDIT = "Characters from the Frappe Character Library, used with permission."

SCENES = ("sky", "periwinkle", "mustard", "salmon", "sage", "grey")

# The six series, in display order. Seeded on install; edit them in the desk afterwards.
SERIES = [
	{
		"slug": "cloud",
		"title": "Frappe Cloud",
		"scene": "sky",
		"description": "Where your Frappe site lives: plans, backups, updates, and what you pay for.",
		"asked_by": "Usually asked by Salman, who is new to all of this.",
		"pose": "dr-thumbsup",
	},
	{
		"slug": "erpnext",
		"title": "ERPNext and business apps",
		"scene": "periwinkle",
		"description": "ERPNext, Frappe HR and Frappe Helpdesk: what each one does for a real business, and where you'll need setup.",
		"asked_by": "Usually asked by Ishita, who runs a company.",
		"pose": "dr-using-ipad",
	},
	{
		"slug": "crm",
		"title": "CRM and selling",
		"scene": "mustard",
		"description": "Frappe CRM and the selling side of ERPNext, from the first lead to a paid invoice.",
		"asked_by": "Usually asked by Raju, who sells for a living.",
		"pose": "dr-idea",
	},
	{
		"slug": "pricing",
		"title": "Pricing and proof",
		"scene": "salmon",
		"description": "What things cost, how the pricing works, and the numbers behind every claim. Each figure is checked against a live source.",
		"asked_by": "Usually asked by Sara, who wants proof.",
		"pose": "dr-book",
	},
	{
		"slug": "framework",
		"title": "Framework and developers",
		"scene": "sage",
		"description": "The Frappe Framework for people who build: DocTypes, hooks, APIs and custom apps.",
		"asked_by": "Usually asked by Joseph, who writes the code.",
		"pose": "dr-laptop",
	},
	{
		"slug": "basics",
		"title": "Basics",
		"scene": "grey",
		"description": "Start here. The words and ideas everything else builds on, explained from zero.",
		"asked_by": "Usually asked by Salman, who asks what everyone wonders.",
		"pose": "dr-thinking",
	},
]

BANNED = [
	"delve",
	"leverage",
	"leverages",
	"leveraging",
	"unlock",
	"unlocks",
	"seamless",
	"seamlessly",
	"robust",
	"game-changer",
	"game changer",
	"elevate",
	"empower",
	"empowers",
	"journey",
	"revolutionize",
	"revolutionise",
	"cutting-edge",
	"cutting edge",
]
_BANNED_RE = [(w, re.compile(r"\b" + re.sub(r"[-\s]", r"[-\\s]", w) + r"\b", re.I)) for w in BANNED]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def copy_issues(text, label):
	"""Brand copy rules: no em or en dashes, no banned words."""
	issues = []
	if not text:
		return issues
	if "\u2014" in text or "\u2013" in text:
		issues.append(f"{label}: replace the dash with a comma, a colon or a new sentence.")
	for word, rx in _BANNED_RE:
		if rx.search(text):
			issues.append(f'{label}: "{word}" is on the banned list.')
	return issues


def word_count(text):
	return len((text or "").split())


def pose_options(prefix):
	return sorted(k for k in CHARACTERS if k.startswith(prefix))


def series_list():
	try:
		rows = frappe.get_all(
			"Explainer Series",
			fields=["name as slug", "title", "scene", "description", "asked_by", "pose"],
			order_by="sort_order asc, creation asc",
		)
	except Exception:
		rows = []
	return rows or [frappe._dict(s) for s in SERIES]


def series_map():
	return {s.slug if hasattr(s, "slug") else s["slug"]: frappe._dict(s) for s in series_list()}


def explainer_list(series=None, limit=None):
	filters = {"published": 1}
	if series:
		filters["series"] = series
	try:
		rows = frappe.get_all(
			"Explainer",
			filters=filters,
			fields=["name as slug", "title", "series", "dek", "card_pose", "published_on", "takeaway", "body", "modified"],
			order_by="published_on desc, creation desc",
			limit_page_length=limit or 0,
		)
	except Exception:
		return []
	smap = series_map()
	for r in rows:
		s = smap.get(r.series) or frappe._dict(title=r.series, scene="grey")
		r.series_title = s.title
		r.scene = s.scene
		r.url = f"/explainers/{r.slug}"
		r.read_minutes = max(1, round(word_count(r.body) / 200))
	return rows


def website_context(context):
	return {
		"tfg_series": series_list(),
		"tfg_base": frappe.utils.get_url().rstrip("/"),
		"tfg_v": __version__,
		"tfg_credit": CREDIT,
	}
