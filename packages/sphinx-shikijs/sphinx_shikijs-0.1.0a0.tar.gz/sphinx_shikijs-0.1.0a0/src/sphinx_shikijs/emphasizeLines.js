(() => {
  // Add highlight-line class to lines in data-hl-lines attribute.
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-hl-lines]").forEach((el) => {
      const { hlLines } = el.dataset;
      const lineSpans = Array.from(el.querySelectorAll("span.line"));

      hlLines
        .split(",")
        .map((s) => Number(s))
        .forEach((lineno) => {
          lineSpans[lineno - 1].classList.add("highlight-line");
        });
    });
  });
})();
