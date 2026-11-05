/* thefrappeguy.com: series filter on /explainers and the question form on /ask. No libraries. */
(function () {
  "use strict";

  // Explainers: filter cards by series. Links work without JavaScript (?series=slug).
  var list = document.getElementById("list");
  if (list) {
    var chips = document.querySelectorAll(".chip[data-filter]");
    var cards = list.querySelectorAll(".card");
    var count = document.getElementById("count");
    var empty = document.getElementById("empty");
    var emptyTitle = document.getElementById("empty-title");
    var apply = function (f) {
      var valid = false, name = "";
      chips.forEach(function (c) { if (c.dataset.filter === f) { valid = true; name = c.dataset.name || ""; } });
      if (!valid) f = "all";
      var shown = 0;
      chips.forEach(function (c) {
        if (c.dataset.filter === f) c.setAttribute("aria-current", "true"); else c.removeAttribute("aria-current");
      });
      cards.forEach(function (c) { var on = f === "all" || c.dataset.series === f; c.hidden = !on; if (on) shown++; });
      count.textContent = shown === 1 ? "1 part" : shown + " parts";
      count.hidden = shown === 0;
      empty.hidden = shown !== 0;
      emptyTitle.textContent = f === "all" ? "The first parts of the story are being written." : "The first parts of " + name + " are being written.";
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function (e) {
        e.preventDefault();
        apply(c.dataset.filter);
        try { history.replaceState(null, "", c.getAttribute("href")); } catch (err) {}
      });
    });
    apply(new URLSearchParams(location.search).get("series") || "all");
  }

  // Ask: send the question, show a plain confirmation or a plain error.
  var form = document.getElementById("ask");
  if (form) {
    var area = new URLSearchParams(location.search).get("area");
    var select = document.getElementById("area");
    if (area && select.querySelector('option[value="' + area.replace(/[^a-z0-9-]/g, "") + '"]')) select.value = area;
    var q = document.getElementById("q"), qErr = document.getElementById("q-err");
    var err = document.getElementById("form-err"), send = document.getElementById("send");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      err.hidden = true;
      if (q.value.trim().length < 10) { qErr.hidden = false; q.setAttribute("aria-invalid", "true"); q.focus(); return; }
      qErr.hidden = true; q.removeAttribute("aria-invalid");
      send.disabled = true; send.textContent = "Sending";
      var body = new URLSearchParams(new FormData(form));
      if (!document.getElementById("may_publish").checked) body.set("may_publish", "0");
      fetch(form.action, { method: "POST", body: body, headers: { "Accept": "application/json" } })
        .then(function (r) {
          if (r.ok) { form.hidden = true; var d = document.getElementById("done"); d.hidden = false; d.focus(); return; }
          return r.json().catch(function () { return {}; }).then(function (data) {
            var msg = r.status === 429 ? "Too many questions from here in the last hour. Please try again later." : "";
            if (!msg && data && data._server_messages) {
              try { msg = JSON.parse(JSON.parse(data._server_messages)[0]).message; } catch (x) {}
            }
            err.textContent = (msg || "Your question didn't send. Please try again in a minute.").replace(/<[^>]+>/g, " ");
            err.hidden = false;
          });
        })
        .catch(function () { err.textContent = "Your question didn't send. Check your connection and try again."; err.hidden = false; })
        .then(function () { send.disabled = false; send.textContent = "Send question"; });
    });
  }
})();
