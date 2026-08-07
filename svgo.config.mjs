// svgo.config.mjs — check-only config for hand-authored fdars diagrams.
//
// Gate pattern (idempotence check — not a source-vs-output diff):
//   FIRST=$(npx svgo@3.3.4 --config svgo.config.mjs --quiet --input "$svg" --output -)
//   SECOND=$(echo "$FIRST" | npx svgo@3.3.4 --config svgo.config.mjs --quiet --input - --output -)
//   diff <(echo "$FIRST") <(echo "$SECOND")  # must be empty
//
// WHY idempotence, not diff-against-source:
//   svgo@3.3.4's XML serializer always normalises whitespace and attribute ordering
//   regardless of plugin settings (this is not disableable via overrides). A direct
//   diff between svgo's stdout and the hand-authored source will therefore always show
//   cosmetic whitespace differences — even with every dangerous plugin disabled.
//   The idempotence check (pass 1 == pass 2) proves the config applies no further
//   semantic transformations: if the diagram is already "settled" under the config,
//   it is conforming.
//
// NEVER use svgo to rewrite committed hand-authored SVGs (D-02: hand-authored markup
// is the source of truth). Always invoke in stdout mode (--output -), never -o <file>.
export default {
  plugins: [
    {
      name: "preset-default",
      params: {
        overrides: {
          // Preserve the CSS <style> block with class definitions (.ttl .sub .lab .sm .mono)
          inlineStyles: false,
          minifyStyles: false,
          // Preserve element IDs (used for <g id="...">, gradients, defs cross-references)
          cleanupIds: false,
          // Preserve <desc> elements (accessibility; may be added to diagrams)
          removeDesc: false,
          // Preserve role="img" and aria-label (accessibility attributes)
          // removeUnknownsAndDefaults strips role/aria-* that are not in SVG spec's known set
          removeUnknownsAndDefaults: false,
          // Preserve viewBox (never remove viewBox from hand-authored diagrams)
          removeViewBox: false,
          // Preserve path data exactly — convertPathData rewrites coordinate sequences
          // and together with mergePaths causes non-idempotent output on the second pass.
          convertPathData: false,
          // Preserve separate <path> elements — mergePaths joins sibling paths into one
          // combined `d` attribute, changing diagram structure and causing non-idempotence.
          mergePaths: false,
          // Preserve <g> grouping structure — collapseGroups unwraps single-child groups
          // used as coordinate-transform anchors in the hand-authored diagrams.
          collapseGroups: false,
        },
      },
    },
  ],
};
