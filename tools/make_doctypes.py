"""Writes the DocType JSON files. Run from the repo root: python3 tools/make_doctypes.py"""
import json, os, sys
sys.path.insert(0, ".")
from thefrappeguy.characters import CHARACTERS

MOD = "The Frappe Guy"
BASE = "thefrappeguy/the_frappe_guy/doctype"
NOW = "2026-11-05 00:00:00.000000"
DEEPAK = "\n".join(sorted(k for k in CHARACTERS if k.startswith("dr-")))
CAST = "\n".join(sorted(k for k in CHARACTERS if k.startswith("cl-")))
PERM = [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1, "share": 1}]

def f(fieldname, fieldtype, label=None, **kw):
    d = {"fieldname": fieldname, "fieldtype": fieldtype}
    if label: d["label"] = label
    d.update(kw)
    return d

def write(name, fields, **kw):
    folder = name.lower().replace(" ", "_")
    path = os.path.join(BASE, folder)
    os.makedirs(path, exist_ok=True)
    doc = {
        "actions": [], "creation": NOW, "doctype": "DocType", "engine": "InnoDB",
        "field_order": [x["fieldname"] for x in fields], "fields": fields,
        "index_web_pages_for_search": 0, "links": [], "modified": NOW, "modified_by": "Administrator",
        "module": MOD, "name": name, "owner": "Administrator", "permissions": PERM,
        "sort_field": "modified", "sort_order": "DESC", "states": [],
    }
    doc.update(kw)
    json.dump(doc, open(os.path.join(path, folder + ".json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(path, "__init__.py"), "a").close()

os.makedirs(BASE, exist_ok=True)
open(os.path.join(BASE, "__init__.py"), "a").close()
open("thefrappeguy/the_frappe_guy/__init__.py", "a").close()

write("Explainer Series", [
    f("slug", "Data", "Slug", reqd=1, unique=1, description="Lowercase words joined by hyphens. It becomes /series/<slug>."),
    f("title", "Data", "Title", reqd=1, in_list_view=1),
    f("scene", "Select", "Scene colour", reqd=1, options="ink\nblue\ncyan\nyellow\nmint\nmagenta\nviolet\ngrey\ngreen\norange", in_list_view=1),
    f("sort_order", "Int", "Order"),
    f("description", "Small Text", "Description", reqd=1),
    f("asked_by", "Data", "Who usually asks", description="One sentence, for example: Usually asked by Sara, who wants proof."),
    f("pose", "Select", "Deepak pose on the series header", options=DEEPAK, default="dr-thinking"),
], autoname="field:slug", title_field="title", show_title_field_in_link=1, track_changes=1)

write("Explainer", [
    f("title", "Data", "Title", reqd=1, in_list_view=1, description="The question, in the asker's words."),
    f("slug", "Data", "Slug", reqd=1, unique=1, description="Lowercase words joined by hyphens. It becomes /explainers/<slug>."),
    f("column_break_1", "Column Break"),
    f("series", "Link", "Series", options="Explainer Series", reqd=1, in_list_view=1, in_standard_filter=1),
    f("published", "Check", "Published", in_list_view=1, in_standard_filter=1),
    f("published_on", "Date", "Published on"),
    f("section_card", "Section Break", "Card"),
    f("dek", "Small Text", "One line under the title", reqd=1),
    f("asked_by", "Select", "Asked by", options="Ishita\nRaju\nSara\nJoseph\nSalman"),
    f("card_pose", "Select", "Deepak pose on the card", options=DEEPAK, default="dr-idea"),
    f("section_panel", "Section Break", "Comic panel", description="Max 20 words per bubble, 12 is the target. The asker sits on the left, Deepak answers from the right."),
    f("cast_pose", "Select", "Asker pose (left)", options=CAST, reqd=1, default="cl-suman-expressing"),
    f("question", "Small Text", "Asker's bubble", reqd=1),
    f("column_break_2", "Column Break"),
    f("deepak_pose", "Select", "Deepak pose (right)", options=DEEPAK, reqd=1, default="dr-using-ipad"),
    f("answer", "Small Text", "Deepak's bubble", description="Leave empty when Deepak is listening."),
    f("environment", "Select", "Scenery", options="env-cafeteria\nenv-cafe-counter\nnone", default="env-cafeteria"),
    f("section_article", "Section Break", "Article", description="Four parts: the answer first, one real example, the catch said plainly, then the takeaway. Write DocType names in backticks, like `Sales Invoice`."),
    f("body", "Markdown Editor", "Article", reqd=1),
    f("takeaway", "Data", "Takeaway", reqd=1, description="One sentence, ideally under 12 words. No unchecked numbers."),
    f("section_share", "Section Break", "Sharing"),
    f("og_image", "Attach Image", "Share image (1200 x 630)", description="Optional. Without it the page uses its own image if one was generated, otherwise the series image."),
], autoname="field:slug", title_field="title", show_title_field_in_link=1, track_changes=1, sort_field="published_on")

write("Question", [
    f("question", "Long Text", "Question", reqd=1, in_list_view=1),
    f("area", "Link", "Area", options="Explainer Series", in_list_view=1, in_standard_filter=1),
    f("column_break_1", "Column Break"),
    f("status", "Select", "Status", options="New\nReplied\nBecame an explainer\nClosed", default="New", in_list_view=1, in_standard_filter=1),
    f("full_name", "Data", "Name"),
    f("email", "Data", "Email", options="Email"),
    f("may_publish", "Check", "May become an explainer", description="The asker allowed this question to become an explainer, without their name."),
    f("explainer", "Link", "Explainer", options="Explainer", depends_on="eval:doc.status=='Became an explainer'"),
], autoname="hash", title_field="question", track_changes=1)
print("ok")
