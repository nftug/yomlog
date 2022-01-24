module.exports = {
  presets: ['@vue/app', '@babel/preset-env'],
  env: {
    test: {
      presets: [['@babel/preset-env', { targets: { node: 'current' } }]],
    },
  },
}
