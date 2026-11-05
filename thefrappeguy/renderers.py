"""Feeds and small files at the site root: rss.xml, sitemap.xml, robots.txt, favicon.ico, site.webmanifest."""

import json
from datetime import timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

import frappe
from frappe.utils import get_datetime, get_url
from frappe.website.page_renderers.base_renderer import BaseRenderer

from thefrappeguy.content import explainer_list, series_list

STATIC_ROUTES = ["", "explainers", "roadmap", "about", "ask", "brand", "privacy"]


class FeedRenderer(BaseRenderer):
	ROUTES = ("rss.xml", "sitemap.xml", "robots.txt", "favicon.ico", "site.webmanifest")

	def can_render(self):
		return self.path in self.ROUTES

	def render(self):
		if self.path == "rss.xml":
			return self.respond(rss(), "application/rss+xml; charset=utf-8")
		if self.path == "sitemap.xml":
			return self.respond(sitemap(), "application/xml; charset=utf-8")
		if self.path == "robots.txt":
			return self.respond(robots(), "text/plain; charset=utf-8")
		if self.path == "site.webmanifest":
			return self.respond(manifest(), "application/manifest+json; charset=utf-8")
		return self.respond(favicon(), "image/x-icon")

	def respond(self, data, content_type):
		response = self.build_response(data, 200, {"Cache-Control": "public, max-age=3600"})
		response.headers["Content-Type"] = content_type
		return response


def base():
	return get_url().rstrip("/")


def rss():
	b = base()
	items = []
	for e in explainer_list(limit=50, latest=True):
		when = get_datetime(e.published_on or e.modified)
		desc = " ".join(x for x in [e.dek, e.takeaway] if x)
		items.append(
			"<item>"
			f"<title>{escape(e.title)}</title>"
			f"<link>{b}{e.url}</link>"
			f'<guid isPermaLink="true">{b}{e.url}</guid>'
			f"<pubDate>{format_datetime(when.replace(tzinfo=timezone.utc))}</pubDate>"
			f"<category>{escape(e.series_title or '')}</category>"
			f"<description>{escape(desc)}</description>"
			"</item>"
		)
	return (
		'<?xml version="1.0" encoding="UTF-8"?>\n'
		'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
		"<title>The Frappe Guy</title>"
		f"<link>{b}/</link>"
		f'<atom:link href="{b}/rss.xml" rel="self" type="application/rss+xml"/>'
		"<description>Learn Frappe the easy way: follow one company as it finds out whether Frappe can run its business, in short comic parts on ERPNext, Frappe Cloud, pricing and more.</description>"
		"<language>en-in</language>"
		+ "".join(items)
		+ "</channel></rss>"
	)


def sitemap():
	b = base()
	urls = [f"{b}/{r}" if r else f"{b}/" for r in STATIC_ROUTES]
	urls += [f"{b}/series/{s.slug}" for s in series_list()]
	rows = [(u, None) for u in urls]
	rows += [(f"{b}{e.url}", get_datetime(e.modified).date().isoformat()) for e in explainer_list()]
	body = "".join(
		f"<url><loc>{escape(u)}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>" for u, d in rows
	)
	return (
		'<?xml version="1.0" encoding="UTF-8"?>\n'
		f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
	)


def robots():
	return "\n".join(
		[
			"User-agent: *",
			"Allow: /",
			"Disallow: /app",
			"Disallow: /api",
			"Disallow: /login",
			f"Sitemap: {base()}/sitemap.xml",
			"",
		]
	)


def manifest():
	icons = "/assets/thefrappeguy/icons/"
	return json.dumps(
		{
			"name": "The Frappe Guy",
			"short_name": "tfg",
			"start_url": "/",
			"display": "browser",
			"background_color": "#FAF8F2",
			"theme_color": "#FAF8F2",
			"icons": [
				{"src": icons + "icon-192.png", "sizes": "192x192", "type": "image/png"},
				{"src": icons + "icon-512.png", "sizes": "512x512", "type": "image/png"},
			],
		}
	)


def favicon():
	path = frappe.get_app_path("thefrappeguy", "public", "icons", "favicon.ico")
	with open(path, "rb") as f:
		return f.read()
