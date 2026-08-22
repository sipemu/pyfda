// Render math produced by pymdownx.arithmatex in "generic" mode, which wraps
// inline math in \( \) and display math in \[ \] (not $ / $$). We also keep the
// $ / $$ delimiters for robustness.
function fdarsRenderMath() {
  renderMathInElement(document.body, {
    delimiters: [
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
    ],
    throwOnError: false,
  });
}

// Material for MkDocs exposes a `document$` observable that also fires on
// instant navigation; fall back to DOMContentLoaded when it is unavailable.
if (typeof document$ !== "undefined" && document$.subscribe) {
  document$.subscribe(fdarsRenderMath);
} else {
  document.addEventListener("DOMContentLoaded", fdarsRenderMath);
}
