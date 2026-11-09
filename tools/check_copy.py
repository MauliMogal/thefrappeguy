"""Check the comic copy in thefrappeguy/data/*.json against the brand rules.

    python3 tools/check_copy.py              # every data file
    python3 tools/check_copy.py path.json    # one file

No Frappe, no bench, no install: Python 3.10+ only. The same rules run on the site when a part is saved
(thefrappeguy/content.py and the Explainer doctype); this script lets you find problems before a pull request.
Exit code 0 means clean, 1 means at least one problem.
"""
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "thefrappeguy" / "data"

BANNED = ["honest", "honestly", "unbiased", "no sales pitch", "costs a sale", "delve", "leverage", "leverages",
          "leveraging", "unlock", "unlocks", "seamless", "seamlessly", "robust", "game-changer", "game changer",
          "elevate", "empower", "empowers", "journey", "revolutionize", "revolutionise", "cutting-edge",
          "cutting edge", "simply"]
BANNED_RE = [(w, re.compile(r"\b" + re.sub(r"[-\s]", r"[-\\s]", w) + r"\b", re.I)) for w in BANNED]
SPEECH = ("caption", "thought", "left_bubble", "right_bubble")
TEXT = SPEECH + ("diagram_labels", "screen_alt")
PART_TEXT = ("title", "takeaway", "dek", "so_far")


def words(s):
    return len(str(s).split())


def check_text(text, where, out):
    if not text:
        return
    if "\u2014" in text or "\u2013" in text:
        out.append(f"{where}: dash found. Use a comma, a colon or a new sentence. Ranges: write '3 to 5'.")
    for word, rx in BANNED_RE:
        if rx.search(text):
            out.append(f'{where}: "{word}" is on the banned list.')
    if re.search(r"\bDeepak\b", text):
        out.append(f'{where}: write "The Frappe Guy", never "Deepak" (Deepak is the library\'s file name only).')


def check_file(path):
    out = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for e in data["explainers"]:
        part = f"{path.name} {e['slug']}"
        for k in PART_TEXT:
            check_text(e.get(k, ""), f"{part} {k}", out)
        stickers = 0
        for i, p in enumerate(e["panels"], 1):
            where = f"{part} panel {i}"
            for k in TEXT:
                check_text(p.get(k, ""), f"{where} {k}", out)
            speech = [k for k in SPEECH if p.get(k)]
            if len(speech) > 2:
                out.append(f"{where}: {len(speech)} speech items (2 at most; a caption counts).")
            for k in speech:
                limit = 30 if (k == "caption" and len(speech) == 1) else 20
                if p.get("shot") == "small":
                    limit = 6
                n = words(p[k])
                if n > limit:
                    out.append(f"{where} {k}: {n} words ({limit} at most).")
            if "!" in p.get("right_bubble", ""):
                out.append(f"{where}: The Frappe Guy never uses exclamation marks.")
            lb = p.get("left_bubble", "")
            if "!" in lb and not p.get("left_pose", "").startswith("cl-raju"):
                out.append(f"{where}: only Raju may use an exclamation mark.")
            if lb.count("!") > 1:
                out.append(f"{where}: one exclamation mark per bubble at most.")
            if p.get("right_pose") == "dr-listen" and p.get("right_bubble"):
                out.append(f"{where}: The Frappe Guy in 'listen' cannot be the one speaking.")
            if p.get("shot") in ("diagram", "screen") and (p.get("left_pose") or p.get("right_pose")):
                out.append(f"{where}: a {p['shot']} panel has no characters.")
            if p.get("sticker"):
                stickers += 1
        if stickers > 1:
            out.append(f"{part}: {stickers} stickers (one per part at most).")
    return out


def main():
    files = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(DATA.glob("*.json"))
    problems = []
    for f in files:
        problems += check_file(f)
    for p in problems:
        print("-", p)
    print(f"checked {len(files)} file(s): {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
