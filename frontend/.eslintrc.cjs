module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  settings: { react: { version: '18.0' } },
  ignorePatterns: ['dist/', 'node_modules/'],
  rules: {
    'react-refresh/only-export-components': 'warn'
  }
};
