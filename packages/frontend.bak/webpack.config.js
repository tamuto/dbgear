const HtmlWebpackPlugin = require('html-webpack-plugin')
const path = require('path')

module.exports = {
  entry: './src/main.tsx',
  output: {
    path: path.resolve(__dirname, '../dbgear-web/dbgear_web/static'),
    filename: 'main.js',
  },
  devtool: 'source-map',
  resolve: {
    alias: {
      '~/api': path.resolve(__dirname, 'src/api'),
      '~/cmp': path.resolve(__dirname, 'src/components'),
      '~/img': path.resolve(__dirname, 'src/resources/img')
    },
    extensions: [".ts", ".tsx", ".js", ".jsx"]
  },
  module: {
    rules: [
      {
        test: /\.ts(x)?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'swc-loader',
            options: {
              jsc: {
                parser: {
                  syntax: "typescript",
                  tsx: true,
                  decorators: true,
                  dynamicImport: true
                },
                transform: {
                  react: {
                    runtime: 'automatic',
                    pragma: 'jsx',
                    importSource: '@emotion/react'
                  },
                  useDefineForClassFields: false
                }
              },
              env: {
                targets: {
                  chrome: "80",
                  firefox: "74",
                  safari: "13",
                  edge: "80",
                },
                mode: "entry",
                coreJs: "3.31.0"
              }
            }
          }
        ]
      },
      {
        test: /\.(jpg|png|svg)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'file-loader?name=[name].[ext]'
          }
        ]
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      cache: false,
      hash: true
    })
  ]
}
