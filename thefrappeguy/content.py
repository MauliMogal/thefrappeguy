"""Series, explainers and the brand's copy rules, shared by pages, feeds and DocTypes."""

import re

import frappe

from thefrappeguy import __version__
from thefrappeguy.characters import CHARACTERS

CREDIT = "Characters from the Frappe Character Library, used with permission."

# One scene per topic, taken from that product's own logo on frappe.io/products (D-114).
# Frappe 101 uses Frappe's black. Pricing has no product, so it uses the library's highlight yellow.
# Raven's logo is black like Frappe's, so Raven takes orange to keep the two apart.
SCENES = ("ink", "blue", "cyan", "yellow", "mint", "magenta", "violet", "grey", "green", "orange")

# The story, in reading order: twelve releases (D-142, D-145). ERPNext is told in three releases (R2 to R4),
# and Pricing follows Frappe Cloud. Each release is one story told in parts; the last part hands over to the next.
# "decision" is what a reader can decide after the release; "sections" are its part titles, one per line (story.md 3.1).
# R2's "Selling online" stays off until Q-34 is decided.
# Seeded on install and synced by patches; edit them in the desk afterwards.
SERIES = [
	{
		"slug": "frappe-101",
		"title": "Frappe 101",
		"scene": "ink",
		"description": "What an ERP is, who makes Frappe, why its code is open, what happens if you leave, and what Frappe makes. The story starts here.",
		"asked_by": "Ishita wants to know who is behind the software before she trusts it with her company.",
		"pose": "dr-coffee-offer",
		"decision": "Whether you can trust the people who build Frappe.",
		"sections": "What is an ERP?\nWho is behind this?\nWhy it is open source\nWhat if we want to leave?\nEverything Frappe makes",
	},
	{
		"slug": "erpnext",
		"title": "ERPNext I: Buying and selling",
		"scene": "blue",
		"description": "One order followed from the first quote to the money in the bank, and how the beans get bought in the first place.",
		"asked_by": "Raju sells the bags. Ishita buys the beans.",
		"pose": "dr-using-ipad",
		"decision": "Whether ERPNext can run how The Coffee Company buys beans and sells bags, to cafes and online.",
		"sections": "The order that starts it all\nCafe prices and online prices\nBuying green beans\nWhat an imported bean really costs",
	},
	{
		"slug": "erpnext-stock",
		"title": "ERPNext II: Stock and the roastery",
		"scene": "blue",
		"description": "Green beans in, packed bags out: warehouses, batches, roasting as manufacturing and quality checks.",
		"asked_by": "Ishita wants to know what happens to the beans once they arrive.",
		"pose": "dr-thinking",
		"decision": "Whether ERPNext can run the roastery, from green bean to packed bag.",
		"sections": "Beans in, bags out\nOne coffee, many bags\nBatches and best-before\nRoasting is manufacturing\nFrom plan to batch\nQuality before it ships\nWhen packing happens outside",
	},
	{
		"slug": "erpnext-accounts",
		"title": "ERPNext III: Accounts, GST and reports",
		"scene": "blue",
		"description": "The books that write themselves from every order, GST on every invoice, and reports you can open down to the document.",
		"asked_by": "Sara wants to see the money.",
		"pose": "dr-book",
		"decision": "Whether the books, GST and reports come out right without retyping.",
		"sections": "The accounts write themselves\nGST on every invoice\nE-invoices and e-way bills\nGetting paid, and matching the bank\nReports you can trust\nWhere do we start?",
	},
	{
		"slug": "cloud",
		"title": "Frappe Cloud",
		"scene": "cyan",
		"description": "Where the company's system lives, who keeps it running, and what happens on a bad day.",
		"asked_by": "Joseph asks what every IT person loses sleep over.",
		"pose": "dr-thumbsup",
		"decision": "Where the system runs, and what is handled for you.",
		"sections": "Where does it run?\nSites and benches\nBackups and bad days\nUpdates without fear\nAdding apps later",
	},
	{
		"slug": "pricing",
		"title": "Pricing",
		"scene": "yellow",
		"description": "What the company will actually pay, line by line. Every figure is checked against a live source.",
		"asked_by": "Sara wants every number proved.",
		"pose": "dr-book",
		"decision": "What running ERPNext on Frappe Cloud costs, all in, over the years.",
		"sections": "What you are paying for\nAdding a person\nThe Cloud plans\nWhat implementation costs\nThe five year view",
	},
	{
		"slug": "hr",
		"title": "HR and Payroll",
		"scene": "mint",
		"description": "Frappe HR for a growing team: people, leave, attendance, expense claims and the first payroll run.",
		"asked_by": "Ishita hires faster than she can file paperwork.",
		"pose": "dr-listen",
		"decision": "Whether it can run hiring, attendance and Indian payroll.",
		"sections": "Everyone in one place\nLeave and attendance\nThe first payroll run\nRaju's expense claims\nHR in your pocket",
	},
	{
		"slug": "crm",
		"title": "CRM",
		"scene": "magenta",
		"description": "Frappe CRM, from the first lead to a won deal that turns into an order without retyping.",
		"asked_by": "Raju wants to sell faster. The Frappe Guy wants his promises written down.",
		"pose": "dr-idea",
		"decision": "Whether it can track every lead and promise until it becomes an order.",
		"sections": "Leads, not sticky notes\nThe pipeline\nPromises in writing\nFrom won deal to order",
	},
	{
		"slug": "helpdesk",
		"title": "Helpdesk",
		"scene": "violet",
		"description": "Frappe Helpdesk for the day an order goes wrong: tickets, response times and a reply that points to the real order.",
		"asked_by": "Salman takes the first complaint.",
		"pose": "dr-work-talk",
		"decision": "Whether every complaint can get an owner and an answer.",
		"sections": "Tickets, not inboxes\nWho answers, and how fast\nAnswers customers find themselves\nFixing the order behind the ticket",
	},
	{
		"slug": "framework",
		"title": "Framework",
		"scene": "grey",
		"description": "What to do when the company needs something the apps do not do yet: DocTypes, custom fields, scripts and apps.",
		"asked_by": "Joseph writes the code and asks what breaks on upgrade.",
		"pose": "dr-laptop",
		"decision": "Whether you can change it when it doesn't fit, without breaking upgrades.",
		"sections": "Everything is a DocType\nA new field, no code\nRules and approvals\nWhen you do need code\nWill upgrades break it?",
	},
	{
		"slug": "learning",
		"title": "Learning",
		"scene": "green",
		"description": "Frappe Learning: courses, quizzes and certificates to train a team and its partners.",
		"asked_by": "Salman builds the first course.",
		"pose": "dr-accomplished",
		"decision": "Whether you can train partner cafes on the same system.",
		"sections": "Courses for partner cafes\nLessons, quizzes, certificates\nWho finished what",
	},
	{
		"slug": "raven",
		"title": "Raven",
		"scene": "orange",
		"description": "Team chat on the same Frappe site, so a question about an order sits next to the order.",
		"asked_by": "Joseph moves the team off five different chat groups.",
		"pose": "dr-laughing",
		"decision": "Whether the whole team can work in one place.",
		"sections": "Chat on the same site\nTalk about a document\nGo live",
	},
]

# The story's frame (D-115). A fictional company; the characters come from Frappe's Character Library.
STORY_PREMISE = (
	"Ishita runs The Coffee Company. It roasts beans, packs them and sells to cafes and online, "
	"and it has outgrown its spreadsheets. Her team is deciding whether Frappe can run the business. "
	"The Frappe Guy helps them build it, one question at a time."
)

# (pose key, public name, role at the company, one line)
CAST = [
	("dr-coffee", "The Frappe Guy", "", "Knows Frappe from the inside and builds the system with the team. Answers with a real example."),
	("cl-ishita-thinking", "Ishita", "Founder and CEO", "Started the company. Wants to know if this will really run it."),
	("cl-raju-thinking", "Raju", "Sales", "Brings in the cafes. Promises a little too much."),
	("cl-saara-thinking", "Sara", "Finance and data", "Numbers first. Asks you to prove it."),
	("cl-jammy-thinking", "Joseph", "Tech", "Keeps everything running. Asks what breaks, and tells bad jokes."),
	("cl-suman-thinking", "Salman", "Design", "New to business software. Asks what everyone else is afraid to ask."),
]

# Old series slugs that now live elsewhere. Used by the redirect hook and the v1_1 patch.
RENAMED_SERIES = {"basics": "frappe-101", "lms": "learning"}

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
	# voice.md: "simply" and "just" get deleted; "simply" is checked (D-161)
	"simply",
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


# Mauli's own profiles for the About page (D-187, D-189): (icon key, label, url). Icon keys: linkedin, youtube,
# instagram, x, reddit, website, email. An empty list hides the sign-off links.
MAULI_LINKS = [
	("website", "maulimogal.com", "https://maulimogal.com/"),
	("linkedin", "LinkedIn", "https://www.linkedin.com/in/maulimogal/"),
	("email", "maulimogal@gmail.com", "mailto:maulimogal@gmail.com"),
]

DIAGRAM_TEMPLATES = ("one-record", "timeline", "closed-open", "lock-in", "family", "one-site")


def parse_diagram(text):
	"""Diagram labels (D-180): '# Title' starts a group, '- item' adds to it. Returns [{title, items}]."""
	groups = []
	for line in (text or "").splitlines():
		line = line.strip()
		if line.startswith("#"):
			groups.append({"title": line.lstrip("#").strip(), "items": []})
		elif line.startswith("-") and groups:
			groups[-1]["items"].append(line[1:].strip())
	return groups


def word_count(text):
	return len((text or "").split())


def pose_options(prefix):
	return sorted(k for k in CHARACTERS if k.startswith(prefix))


def series_list():
	try:
		rows = frappe.get_all(
			"Explainer Series",
			fields=["name as slug", "title", "scene", "description", "asked_by", "pose", "decision", "sections"],
			order_by="sort_order asc, creation asc",
		)
	except Exception:
		rows = []
	return rows or [frappe._dict(s) for s in SERIES]


def series_map():
	return {s.slug if hasattr(s, "slug") else s["slug"]: frappe._dict(s) for s in series_list()}


def explainer_list(series=None, limit=None, latest=False):
	"""Published explainers. Story order (topic, then part) unless latest=True asks for newest first."""
	filters = {"published": 1}
	if series:
		filters["series"] = series
	try:
		rows = frappe.get_all(
			"Explainer",
			filters=filters,
			fields=["name as slug", "title", "series", "part", "dek", "card_pose", "published_on", "takeaway", "body", "modified"],
			order_by="published_on desc, creation desc",
			limit_page_length=0,
		)
	except Exception:
		return []
	smap = series_map()
	order = {slug: i for i, slug in enumerate(smap)}
	for r in rows:
		s = smap.get(r.series) or frappe._dict(title=r.series, scene="ink")
		r.series_title = s.title
		r.scene = s.scene
		r.url = f"/explainers/{r.slug}"
		r.read_minutes = max(1, round(word_count(r.body) / 200))
	if not latest:
		rows.sort(key=lambda r: (order.get(r.series, 99), r.part or 0))
	return rows[:limit] if limit else rows


def story_nav(slug):
	"""Previous and next part in reading order. The last part of a topic leads into the first part of the next one."""
	rows = explainer_list()
	names = [r.slug for r in rows]
	if slug not in names:
		return None, None
	i = names.index(slug)
	prev = rows[i - 1] if i > 0 else None
	nxt = rows[i + 1] if i + 1 < len(rows) else None
	return prev, nxt


def series_counts():
	"""Published explainers per series, so empty series can say "Coming soon"."""
	# Counted in Python: Frappe v16 refuses SQL functions written as strings in fields.
	try:
		rows = frappe.get_all("Explainer", filters={"published": 1}, pluck="series")
	except Exception:
		return {}
	counts = {}
	for series in rows:
		counts[series] = counts.get(series, 0) + 1
	return counts


def series_with_counts():
	counts = series_counts()
	out = []
	for s in series_list():
		s = frappe._dict(s)
		s.count = counts.get(s.slug, 0)
		# A release is complete when every planned section is published; then it only offers "Read".
		s.total = len([t for t in (s.sections or "").splitlines() if t.strip()])
		s.complete = bool(s.total) and s.count >= s.total
		out.append(s)
	return out


def website_context(context):
	return {
		"tfg_series": series_with_counts(),
		"tfg_base": frappe.utils.get_url().rstrip("/"),
		"tfg_v": __version__,
		"tfg_credit": CREDIT,
		"tfg_cast": CAST,
		"tfg_premise": STORY_PREMISE,
	}
