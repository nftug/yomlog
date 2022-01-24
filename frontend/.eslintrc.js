module.exports = {
  env: {
    node: true,
    commonjs: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/base',
    'plugin:vue/essential',
    'prettier',
    'jest',
  ],
  rules: {
    'no-console': 'off',
  },
  parserOptions: {
    parser: 'babel-eslint',
    ecmaVersion: 2017,
    sourceType: 'module',
  },
}
