import vue from "@vue/eslint-config-prettier";

export default [
    vue,
    {
        rules: {
            // ── Indentation ────────────────────────────────────────────────────
            // 4 spaces for JS files, consistent with conventional style
            indent: ["error", 4],

            // ── Tabs vs Spaces ────────────────────────────────────────────────
            "no-mixed-spaces-and-tabs": "error",
            // Allow tabs for alignment (common in code)
            "no-tabs": "off",

            // ── Semicolons ────────────────────────────────────────────────────
            semi: ["error", "always"],

            // ── Quotes ────────────────────────────────────────────────────────
            quotes: ["error", "double", { avoidEscape: true, allowTemplateLiterals: true }],

            // ── Trailing commas ───────────────────────────────────────────────
            "comma-dangle": ["error", "always-multiline"],

            // ── Max line length ───────────────────────────────────────────────
            "max-len": ["warn", 100],

            // ── General style ─────────────────────────────────────────────────
            "no-trailing-spaces": "error",
            "no-multiple-empty-lines": ["error", { max: 1, maxBOF: 0, maxEOF: 0 }],
            "eol-last": ["error", "always"],
            "space-before-blocks": ["error", "always"],
            "space-in-parens": ["error", "never"],
            "space-infix-ops": "error",
            "arrow-spacing": ["error", { before: true, after: true }],
            "comma-spacing": ["error"],
            "key-spacing": ["error"],
            "keyword-spacing": ["error"],
        },
    },
];
