const path = require('path');
const version = require('./package.json').version;
const webpack = require('webpack');

// Custom webpack rules
const rules = [
  { test: /\.ts$/, loader: 'ts-loader' },
  { test: /\.js$/, loader: 'source-map-loader' },
  { test: /\.css$/, use: ['style-loader', 'css-loader'] }
];

// Packages that shouldn't be bundled but loaded at runtime
const externals = ['@jupyter-widgets/base'];

const resolve = {
  // Add '.ts' and '.tsx' as resolvable extensions.
  extensions: ['.webpack.js', '.web.js', '.ts', '.js']
};

module.exports = (env, argv) => {
  const mode = argv.mode || 'production';
  const plugins = [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(mode)
    })
  ];
  return [
    /**
     * Notebook extension
     *
     * This bundle only contains the part of the JavaScript that is run on load of
     * the notebook.
     */
    {
      entry: './src/extension.ts',
      output: {
        filename: 'index.js',
        path: path.resolve(__dirname, 'unfolded', 'map_sdk', 'nbextension'),
        libraryTarget: 'amd',
        publicPath: ''
      },
      module: {
        rules: rules
      },
      ...(mode === 'development' ? { devtool: 'source-map' } : {}),
      plugins,
      externals,
      resolve
    },

    /**
     * Embeddable @unfolded/jupyter-map-sdk bundle
     *
     * This bundle is almost identical to the notebook extension bundle. The only
     * difference is in the configuration of the webpack public path for the
     * static assets.
     *
     * The target bundle is always `dist/index.js`, which is the path required by
     * the custom widget embedder.
     */
    {
      entry: './src/index.ts',
      output: {
        filename: 'index.js',
        path: path.resolve(__dirname, 'dist'),
        libraryTarget: 'amd',
        library: '@unfolded/jupyter-map-sdk',
        publicPath:
          'https://unpkg.com/@unfolded/jupyter-map-sdk@' + version + '/dist/'
      },
      devtool: 'source-map',
      module: {
        rules: rules
      },
      plugins,
      externals,
      resolve
    },

    /**
     * Documentation widget bundle
     *
     * This bundle is used to embed widgets in the package documentation.
     */
    {
      entry: './src/index.ts',
      output: {
        filename: 'embed-bundle.js',
        path: path.resolve(__dirname, 'docs', 'source', '_static'),
        library: '@unfolded/jupyter-map-sdk',
        libraryTarget: 'amd'
      },
      module: {
        rules: rules
      },
      devtool: 'source-map',
      plugins,
      externals,
      resolve
    }
  ];
};
