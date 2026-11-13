// Evidence presentation is shared by the reader views. It never infers support.
(function (root) {
  "use strict";
  root.BoringEvidence = { create: function (D, el, $, plural) {
  function provenance(s) {
    var writer = s.written_by || "";
    var text = !writer ? "Summary provenance was not recorded in this edition."
      : /mock/i.test(writer) ? "Sample summary. Invented demonstration data."
      : /fallback/i.test(writer) ? "Automated fallback summary from source material."
      : "AI-generated summary. Check the original reporting.";
    return el("p", { className: "provenance", text: text });
  }
  function claimEvidence(s) {
    var claims = (s.checks || {}).claims || [];
    var box = el("details", { className: "claim-evidence" }, [el("summary", { text: "Sources behind each statement" })]);
    if (!claims.length) box.appendChild(el("p", { className: "hint", text: "Statement-level evidence was not recorded for this edition. The original reports are linked below." }));
    claims.forEach(function (claim) {
      var section = el("section", {}, [el("p", { text: claim.text }), el("p", { className: "hint", text:
        claim.status === "model-supported" ? "The model marked this supported. This is not an independent fact check."
        : claim.status === "numbers-only" ? "Numbers matched source text; the claim was not verified by a model." : "This statement has not been verified." })]);
      (claim.sources || []).forEach(function (source) {
        section.appendChild(el("blockquote", { text: source.quote }));
        section.appendChild(el("a", { href: source.url, target: "_blank", rel: "noopener", text: (D.sources[source.source_id] || {}).name || source.source_id }));
      });
      box.appendChild(section);
    });
    return box;
  }
  function renderHealth() {
    var box = $("coverage-health"), ids = Object.keys(D.sources), down = D.feeds_down || [];
    var windowInfo = D.collection_window || {};
    box.innerHTML = "";
    var known = D.coverage_known === true;
    box.appendChild(el("p", { text: known ? plural(ids.length - down.length, "source", "sources") + " read; " + down.length + " unavailable."
      : "Collection health was not fully recorded for this edition." }));
    if (windowInfo.start && windowInfo.end) box.appendChild(el("p", { text: "Collection window (UTC): " + windowInfo.start + " to " + windowInfo.end + "." }));
    if (down.length) box.appendChild(el("p", { text: "Could not read: " + down.map(function (id) { return (D.sources[id] || {}).name || id; }).join(", ") + "." }));
    var provisional = ids.filter(function (id) { var src = D.sources[id]; return src.type !== "primary" && (!src.ratings || !Object.keys(src.ratings).length); });
    box.appendChild(el("p", { text: provisional.length + " outlet labels are provisional starting assumptions. RSS feeds do not contain everything an outlet publishes. No match in a feed does not establish that an outlet ignored a story." }));
    box.appendChild(el("a", { href: "#how-it-works", text: "Inspect the sources and selection rules" }));
  }

    return { provenance: provenance, claims: claimEvidence, health: renderHealth };
  } };
})(globalThis);
