# Contributing to The Frappe Guy

The Frappe Guy (thefrappeguy.com) explains Frappe, ERPNext and Frappe Cloud as a comic, following one small fictional company, The Coffee Company. It is run by Mauli Mogal, Sales @ Frappe. It is not Frappe's official channel.

Everyone who knows Frappe well can make it better. You do not need to code.

## Ways to help, easiest first

| You want to | Do this | Needs |
|---|---|---|
| Fix or improve a line of dialogue | Open a [Wording suggestion](../../issues/new?template=wording.yml) | A browser |
| Report a wrong or out-of-date fact | Open a [Fact check](../../issues/new?template=fact.yml) | A browser |
| Suggest a story for another industry | Open a [Storyline idea](../../issues/new?template=storyline.yml) | A browser |
| Help with layout, accessibility or technical writing | Open a [Design issue](../../issues/new?template=design.yml) | A browser |
| Change the wording yourself | Edit the JSON on GitHub and open a pull request (below) | A GitHub account |
| Work on the site's code | Run it locally (below) | A Frappe bench |

If you only have a minute, use the Ask page on the site: https://thefrappeguy.com/ask

## Reading a part so you can comment

1. Open a part, for example https://thefrappeguy.com/explainers/what-is-an-erp
2. Panels are numbered by position, starting at 1. Counting down the page works. "Read the comic as text" at the bottom lists every panel in order.
3. Say the part and the panel number in your issue.

## Changing wording yourself

The comic text lives in `thefrappeguy/data/`:

| File | Release |
|---|---|
| `r1_stage6.json` | Frappe 101, five parts (the live version) |
| `r2_erpnext_1.json` | ERPNext I, five parts |

Older `r1_*` files are history. Do not edit them.

Each part has `panels`. Each panel can have `caption`, `thought`, `left_bubble` (the cast member on the left) and `right_bubble` (The Frappe Guy on the right).

1. On GitHub, open the file, click the pencil, change the text, and choose "Create a new branch and start a pull request".
2. The **Copy check** runs by itself. If it shows a red cross, open it and read the list. Each line names the part, the panel and the rule.
3. To check before you push: `python3 tools/check_copy.py` (Python 3.10 or newer, nothing to install).

Heads up: editing a JSON file does not change the live site by itself. The maintainer reviews your pull request, adds the patch that reloads the part, and deploys. That is the one step you do not need to do.

## The rules, short version

The full guides are the Voice and Usage rules pages in the brand book at https://thefrappeguy.com/brand.

**Voice.** A calm senior engineer at a whiteboard. Plain words, short sentences, one real example. The catch is said next to the feature. Say it the way you would across a table.

**In every line**

- No em dashes or en dashes. Use a comma, a colon or a new sentence. Ranges: "3 to 5".
- Bubbles hold 20 words at most. Aim for 12. A caption alone in its panel can hold 30.
- At most 2 speech items per panel: a caption, a thought or a bubble each count as one.
- The Frappe Guy never uses an exclamation mark. Only Raju may, once per bubble.
- Never use: delve, leverage, unlock, seamless, robust, game-changer, elevate, empower, journey, revolutionize, cutting-edge, simply. Never call The Frappe Guy honest or unbiased: show it, never say it.
- In public he is "The Frappe Guy", never "Deepak".
- Indian English spelling: colour, customise, organisation, licence (noun).
- No emoji.

**Facts**

- Every claim about Frappe, ERPNext or Frappe Cloud must be on frappe.io, docs.frappe.io, frappecloud.com/docs or github.com/frappe. Add the link in your issue or pull request.
- No invented prices, plans, dates, customers, quotes or numbers. Use placeholders: [PRICE], [NUMBER].
- Prices and costs belong to the Pricing release only.
- Compare facts, never name a competitor in a negative line.
- Point people to Frappe Cloud. Never promote self-hosting.
- Never put words in a real person's mouth.

## The characters

The Frappe Guy (Deepak) and the cast (Ishita, Raju, Sara, Joseph, Salman) belong to Frappe Technologies and are used here with permission. They are composed only from the exports of Frappe's Character Library.

- Never draw, trace, edit, recolour, mirror or generate a character, with any tool, including AI image tools.
- Do not add or replace files in `thefrappeguy/public/img` for characters.
- If a story needs a pose that does not exist, open a Design issue naming it. We ask Frappe's designer.
- Do not reuse the character files outside this project. See the licence note in `license.txt`.

## Running the site locally

You need a Frappe bench on version 15 or 16.

```bash
bench get-app https://github.com/MauliMogal/thefrappeguy
bench new-site tfg.localhost
bench --site tfg.localhost install-app thefrappeguy
bench start
```

Open http://tfg.localhost:8000. Parts are saved through `Explainer.validate`, which runs the same brand checks as `tools/check_copy.py`.

Please keep pull requests small: one part, one page or one idea. Open an issue first for anything bigger.

## Reviews

Mauli reads every issue and pull request, usually within a few days. Facts about Frappe that need an insider can wait for someone at Frappe to confirm: say so in your issue and we will ask on Raven.
