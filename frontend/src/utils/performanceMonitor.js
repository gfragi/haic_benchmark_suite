/**
 * Performance Monitoring Utility
 *
 * Tracks and monitors application performance metrics
 * Provides insights for optimization and debugging
 */

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      navigation: [],
      apiCalls: [],
      componentRenders: [],
      memoryUsage: [],
      errors: [],
    };

    this.isEnabled = process.env.NODE_ENV === "development";
  }

  // Navigation timing
  trackNavigation() {
    if (!this.isEnabled || !window.performance) return;

    const navigation = window.performance.getEntriesByType("navigation")[0];
    if (navigation) {
      const timing = {
        timestamp: Date.now(),
        type: "navigation",
        domContentLoaded:
          navigation.domContentLoadedEventEnd -
          navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        totalTime: navigation.loadEventEnd - navigation.fetchStart,
      };

      this.metrics.navigation.push(timing);
      this.log("Navigation Performance:", timing);
    }
  }

  // API call timing
  trackApiCall(url, method, startTime, endTime, status) {
    if (!this.isEnabled) return;

    const duration = endTime - startTime;
    const metric = {
      timestamp: Date.now(),
      url,
      method,
      duration,
      status,
      slow: duration > 1000, // Flag calls taking > 1 second
    };

    this.metrics.apiCalls.push(metric);

    if (metric.slow) {
      console.warn(
        `🚨 Slow API call detected: ${method} ${url} took ${duration}ms`
      );
    }

    this.log("API Call:", metric);
  }

  // Component render timing
  trackComponentRender(componentName, startTime, endTime) {
    if (!this.isEnabled) return;

    const duration = endTime - startTime;
    const metric = {
      timestamp: Date.now(),
      component: componentName,
      duration,
      slow: duration > 16, // Flag renders taking > 16ms (60fps threshold)
    };

    this.metrics.componentRenders.push(metric);

    if (metric.slow) {
      console.warn(
        `🐌 Slow component render: ${componentName} took ${duration}ms`
      );
    }
  }

  // Memory usage tracking
  trackMemoryUsage() {
    if (!this.isEnabled || !window.performance.memory) return;

    const memory = window.performance.memory;
    const metric = {
      timestamp: Date.now(),
      used: memory.usedJSHeapSize,
      total: memory.totalJSHeapSize,
      limit: memory.jsHeapSizeLimit,
      usagePercent: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100,
    };

    this.metrics.memoryUsage.push(metric);

    if (metric.usagePercent > 80) {
      console.warn(`⚠️ High memory usage: ${metric.usagePercent.toFixed(1)}%`);
    }
  }

  // Error tracking
  trackError(error, context = {}) {
    const metric = {
      timestamp: Date.now(),
      message: error.message,
      stack: error.stack,
      context,
    };

    this.metrics.errors.push(metric);
    console.error("📊 Error tracked:", metric);
  }

  // Performance summary
  getSummary() {
    const summary = {
      navigation: this.getAverageTime(this.metrics.navigation, "totalTime"),
      apiCalls: {
        total: this.metrics.apiCalls.length,
        averageDuration: this.getAverageTime(this.metrics.apiCalls, "duration"),
        slowCalls: this.metrics.apiCalls.filter((call) => call.slow).length,
      },
      componentRenders: {
        total: this.metrics.componentRenders.length,
        averageDuration: this.getAverageTime(
          this.metrics.componentRenders,
          "duration"
        ),
        slowRenders: this.metrics.componentRenders.filter(
          (render) => render.slow
        ).length,
      },
      memoryUsage: this.getMemorySummary(),
      errors: this.metrics.errors.length,
    };

    return summary;
  }

  // Helper: Calculate average time
  getAverageTime(metrics, field) {
    if (metrics.length === 0) return 0;

    const total = metrics.reduce(
      (sum, metric) => sum + (metric[field] || 0),
      0
    );
    return Math.round(total / metrics.length);
  }

  // Helper: Memory usage summary
  getMemorySummary() {
    if (this.metrics.memoryUsage.length === 0) return null;

    const latest =
      this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1];
    const max = Math.max(
      ...this.metrics.memoryUsage.map((m) => m.usagePercent)
    );

    return {
      currentUsage: latest.usagePercent.toFixed(1) + "%",
      peakUsage: max.toFixed(1) + "%",
      usedMB: Math.round(latest.used / 1024 / 1024),
      totalMB: Math.round(latest.total / 1024 / 1024),
    };
  }

  // Export data for analysis
  exportData() {
    return {
      summary: this.getSummary(),
      raw: this.metrics,
      timestamp: new Date().toISOString(),
    };
  }

  // Clear all metrics
  clear() {
    Object.keys(this.metrics).forEach((key) => {
      this.metrics[key] = [];
    });
    console.log("🧹 Performance metrics cleared");
  }

  // Logging helper
  log(label, data) {
    if (this.isEnabled) {
      console.log(`📊 ${label}`, data);
    }
  }
}

// Global performance monitor instance
const performanceMonitor = new PerformanceMonitor();

// Vue plugin for automatic performance tracking
export const PerformancePlugin = {
  install(app) {
    // Track navigation on app mount
    app.mixin({
      mounted() {
        if (this.$route && this.$el) {
          performanceMonitor.trackNavigation();
        }
      },

      beforeUnmount() {
        // Cleanup if needed
      },
    });

    // Make performance monitor available globally
    app.config.globalProperties.$performance = performanceMonitor;
    app.provide("performance", performanceMonitor);
  },
};

export default performanceMonitor;
