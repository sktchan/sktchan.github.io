/* Community ribbon — keeps the popovers inside the frame.
 *
 * The reveal itself is pure CSS: :hover and :focus-visible on the row button
 * show the popover next to it. That is deliberate, so the ribbon still works
 * with JavaScript off. Everything here is refinement on top.
 *
 * The build already picks a side for each popover from the bar's position —
 * see the Liquid in _includes/community-ribbon.html — but it can only guess
 * from percentages, not from how wide the text actually turned out. This
 * measures the real box and flips it if the guess overflowed.
 *
 * Focus matters as much as hover: the rows are buttons precisely so keyboard
 * and touch users can reach them, and binding hover alone would strand both.
 * Screen readers need none of it — every button's aria-label already carries
 * the full record, note included — so the popovers are aria-hidden.
 */

(function () {
  "use strict";

  var ribbon = document.querySelector(".cribbon");
  if (!ribbon) return;

  var frame = ribbon.querySelector(".cribbon__frame");
  var rows = ribbon.querySelectorAll(".cribbon__row");
  if (!frame || !rows.length) return;

  // The pinned-sheet layout below this width positions popovers with `fixed`,
  // where flipping sides is meaningless. Matches the CSS breakpoint.
  var wide = window.matchMedia("(min-width: 40.0625rem)");

  var active = null;

  function place(row) {
    var pop = row.querySelector(".cribbon__pop");
    if (!pop || !wide.matches) return;

    // Reset to the build-time guess before measuring, or successive passes
    // would compound each other's corrections.
    pop.classList.remove("is-flipped");

    var bounds = frame.getBoundingClientRect();
    var box = pop.getBoundingClientRect();

    // A popover anchored left that runs off the right edge — or anchored right
    // that runs off the left — swaps to the other side. `is-flipped` inverts
    // whichever of --left/--right the markup chose.
    var overflowsRight = box.right > bounds.right;
    var overflowsLeft = box.left < bounds.left;

    if (overflowsRight || overflowsLeft) pop.classList.add("is-flipped");
  }

  function show(row) {
    if (active && active !== row) hide(active);
    active = row;
    row.querySelector(".cribbon__hit").classList.add("is-active");
    place(row);
  }

  function hide(row) {
    var hit = row.querySelector(".cribbon__hit");
    if (hit) hit.classList.remove("is-active");
    if (active === row) active = null;
  }

  rows.forEach(function (row) {
    var hit = row.querySelector(".cribbon__hit");
    if (!hit) return;

    hit.addEventListener("mouseenter", function () { show(row); });
    hit.addEventListener("focus", function () { show(row); });
    // Tap: buttons fire click on touch, where mouseenter is unreliable.
    hit.addEventListener("click", function () { show(row); });
    hit.addEventListener("blur", function () { hide(row); });
  });

  // Only clear on the way out of the whole ribbon, so moving between rows
  // doesn't flicker the popover off and on again.
  ribbon.addEventListener("mouseleave", function () {
    if (active) hide(active);
  });

  // A tapped-open popover on touch has no blur and no mouseleave to close it.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || !active) return;
    var hit = active.querySelector(".cribbon__hit");
    hide(active);
    if (hit) hit.blur();
  });

  // Text reflows at other widths, so a side chosen at one size can be wrong at
  // the next. Re-measure whatever is open.
  window.addEventListener("resize", function () {
    if (active) place(active);
  });
})();
