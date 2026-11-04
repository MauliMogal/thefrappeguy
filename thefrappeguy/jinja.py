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
	css = f"--n:{n};" + (f"--drop:{drop};" if drop else "") + (style or "")
	attrs = ' data-baked-table=""' if drop else ""
	loading = ' loading="lazy"' if lazy else ""
	return Markup(
		f'<img class="tfg-char" src="{IMG}{key}.webp" alt="{escape(name)}, {escape(pose.replace("-", " "))}" '
		f'data-character="{escape(name)}" data-pose="{escape(pose)}" data-side="{side}"{attrs} '
		f'style="{escape(css)}"{loading} decoding="async">'
	)


def tfg_bubble(text, side="right", style=""):
	if not text:
		return Markup("")
	return Markup(f'<p class="tfg-bubble" data-tail="{side}" style="{escape(style)}">{escape(text)}</p>')


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
