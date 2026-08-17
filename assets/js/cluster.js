/* Community cluster — fills the detail panel from whichever name is hovered or
 * focused.
 *
 * Focus matters as much as hover here: the names are buttons precisely so that
 * keyboard and touch users can reach them, and binding hover alone would strand
 * both. Screen readers don't need any of this — each button's aria-label
 * already carries the full record — so the panel is aria-hidden.
 */

(function () {
  "use strict";

  var cluster = document.querySelector(".cluster");
  if (!cluster) return;

  var leadEl = cluster.querySelector(".cluster__lead");
  var detailEl = cluster.querySelector(".cluster__detail");
  var names = cluster.querySelectorAll(".cluster__name");
  if (!leadEl || !detailEl || !names.length) return;

  var resting = detailEl.textContent;

  function show(btn) {
    leadEl.textContent = btn.dataset.lead || "";
    detailEl.textContent = btn.dataset.detail || "";
    names.forEach(function (n) {
      n.classList.toggle("is-active", n === btn);
    });
  }

  function clear() {
    leadEl.textContent = "";
    detailEl.textContent = resting;
    names.forEach(function (n) {
      n.classList.remove("is-active");
    });
  }

  names.forEach(function (btn) {
    btn.addEventListener("mouseenter", function () { show(btn); });
    btn.addEventListener("focus", function () { show(btn); });
    // Tap: buttons fire click on touch, where mouseenter is unreliable.
    btn.addEventListener("click", function () { show(btn); });
    btn.addEventListener("blur", clear);
  });

  // Only clear on the way out of the whole cluster, so moving between names
  // doesn't flicker the panel back to its resting text.
  cluster.addEventListener("mouseleave", clear);
})();
