"""Series, explainers and the brand's copy rules, shared by pages, feeds and DocTypes."""

import re

import frappe

from thefrappeguy import __version__
from thefrappeguy.characters import CHARACTERS

CREDIT = "Characters from the Frappe Character Library, used with permission."

SCENES = ("tangerine", "sky", "periwinkle", "lilac", "mustard", "teal", "lime", "pink", "sage", "salmon")

# The ten series, in display order. Seeded on install and synced by the v1_1 patch; edit them in the desk afterwards.
SERIES = [
	{
		"slug": "frappe-101",
		"title": "Frappe 101",
		"scene": "tangerine",
		"description": "Start here. What Frappe is, and what a site, an app and a DocType are, explained from zero.",
		"asked_by": "Usually asked by Salman, who is new to all of this.",
		"pose": "dr-thinking",
	},
	{
		"slug": "cloud",
		"title": "Frappe Cloud",
		"scene": "sky",
		"description": "Where your Frappe site lives: sites, plans, backups and updates.",
		"asked_by": "Usually asked by Ishita, who wants her company's data safe.",
		"pose": "dr-thumbsup",
	},
	{
		"slug": "erpnext",
		"title": "ERPNext",
		"scene": "periwinkle",
		"description": "Accounting, stock, buying, selling and manufacturing, and how they fit a real business.",
		"asked_by": "Usually asked by Ishita, who runs a company.",
		"pose": "dr-using-ipad",
	},
	{
		"slug": "hr",
		"title": "HR and Payroll",
		"scene": "lilac",
		"description": "Frappe HR: employees, leave, attendance, expense claims and payroll.",
		"asked_by": "Usually asked by Ishita, who hires faster than she can file paperwork.",
		"pose": "dr-coffee-offer",
	},
	{
		"slug": "crm",
		"title": "CRM",
		"scene": "mustard",
		"description": "Frappe CRM, from the first lead to a closed deal.",
		"asked_by": "Usually asked by Raju, who sells for a living.",
		"pose": "dr-idea",
	},
	{
		"slug": "helpdesk",
		"title": "Helpdesk",
		"scene": "teal",
		"description": "Frappe Helpdesk: tickets, teams and replying to customers on time.",
		"asked_by": "Usually asked by Raju, whose customers call him first.",
		"pose": "dr-work-talk",
	},
	{
		"slug": "lms",
		"title": "LMS",
		"scene": "lime",
		"description": "Frappe Learning: courses, quizzes and certificates for your team or your customers.",
		"asked_by": "Usually asked by Salman, who learns by doing.",
		"pose": "dr-accomplished",
	},
	{
		"slug": "raven",
		"title": "Raven",
		"scene": "pink",
		"description": "Team chat that runs on your Frappe site, with your users, roles and documents in the conversation.",
		"asked_by": "Usually asked by Joseph, who lives in chat.",
		"pose": "dr-laughing",
	},
	{
		"slug": "framework",
		"title": "Framework",
		"scene": "sage",
		"description": "DocTypes, hooks, APIs and custom apps, for people who build on Frappe.",
		"asked_by": "Usually asked by Joseph, who writes the code.",
		"pose": "dr-laptop",
	},
	{
		"slug": "pricing",
		"title": "Pricing",
		"scene": "salmon",
		"description": "What things cost and how the pricing works. Every figure is checked against a live source.",
		"asked_by": "Usually asked by Sara, who wants proof.",
		"pose": "dr-book",
	},
]

# Old series slugs that now live elsewhere. Used by the redirect hook and the v1_1 patch.
RENAMED_SERIES = {"basics": "frappe-101"}

BANNED = [
	# Never claim it, show it (D-102)
	"honest",
	"honestly",
	"unbiased",
	"no sales pitch",
	"costs a sale",
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
		s = smap.get(r.series) or frappe._dict(title=r.series, scene="tangerine")
		r.series_title = s.title
		r.scene = s.scene
		r.url = f"/explainers/{r.slug}"
		r.read_minutes = max(1, round(word_count(r.body) / 200))
	return rows


def series_counts():
	"""Published explainers per series, so empty series can say "Coming soon"."""
	try:
		rows = frappe.get_all("Explainer", filters={"published": 1}, fields=["series", "count(name) as n"], group_by="series")
	except Exception:
		return {}
	return {r.series: r.n for r in rows}


def series_with_counts():
	counts = series_counts()
	out = []
	for s in series_list():
		s = frappe._dict(s)
		s.count = counts.get(s.slug, 0)
		out.append(s)
	return out


def website_context(context):
	return {
		"tfg_series": series_with_counts(),
		"tfg_base": frappe.utils.get_url().rstrip("/"),
		"tfg_v": __version__,
		"tfg_credit": CREDIT,
	}
