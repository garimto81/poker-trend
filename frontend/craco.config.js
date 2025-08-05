const CracoAlias = require('craco-alias');

module.exports = {
  plugins: [
    {
      plugin: CracoAlias,
      options: {
        source: 'tsconfig',
        baseUrl: './src',
        tsConfigPath: './tsconfig.json',
      },
    },
  ],
  webpack: {
    configure: (webpackConfig) => {
      // Ant Design 최적화
      webpackConfig.resolve.alias = {
        ...webpackConfig.resolve.alias,
        '@': require('path').resolve(__dirname, 'src'),
      };
      
      return webpackConfig;
    },
  },
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
};