(function () {
  var d = document, f = d.getElementById("cf"), msg = d.getElementById("cmsg"), btn = f.querySelector("button[type=submit]"), t0 = Date.now();
  function say(t, bad) { msg.textContent = t; msg.className = "cmsg" + (bad ? " bad" : " ok"); }
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    if (f.elements._honey.value) return;                            // bots fill the hidden field
    var name = f.elements.name.value.trim(), email = f.elements.email.value.trim(), subj = f.elements.subject.value.trim(), body = f.elements.message.value.trim();
    if (!name || !subj || !body || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say("Please fill in your name, a valid email, a subject and a message.", true); return; }
    if (Date.now() - t0 < 2500) { say("One moment, then press send again.", true); t0 = Date.now() - 1500; return; }
    f.elements._subject.value = "Portfolio message: " + subj;
    btn.disabled = true; say("Sending\u2026");
    fetch(f.action, { method: "POST", headers: { Accept: "application/json" }, body: new FormData(f) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        if (!x.ok || (x.j.success !== true && x.j.success !== "true")) throw new Error(x.j.message || "failed");
        f.hidden = true;
        var ok = d.getElementById("cdone"); ok.hidden = false; ok.focus();
      })
      .catch(function () {
        btn.disabled = false;
        say("That didn\u2019t go through. Please email me directly at the address below.", true);
      });
  });
})();
