import frappe
from frappe.utils import cint, validate_email_address

# Signups and questions per visitor address per hour (D-191). A whole office often shares one address,
# so a launch post on Raven must not lock out the sixth colleague. Bot-trap requests are not counted.
SUBSCRIBE_LIMIT = 30
ASK_LIMIT = 20


def over_limit(action, limit, seconds=60 * 60):
	"""Counts one real request from this address. Past the limit, answers 429 with a plain message instead of
	raising: Frappe's own 429 page talks about the site's compute plan, which is not what happened."""
	ip = getattr(frappe.local, "request_ip", None) or "unknown"
	key = frappe.cache.make_key(f"tfg-limit:{action}:{ip}")
	count = frappe.cache.incr(key)
	if count == 1:
		frappe.cache.expire(key, seconds)
	if count > limit:
		frappe.local.response["http_status_code"] = 429
		return True
	return False


@frappe.whitelist(allow_guest=True, methods=["POST"])
def ask(question=None, area=None, full_name=None, email=None, may_publish=0, website=None):
	"""Saves a question from /ask as a Question record. `website` is a hidden trap field for bots."""
	if website:
		return {"ok": True}
	if over_limit("ask", ASK_LIMIT):
		return {"ok": False, "message": "Too many questions from here in the last hour. Please try again later."}

	question = (question or "").strip()
	if len(question) < 10:
		frappe.throw("Write your question in a sentence or two, then send it.")
	if len(question) > 4000:
		frappe.throw("That's a long one. Please keep it under 4,000 characters.")

	email = (email or "").strip()
	if email and not validate_email_address(email):
		frappe.throw("That email address doesn't look right. Check it, or leave it empty.")

	if area and not frappe.db.exists("Explainer Series", area):
		area = None

	frappe.get_doc(
		{
			"doctype": "Question",
			"question": question,
			"area": area,
			"full_name": (full_name or "").strip()[:140],
			"email": email,
			"may_publish": cint(may_publish),
		}
	).insert(ignore_permissions=True)
	return {"ok": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def subscribe(email=None, source=None, website=None):
	"""Saves a newsletter signup as a Subscriber, then hands it to Kit in the background (D-186).
	`website` is a hidden trap field for bots. Signing up twice is fine and changes nothing."""
	if website:
		return {"ok": True}
	if over_limit("subscribe", SUBSCRIBE_LIMIT):
		return {"ok": False, "message": "Too many signups from here in the last hour. Please try again later."}
	email = (email or "").strip().lower()
	if not email or not validate_email_address(email):
		frappe.throw("That email address doesn't look right. Check it and try again.")
	source = (source or "").strip()[:140]
	name = frappe.db.get_value("Subscriber", {"email": email})
	if name:
		frappe.db.set_value("Subscriber", name, "status", "Subscribed")
	else:
		name = frappe.get_doc({"doctype": "Subscriber", "email": email, "source": source}).insert(ignore_permissions=True).name
	frappe.db.commit()
	if kit_ready():
		frappe.enqueue("thefrappeguy.api.send_to_kit", queue="short", name=name, enqueue_after_commit=True)
	return {"ok": True}


def kit_ready():
	s = frappe.get_cached_doc("Newsletter Settings")
	return bool(s.kit_enabled and s.kit_form_id and s.get_password("kit_api_key", raise_exception=False))


def send_to_kit(name):
	"""Creates the subscriber in Kit and adds them to the form (Kit API v4). Kit sends the emails."""
	import requests

	doc = frappe.get_doc("Subscriber", name)
	s = frappe.get_doc("Newsletter Settings")
	key = s.get_password("kit_api_key", raise_exception=False)
	if not (s.kit_enabled and s.kit_form_id and key) or doc.status != "Subscribed":
		return
	headers = {"X-Kit-Api-Key": key, "Accept": "application/json"}
	try:
		r = requests.post("https://api.kit.com/v4/subscribers", json={"email_address": doc.email}, headers=headers, timeout=20)
		if r.status_code not in (200, 201, 202):
			raise Exception(f"create subscriber: {r.status_code} {r.text[:300]}")
		r = requests.post(
			f"https://api.kit.com/v4/forms/{s.kit_form_id.strip()}/subscribers",
			json={"email_address": doc.email, "referrer": f"https://thefrappeguy.com{doc.source or ''}"},
			headers=headers,
			timeout=20,
		)
		if r.status_code not in (200, 201):
			raise Exception(f"add to form: {r.status_code} {r.text[:300]}")
		doc.db_set({"kit_status": "Sent to Kit", "kit_error": ""})
	except Exception as e:
		doc.db_set({"kit_status": "Kit error", "kit_error": str(e)[:1000]})
	frappe.db.commit()


def send_waiting_to_kit():
	"""Daily: hands Kit every signup it doesn't have yet, including those made before Kit was set up."""
	if not kit_ready():
		return
	for name in frappe.get_all(
		"Subscriber", filters={"status": "Subscribed", "kit_status": ["in", ["Waiting", "Kit error"]]}, pluck="name"
	):
		send_to_kit(name)


# Page counting without cookies (D-196) ---------------------------------------------------------------------------
# What is stored: the day, the page, phone/tablet/computer, the referring site's host name, the utm tags, and a
# one-way hash of (address, browser, a random code that changes daily). Nothing that identifies a person.

BOT_WORDS = ("bot", "crawl", "spider", "slurp", "preview", "headless", "lighthouse", "pingdom", "monitor", "python", "curl", "wget")
SOURCE_NAMES = {
	"lnkd.in": "linkedin", "linkedin.com": "linkedin", "t.co": "x", "x.com": "x", "twitter.com": "x",
	"facebook.com": "facebook", "instagram.com": "instagram", "reddit.com": "reddit", "youtube.com": "youtube",
	"wa.me": "whatsapp", "web.whatsapp.com": "whatsapp", "frappe.io": "frappe.io", "discuss.frappe.io": "frappe forum",
}


def _clip(value, n=80):
	return (value or "").strip()[:n] or None


def _host(url):
	from urllib.parse import urlparse

	try:
		host = (urlparse(url or "").hostname or "").lower()
	except ValueError:
		return None
	return host[4:] if host.startswith("www.") else host or None


def _device(ua):
	ua = ua.lower()
	if "ipad" in ua or "tablet" in ua or ("android" in ua and "mobile" not in ua):
		return "Tablet"
	if "mobi" in ua or "iphone" in ua or "android" in ua:
		return "Phone"
	return "Computer"


def _daily_salt(day):
	key = frappe.cache.make_key(f"tfg-hit-salt:{day}")
	salt = frappe.cache.get(key)
	if not salt:
		frappe.cache.set(key, frappe.generate_hash(length=32), nx=True, ex=60 * 60 * 48)
		salt = frappe.cache.get(key)
	return salt.decode() if isinstance(salt, bytes) else str(salt)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def hit(path=None, referrer=None, utm_source=None, utm_medium=None, utm_campaign=None):
	"""Counts one page view. Sent by site.js with navigator.sendBeacon; answers nothing useful on purpose."""
	import hashlib

	from frappe.utils import today

	ua = frappe.get_request_header("User-Agent") or ""
	if frappe.session.user != "Guest" or not ua or any(w in ua.lower() for w in BOT_WORDS):
		return
	path = (path or "").split("?")[0].split("#")[0][:140]
	if not path.startswith("/") or path.startswith(("/api", "/desk", "/app", "/login", "/stats", "/assets")):
		return
	if over_limit("hit", 600):
		frappe.local.response["http_status_code"] = 200
		return

	ref = _host(referrer)
	own = _host(frappe.utils.get_url())
	if ref == own:
		ref = None
	source = _clip(utm_source, 40)
	source = source.lower() if source else SOURCE_NAMES.get(ref or "", ref)
	if not source and ref and ref.startswith("google."):
		source = "google"
	day = today()
	ip = getattr(frappe.local, "request_ip", None) or ""
	visitor = hashlib.sha256(f"{_daily_salt(day)}|{ip}|{ua}".encode()).hexdigest()[:16]

	frappe.get_doc({
		"doctype": "Page Hit", "day": day, "path": path, "device": _device(ua), "referrer": ref,
		"source": source, "medium": _clip(utm_medium, 40), "campaign": _clip(utm_campaign, 60), "visitor": visitor,
	}).db_insert()


def delete_old_hits():
	"""Page counts are kept for 13 months (Privacy)."""
	frappe.db.delete("Page Hit", {"day": ["<", frappe.utils.add_days(frappe.utils.today(), -396)]})
