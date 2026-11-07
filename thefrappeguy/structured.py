"""Structured data (schema.org JSON-LD) for search engines and AI answer tools (D-206).

Only facts the page already shows: the title, the one-line summary, dates, the share image, the author,
the breadcrumb and the page's own questions. Google stopped showing FAQ rich results in May 2026, but it
and other search and AI tools still read this markup to understand a page."""

import json

import frappe
from markupsafe import Markup

from thefrappeguy.content import MAULI_LINKS

SITE = "The Frappe Guy"


def base():
	return frappe.utils.get_url().rstrip("/")


def as_script(graph):
	"""One JSON-LD block, safe inside a script tag."""
	text = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
	return Markup(text.replace("</", "<\\/"))


def author():
	b = base()
	return {
		"@type": "Person",
		"@id": f"{b}/about#mauli",
		"name": "Mauli Mogal",
		"url": f"{b}/about",
		"sameAs": [url for _key, _label, url in MAULI_LINKS if url.startswith("http")],
	}


def website():
	b = base()
	return {
		"@type": "WebSite",
		"@id": f"{b}/#website",
		"name": SITE,
		"url": f"{b}/",
		"description": "Learn Frappe the easy way: follow one company as it finds out whether Frappe can run its business, in short comic parts.",
		"inLanguage": "en-IN",
		"publisher": {"@id": f"{b}/about#mauli"},
	}


def home_ld():
	return as_script([website(), author()])


def explainer_ld(doc, series, og_image):
	b = base()
	url = f"{b}/explainers/{doc.name}"
	image = og_image if og_image.startswith("http") else b + og_image
	graph = [
		{
			"@type": "Article",
			"@id": f"{url}#article",
			"headline": doc.title,
			"description": doc.dek,
			"url": url,
			"mainEntityOfPage": url,
			"image": image,
			"inLanguage": "en-IN",
			"datePublished": str(doc.published_on) if doc.published_on else None,
			"dateModified": str(doc.modified)[:10],
			"author": {"@id": f"{b}/about#mauli"},
			"publisher": {"@id": f"{b}/about#mauli"},
			"isPartOf": {"@id": f"{b}/#website"},
			"about": ["Frappe", "ERPNext"],
		},
		{
			"@type": "BreadcrumbList",
			"itemListElement": [
				{"@type": "ListItem", "position": 1, "name": "Explainers", "item": f"{b}/explainers"},
				{"@type": "ListItem", "position": 2, "name": series.title, "item": f"{b}/series/{series.slug}"},
				{"@type": "ListItem", "position": 3, "name": doc.title, "item": url},
			],
		},
		website(),
		author(),
	]
	graph[0] = {k: v for k, v in graph[0].items() if v is not None}
	faqs = [q for q in (doc.get("faqs") or []) if q.question and q.answer]
	if faqs:
		graph.append(
			{
				"@type": "FAQPage",
				"@id": f"{url}#questions",
				"url": url,
				"mainEntity": [
					{"@type": "Question", "name": q.question, "acceptedAnswer": {"@type": "Answer", "text": q.answer}}
					for q in faqs
				],
			}
		)
	return as_script(graph)
