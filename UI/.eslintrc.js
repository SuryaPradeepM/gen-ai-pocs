module.exports = {
    parser: "@babel/eslint-parser",
    env: {
        browser: true,
        node: true,
        es6: true,
        jest: true,
    },
    extends: [
        "eslint:recommended",
        "plugin:react/recommended",
        "plugin:jsx-a11y/recommended"
    ],
    plugins: [
        "react",
        "react-hooks",
        "jsx-a11y",
    ],
    rules: {
        // strict: 0,
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
        "react/jsx-uses-react": "off",
        "react/react-in-jsx-scope": "off",
        "react/prop-types": "off",
        "jsx-a11y/no-autofocus": "off",
        "react/no-unescaped-entities": 0
    },
    settings: {
        react: {
            version: "detect"
        }
    }
}