var BundleTracker = require('webpack-bundle-tracker')
var HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  transpileDependencies: ['vuetify'],
  outputDir: '../static/webpack_bundles/',
  indexPath: '../../templates/index.html',
  publicPath:
    process.env.NODE_ENV === 'production' ? '/static/webpack_bundles/' : '/',
  productionSourceMap: process.env.NODE_ENV === 'production' ? false : true,

  configureWebpack: {
    plugins: [
      new HtmlWebpackPlugin({
        template:
          process.env.NODE_ENV === 'production'
            ? 'public/index.html'
            : 'index_dev.html',
        favicon: './public/favicon.ico',
        inject: process.env.NODE_ENV === 'production' ? false : true,
        minify: false,
      }),
      new BundleTracker({ filename: '../webpack-stats.json' }),
    ],
    devtool: 'source-map',
  },
  css: {
    sourceMap: true,
  },
  devServer: {
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
}
