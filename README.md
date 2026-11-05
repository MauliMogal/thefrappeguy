# The Frappe Guy

The Frappe app behind **thefrappeguy.com**: learn Frappe the easy way by following one fictional business, The Coffee Company, through twelve releases: Frappe 101, ERPNext (in three releases), Frappe Cloud, Pricing, HR and Payroll, CRM, Helpdesk, Framework, Learning and Raven. Run by Mauli Mogal, Sales @ Frappe.

The site is the brand system's "comic on a quiet page": pages stay ink and paper, and all colour comes from Deepak and the cast of Frappe's Character Library.

## What's in the app

| Part | Where | What it does |
|---|---|---|
| Pages | `thefrappeguy/www/` | Home, explainers index, release pages (`/series/<slug>`), the roadmap, explainer article, About, Ask, Brand book, Privacy, 404. All extend `templates/tfg_base.html`; no Frappe website chrome or desk JavaScript is loaded. |
| Routes | `hooks.py` | `/explainers/<slug>` and `/series/<slug>` route to `www/explainer` and `www/series`. The site is light only. |
| Content | DocTypes in module **The Frappe Guy** | **Explainer** (one numbered part of a topic's story: question, panel, article, takeaway), **Explainer Series** (the twelve releases: scene colour, what a reader can decide, and section titles for the roadmap), **Question** (what people send from /ask). |
| Brand checks | `content.py`, `explainer.py` | Saving an explainer or a release fails on em or en dashes, banned words (including "simply"), bubbles over 20 words, exclamation marks from Deepak, or a pose that can't do the job. |
| Feeds | `renderers.py` | `/rss.xml`, `/sitemap.xml`, `/robots.txt`, `/favicon.ico`, `/site.webmanifest`. |
| Ask form | `api.py` | `thefrappeguy.api.ask`: guest POST, 5 per hour per IP, a hidden trap field for bots. |
| Assets | `thefrappeguy/public/` | Fonts (Inter, Caveat, JetBrains Mono, all OFL), logo kit, favicons, share images, the public brand book PDF, and the character exports. |
| Tools | `tools/` | Scripts that regenerate the share images, the favicon and the brand book PDF from the site itself. Not loaded by the app. |

## Install

On Frappe Cloud: add this repository to the bench as an app, deploy, then install `thefrappeguy` on the site. The twelve releases are created on install. On an older site, `v1_1.ten_series` and `v1_2.story_order` move it to the story order, number existing explainers as parts and redirect `/series/basics` and `/series/lms`; `v1_3.twelve_releases` splits ERPNext into three releases (`/series/erpnext` stays as ERPNext I) and fills in the roadmap fields.

Locally:

```bash
bench get-app https://github.com/MauliMogal/the-frappe-guy
bench --site yoursite install-app thefrappeguy
```

## Writing an explainer

Desk → **Explainer** → New. Fill the card, the comic panel (asker on the left, Deepak on the right), the article in Markdown and one takeaway, then tick **Published**. The page goes live at `/explainers/<slug>` and appears in the feed and sitemap.

## The characters

Deepak and the cast belong to Frappe and are used with permission. They are composed only from the library's own exports, never drawn, generated or redrawn. They are not covered by this repository's licence, and this repository stays private so the artwork never becomes a public kit.

Characters from the Frappe Character Library, used with permission.
