/* Community map — fills the detail panel from whichever marker is hovered or
 * focused.
 *
 * Focus matters as much as hover here: the markers are buttons precisely so that
 * keyboard and touch users can reach them, and binding hover alone would strand
 * both. Screen readers don't need any of this — each button's aria-label
 * already carries the full record — so the panel is aria-hidden.
 */

(function () {
  "use strict";

  var map = document.querySelector(".cmap");
  if (!map) return;

  var leadEl = map.querySelector(".cmap__lead");
  var detailEl = map.querySelector(".cmap__detail");
  var dots = map.querySelectorAll(".cmap__dot");
  if (!leadEl || !detailEl || !dots.length) return;

  var resting = detailEl.textContent;

  function show(btn) {
    leadEl.textContent = btn.dataset.lead || "";
    detailEl.textContent = btn.dataset.detail || "";
    dots.forEach(function (n) {
      n.classList.toggle("is-active", n === btn);
    });
  }

  function clear() {
    leadEl.textContent = "";
    detailEl.textContent = resting;
    dots.forEach(function (n) {
      n.classList.remove("is-active");
    });
  }

  dots.forEach(function (btn) {
    btn.addEventListener("mouseenter", function () { show(btn); });
    btn.addEventListener("focus", function () { show(btn); });
    // Tap: buttons fire click on touch, where mouseenter is unreliable.
    btn.addEventListener("click", function () { show(btn); });
    btn.addEventListener("blur", clear);
  });

  // Only clear on the way out of the whole map, so moving between dots
  // doesn't flicker the panel back to its resting text.
  map.addEventListener("mouseleave", clear);
})();
