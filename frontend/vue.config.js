// frontend/vue.config.js
const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  // Production optimizations
  productionSourceMap: false,

  // Bundle analyzer for build analysis
  pluginOptions: {
    webpackBundleAnalyzer: {
      openAnalyzer: false,
      analyzerMode: process.env.ANALYZE ? "static" : "disabled",
    },
  },

  configureWebpack: {
    // Performance optimizations
    optimization: {
      splitChunks: {
        chunks: "all",
        cacheGroups: {
          // Separate Vue ecosystem
          vue: {
            test: /[\\/]node_modules[\\/](vue|vue-router|vuex|vuetify)[\\/]/,
            name: "vue-ecosystem",
            chunks: "all",
            priority: 10,
          },
          // Separate chart libraries
          charts: {
            test: /[\\/]node_modules[\\/](chart\.js|vue-chartjs)[\\/]/,
            name: "charts",
            chunks: "all",
            priority: 10,
          },
          // Separate large libraries
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            chunks: "all",
            priority: 5,
          },
        },
      },
    },

    // Performance hints
    performance: {
      hints: process.env.NODE_ENV === "production" ? "warning" : false,
      maxAssetSize: 1024 * 1024, // 1MB
      maxEntrypointSize: 1024 * 1024, // 1MB
    },
  },

  // Development server configuration
  devServer: {
    port: 8080,
    host: "0.0.0.0",
    allowedHosts: "all",

    // Proxy API calls to backend
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },

    // Performance monitoring in development
    client: {
      overlay: {
        warnings: false,
        errors: true,
      },
    },
  },

  // PWA support (for future enhancement)
  pwa: {
    name: "HAIC Benchmark Suite",
    themeColor: "#1976D2",
    msTileColor: "#000000",
    appleMobileWebAppCapable: "yes",
    appleMobileWebAppStatusBarStyle: "black",

    // Workbox options
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
      exclude: [/\.map$/, /manifest\.json$/],
    },
  },

  // CSS optimization
  css: {
    extract: process.env.NODE_ENV === "production",
    sourceMap: process.env.NODE_ENV === "development",
  },
});
