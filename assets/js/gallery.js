/* Photo strip arrows.
 *
 * The strip scrolls perfectly well without this - trackpad, wheel, touch and
 * keyboard all work on an overflow container. These buttons are an affordance
 * for people using a mouse with no horizontal wheel, who otherwise have only a
 * thin overlay scrollbar to aim at.
 *
 * The buttons ship with the `hidden` attribute set and are revealed here, so a
 * page where this script never runs shows no dead controls.
 */

(function () {
  "use strict";

  document.querySelectorAll(".gallery-strip").forEach(function (strip) {
    var rail = strip.querySelector(".gallery");
    var prev = strip.querySelector(".gallery__nav--prev");
    var next = strip.querySelector(".gallery__nav--next");
    if (!rail || !prev || !next) return;

    // Nothing overflows, so there is nothing to scroll to.
    if (rail.scrollWidth <= rail.clientWidth) return;

    prev.hidden = false;
    next.hidden = false;

    function page() {
      // Just under a full screen, so a photo stays in view as an anchor.
      return Math.max(160, rail.clientWidth * 0.8);
    }

    function sync() {
      // A 2px slack absorbs the sub-pixel scrollLeft browsers report at the
      // extremes, which would otherwise leave a button enabled but inert.
      var max = rail.scrollWidth - rail.clientWidth;
      prev.disabled = rail.scrollLeft <= 2;
      next.disabled = rail.scrollLeft >= max - 2;
    }

    function go(dir) {
      rail.scrollBy({
        left: dir * page(),
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth"
      });
    }

    prev.addEventListener("click", function () { go(-1); });
    next.addEventListener("click", function () { go(1); });
    rail.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);

    sync();
  });
})();
