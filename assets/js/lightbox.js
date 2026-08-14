/* Minimal photo lightbox — no dependencies.
 *
 * Keyboard: Escape closes, arrow keys move. Focus is trapped inside the dialog
 * while it's open and returned to the thumbnail that opened it on close, so
 * keyboard users don't lose their place in the grid.
 */

(function () {
  "use strict";

  var box = document.getElementById("lightbox");
  if (!box) return;

  var img = document.getElementById("lightbox-img");
  var caption = document.getElementById("lightbox-caption");
  var triggers = Array.prototype.slice.call(
    document.querySelectorAll("[data-lightbox]")
  );
  if (!triggers.length) return;

  var current = 0;
  var lastFocused = null;

  function show(index) {
    current = (index + triggers.length) % triggers.length; // wrap both ways
    var t = triggers[current];
    img.src = t.dataset.src;
    img.alt = t.dataset.alt || "";
    caption.textContent = t.dataset.caption || "";
    caption.hidden = !t.dataset.caption;
  }

  function open(index) {
    lastFocused = document.activeElement;
    show(index);
    box.hidden = false;
    document.body.style.overflow = "hidden"; // don't scroll the page behind
    box.querySelector("[data-close]").focus();
  }

  function close() {
    box.hidden = true;
    img.src = "";
    document.body.style.overflow = "";
    if (lastFocused) lastFocused.focus();
  }

  triggers.forEach(function (t, i) {
    t.addEventListener("click", function () {
      open(i);
    });
  });

  box.querySelector("[data-close]").addEventListener("click", close);
  box.querySelector("[data-prev]").addEventListener("click", function () {
    show(current - 1);
  });
  box.querySelector("[data-next]").addEventListener("click", function () {
    show(current + 1);
  });

  // Clicking the backdrop (but not the image or a button) closes.
  box.addEventListener("click", function (e) {
    if (e.target === box) close();
  });

  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;

    if (e.key === "Escape") {
      close();
    } else if (e.key === "ArrowLeft") {
      show(current - 1);
    } else if (e.key === "ArrowRight") {
      show(current + 1);
    } else if (e.key === "Tab") {
      // Trap focus: cycle through the dialog's own buttons only.
      var focusable = box.querySelectorAll("button");
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
})();
