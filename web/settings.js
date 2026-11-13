// Reader controls and feed recipes. Selection behavior belongs to core.js.
(function (root) {
  "use strict";
  root.BoringSettings = { create: function (ctx) {
    var D = ctx.D, R = D.rubric, C = ctx.C, getPrefs = ctx.prefs;
    var $ = ctx.$, el = ctx.el, checkbox = ctx.checkbox, toggleIn = ctx.toggleIn;
    var update = ctx.update, updateSoon = ctx.updateSoon;
    var partLabel = ctx.partLabel, weightWords = ctx.weightWords, plural = ctx.plural;
    var THRESHOLD_LABELS = ctx.labels, THRESHOLD_HINTS = ctx.hints;
    var WEIGHT_PARTS = root.BoringCore.WEIGHT_PARTS;
  function renderControls() {
    var th = $("threshold");
    th.innerHTML = "";
    Object.keys(R.thresholds).forEach(function (k) {
      var input = el("input", { type: "radio", name: "threshold", id: "threshold-" + k, value: k });
      input.checked = getPrefs().threshold === k;
      input.addEventListener("change", function () { getPrefs().threshold = k; update(); });
      th.appendChild(el("label", { for: "threshold-" + k }, [input, THRESHOLD_LABELS[k]]));
    });
    renderWeights();
    $("recipe-name").value = getPrefs().recipe;
    $("all-topics").checked = !getPrefs().topics.length;
    $("all-topics").onchange = function () {
      // Turning off all starts with every category selected, ready to narrow.
      getPrefs().topics = this.checked ? [] : Object.keys(D.topics);
      syncTopics(); update();
    };
    [["topics", D.topics]].forEach(function (pair) {
      var key = pair[0], map = pair[1], box = $(key);
      box.innerHTML = "";
      Object.keys(map).forEach(function (k) {
        var label = el("span", { className: "opt" }, [el("span", { text: map[k] }),
          D.topic_descriptions && D.topic_descriptions[k] ? el("small", { text: D.topic_descriptions[k] }) : null]);
        box.appendChild(checkbox(key + "-" + k, label, !getPrefs()[key].length || getPrefs()[key].indexOf(k) >= 0, function (on) {
          var chosen = getPrefs()[key].length ? getPrefs()[key] : Object.keys(map);
          getPrefs()[key] = toggleIn(chosen, k, on);
          if (!getPrefs()[key].length) getPrefs()[key] = [k]; // keep one category; All is explicit
          syncTopics(); update();
        }));
      });
    });
    var off = $("official");
    off.checked = getPrefs().official;
    off.onchange = function () { getPrefs().official = off.checked; update(); };
    var bs = $("blindspots");
    bs.checked = getPrefs().blindspots;
    bs.onchange = function () { getPrefs().blindspots = bs.checked; update(); };
    var st = $("statements");
    st.checked = getPrefs().statements;
    st.onchange = function () { getPrefs().statements = st.checked; update(); };
    var ho = $("headlines-only");
    ho.checked = getPrefs().length === "headlines";
    ho.onchange = function () { getPrefs().length = ho.checked ? "headlines" : "full"; update(); };
    var so = $("spotlight-only");
    so.checked = getPrefs().spotlight;
    so.onchange = function () { getPrefs().spotlight = so.checked; update(); };

    var groups = $("sources");
    groups.innerHTML = "";
    [["Left", function (s) { return s.lean === "left"; }],
     ["Center", function (s) { return s.lean === "center"; }],
     ["Right", function (s) { return s.lean === "right"; }],
     ["Unrated", function (s) { return s.lean === "unrated" && s.type !== "primary"; }],
     ["Government records", function (s) { return s.type === "primary" && s.role === "record"; }],
     ["Government statements", function (s) { return s.type === "primary" && s.role !== "record"; }]].forEach(function (b) {
      var ids = Object.keys(D.sources).filter(function (id) { return b[1](D.sources[id]); })
        .sort(function (x, y) { return D.sources[x].name.localeCompare(D.sources[y].name); });
      if (!ids.length) return;
      var g = el("div", {}, [el("h2", { text: b[0] })]);
      ids.forEach(function (id) {
        g.appendChild(checkbox("src-" + id, D.sources[id].name, getPrefs().exclude.indexOf(id) < 0, function (on) {
          getPrefs().exclude = toggleIn(getPrefs().exclude, id, !on); update();
        }));
      });
      groups.appendChild(g);
    });
  }

  function syncTopics() {
    var topics = getPrefs().topics;
    $("all-topics").checked = !topics.length;
    Object.keys(D.topics).forEach(function (key) {
      $("topics-" + key).checked = !topics.length || topics.indexOf(key) >= 0;
    });
  }
  function renderShares() {
    var w = C.weightsFor(getPrefs());
    WEIGHT_PARTS.forEach(function (k) { $("weight-share-" + k).textContent = Math.round(w[k] * 100) + "%"; });
  }
  function sliderValue(k, i) { return String(getPrefs().weights ? getPrefs().weights[i] : Math.round(R.weights[k] * 100)); }
  function renderWeights() {
    var box = $("weight-controls");
    box.innerHTML = "";
    WEIGHT_PARTS.forEach(function (k, i) {
      var input = el("input", { type: "range", id: "weight-" + k, min: "0", max: "100", step: "1" });
      input.value = sliderValue(k, i);
      input.addEventListener("input", function () {
        var values = WEIGHT_PARTS.map(function (part) { return Number($("weight-" + part).value); });
        getPrefs().weights = C.cleanWeights(values);
        // All four at zero means nothing to rank by, so go back to the published
        // rule. The sliders stay in place, because one of them is in use.
        if (!values.some(function (n) { return n > 0; })) {
          WEIGHT_PARTS.forEach(function (part, n) { $("weight-" + part).value = sliderValue(part, n); });
        }
        renderShares();
        updateSoon();
      });
      box.appendChild(el("div", { className: "weight" }, [
        el("label", { for: "weight-" + k, text: partLabel(k) }), input,
        el("span", { className: "pct", id: "weight-share-" + k })
      ]));
    });
    renderShares();
  }

  function renderDocs() {
    var any = Object.keys(D.sources)[0];
    var rows = [
      ["topics=economy,world", "Only these categories: " + Object.keys(D.topics).join(", ") + "."],
      ["exclude=" + any, "Leave out these sources by their id, then score every story again. Ids are listed in sources.yaml."],
      ["threshold=strict", "How much agreement a story needs: broad, standard (default) or strict."],
      ["weights=60,20,10,10", "Your own weights for " + WEIGHT_PARTS.join(", ") + ": four whole numbers from 0 to 100, in that order. Each counts as its share of their total. This re-ranks stories that were written; it can't bring back one the published rule dropped."],
      ["official=0", "Leave out government records and statements that no outlet has covered yet."],
      ["blindspots=0", "Leave out stories that only one side ran and that didn't reach your threshold."],
      ["statements=0", "Leave out government statements, such as White House and agency press releases. Records still count."],
      ["spotlight=1", "Only the top " + R.spotlight + " stories each day."],
      ["length=headlines", "Headlines without the bullet points."],
      ["recipe=Morning%20brief", "A name for this setup, up to 60 characters. It labels the page and the feed and changes nothing else."]
    ];
    var tb = $("param-table");
    tb.innerHTML = "";
    rows.forEach(function (r) { tb.appendChild(el("tr", {}, [el("td", {}, [el("code", { translate: "no", text: r[0] })]), el("td", { text: r[1] })])); });

    var base = D.base_url + "/feed.xml";
    var ex = [
      ["Just the spotlight", base + "?spotlight=1"],
      ["Economy and world news, strict agreement", base + "?topics=economy,world&threshold=strict"],
      ["Politics and government, no press releases", base + "?topics=government&statements=0"]
    ];
    var ul = $("examples");
    ul.innerHTML = "";
    ex.forEach(function (e) { ul.appendChild(el("li", {}, [el("span", { text: e[0] }), el("code", { translate: "no", text: e[1] })])); });
    var recipes = $("recipe-list");
    recipes.innerHTML = "";
    C.recipes().forEach(function (r) {
      recipes.appendChild(el("li", {}, [el("a", { href: "?" + r.query + "#today", text: r.name }), el("span", { text: r.note })]));
    });
    $("repo-link").href = D.repo_url;
    Array.prototype.forEach.call(document.querySelectorAll(".spot-n"), function (n) { n.textContent = String(R.spotlight); });
  }

  function renderSettingsSummary() {
    var bits = [THRESHOLD_LABELS[getPrefs().threshold] + " agreement"];
    bits.push(getPrefs().topics.length ? getPrefs().topics.map(function (t) { return D.topics[t]; }).join(", ") : "all categories");
    if (getPrefs().exclude.length) bits.push(plural(getPrefs().exclude.length, "source", "sources") + " off");
    if (!getPrefs().official) bits.push("no uncovered government items");
    if (!getPrefs().blindspots) bits.push("no one-sided stories");
    if (!getPrefs().statements) bits.push("no government statements");
    if (getPrefs().weights) bits.push("your own weights");
    if (getPrefs().length === "headlines") bits.push("headlines only");
    $("settings-summary").textContent = "Now: " + bits.join(", ") + ".";
    $("threshold-hint").textContent = THRESHOLD_HINTS[getPrefs().threshold] +
      (getPrefs().weights ? " That describes the published weights; yours can change which stories reach it." : "");
    $("weights-now").textContent = getPrefs().weights ? "Yours: " + weightWords() + "." : "These are the published weights.";
    $("feed-url").value = C.link(getPrefs(), "/feed.xml");
    $("recipe-link").value = C.link(getPrefs(), "/");
    var note = $("recipe-note");
    note.hidden = !getPrefs().recipe;
    note.innerHTML = "";
    if (getPrefs().recipe) {
      note.appendChild(document.createTextNode("Using the recipe \u201c" + getPrefs().recipe + "\u201d. Whoever made the link chose that name, not Standard Edition. "));
      note.appendChild(el("a", { href: "#your-feed", text: "See its settings" }));
    }
  }

    return { controls: renderControls, docs: renderDocs, summary: renderSettingsSummary };
  } };
})(globalThis);
