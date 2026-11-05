"""Template helpers. Characters are placed from the library exports only, by their --n."""

from html import escape

import frappe
from markupsafe import Markup

from thefrappeguy.characters import CHARACTERS, ENVIRONMENTS

IMG = "/assets/thefrappeguy/img/"


def tfg_char(key, style="", lazy=False):
	"""One character export, sized by the registry. Never flipped, never drawn."""
	if key not in CHARACTERS:
		return Markup("")
	name, pose, side, n, drop = CHARACTERS[key]
	# In public copy the hero is The Frappe Guy; "Deepak" is the library's component name only (D-107).
	public = "The Frappe Guy" if name == "Deepak" else name
	css = f"--n:{n};" + (f"--drop:{drop};" if drop else "") + (style or "")
	attrs = ' data-baked-table=""' if drop else ""
	loading = ' loading="lazy"' if lazy else ""
	return Markup(
		f'<img class="tfg-char" src="{IMG}{key}.webp" alt="{escape(public)}, {escape(pose.replace("-", " "))}" '
		f'data-character="{escape(name)}" data-pose="{escape(pose)}" data-side="{side}"{attrs} '
		f'style="{escape(css)}"{loading} decoding="async">'
	)


def tfg_bubble(text, side="right", style=""):
	if not text:
		return Markup("")
	# Long bubbles (over 14 words) letter a little smaller, so the bubble ends above the faces.
	if len(text.split()) > 14 and "--letter" not in (style or ""):
		style = "--letter:3.9cqw;" + (style or "")
	return Markup(f'<p class="tfg-bubble" data-tail="{side}" style="{escape(style)}">{escape(text)}</p>')


# The library's thought cloud: 12 scallops and two trailing circles toward the thinker on the left.
_CLOUD = (
	"M100.0 10.0 A26.4 26.4 0 0 1 145.0 16.7 A21.9 21.9 0 0 1 177.9 35.0 A16.1 16.1 0 0 1 190.0 60.0 "
	"A16.1 16.1 0 0 1 177.9 85.0 A21.9 21.9 0 0 1 145.0 103.3 A26.4 26.4 0 0 1 100.0 110.0 "
	"A26.4 26.4 0 0 1 55.0 103.3 A21.9 21.9 0 0 1 22.1 85.0 A16.1 16.1 0 0 1 10.0 60.0 "
	"A16.1 16.1 0 0 1 22.1 35.0 A21.9 21.9 0 0 1 55.0 16.7 A26.4 26.4 0 0 1 100.0 10.0 Z"
)


def tfg_thought(text, style=""):
	if not text:
		return Markup("")
	return Markup(
		f'<p class="tfg-thought" data-tail="left" style="{escape(style)}">'
		f'<svg viewBox="0 0 200 120" preserveAspectRatio="none" aria-hidden="true"><path d="{_CLOUD}"/>'
		'<circle cx="40" cy="132" r="8"/><circle cx="24" cy="150" r="5"/></svg>'
		f"{escape(text)}</p>"
	)


def tfg_caption(text):
	"""Narration in the panel's top-left corner, no tail (D-158). Counts toward the 2-bubble limit."""
	if not text:
		return Markup("")
	return Markup(f'<p class="tfg-caption">{escape(text)}</p>')


def tfg_panel(inner, env="env-cafeteria", table=True, extra=""):
	scenery = (
		f'<img class="tfg-scenery" src="{IMG}{env}.webp" alt="" decoding="async">' if env in ENVIRONMENTS else ""
	)
	strip = '<div class="tfg-table"></div>' if table else ""
	return Markup(f'<figure class="tfg-panel"{extra}>{scenery}{inner}{strip}</figure>')


def tfg_canonical():
	"""The address of this page as the visitor asked for it, so route-rule pages get their real URL."""
	path = ""
	try:
		path = frappe.local.request.path or ""
	except Exception:
		path = ""
	path = "/" + path.strip("/")
	if path in ("/index", "/"):
		path = "/"
	return frappe.utils.get_url().rstrip("/") + (path if path != "/" else "/")


def tfg_read_minutes(text):
	return max(1, round(len((text or "").split()) / 200))
