<template>
  <div class="error-boundary-wrapper">
    <div v-if="hasError" class="error-boundary">
      <v-alert
        type="error"
        variant="tonal"
        class="mb-4"
        prominent
      >
        <v-alert-title>Something went wrong</v-alert-title>
        <div class="error-message">
          {{ errorMessage }}
        </div>
        <div v-if="showDetails && errorDetails" class="error-details mt-3">
          <v-divider class="my-3" />
          <div class="text-caption font-weight-medium mb-2">Technical Details:</div>
          <v-code class="text-body-2">
            <pre>{{ errorDetails }}</pre>
          </v-code>
        </div>
      </v-alert>

      <v-card-actions class="justify-center pa-0">
        <v-btn
          color="primary"
          variant="outlined"
          @click="retry"
          :loading="retrying"
          prepend-icon="mdi-refresh"
        >
          Try Again
        </v-btn>
        <v-btn
          v-if="!showDetails && errorDetails"
          variant="text"
          size="small"
          @click="showDetails = true"
        >
          Show Details
        </v-btn>
        <v-btn
          variant="text"
          size="small"
          @click="reportError"
          prepend-icon="mdi-bug"
        >
          Report Issue
        </v-btn>
      </v-card-actions>
    </div>

    <slot v-else />
  </div>
</template>

<script>
/**
 * ErrorBoundary Component
 *
 * Catches and displays JavaScript errors gracefully.
 * Integrates with Vuex store for error notifications and logging.
 */
import { ref, onErrorCaptured } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ErrorBoundary',

  props: {
    fallbackMessage: {
      type: String,
      default: 'An unexpected error occurred. Please try again.',
    },
    showErrorDetails: {
      type: Boolean,
      default: false,
    },
  },

  emits: ['error', 'retry'],

  setup(props, { emit }) {
    const store = useStore()
    const hasError = ref(false)
    const errorMessage = ref('')
    const errorDetails = ref('')
    const showDetails = ref(props.showErrorDetails)
    const retrying = ref(false)

    const handleError = (error, instance, info) => {
      hasError.value = true
      errorMessage.value = props.fallbackMessage
      errorDetails.value = `${error.message}\n\nStack: ${error.stack}\n\nInfo: ${info}`

      // Log to store
      store.dispatch('ui/showError', error.message)

      // Emit error event
      emit('error', { error, instance, info })

      console.error('ErrorBoundary caught an error:', error, instance, info)
    }

    const retry = async () => {
      retrying.value = true

      try {
        // Reset error state
        hasError.value = false
        errorMessage.value = ''
        errorDetails.value = ''
        showDetails.value = props.showErrorDetails

        // Emit retry event
        emit('retry')

        // Small delay for UX
        await new Promise(resolve => setTimeout(resolve, 500))

      } catch (error) {
        console.error('Retry failed:', error)
        store.dispatch('ui/showError', 'Retry failed. Please refresh the page.')
      } finally {
        retrying.value = false
      }
    }

    const reportError = () => {
      const reportData = {
        message: errorMessage.value,
        details: errorDetails.value,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }

      // Copy to clipboard for easy reporting
      navigator.clipboard.writeText(JSON.stringify(reportData, null, 2))
        .then(() => {
          store.dispatch('ui/showSuccess', 'Error details copied to clipboard')
        })
        .catch(() => {
          store.dispatch('ui/showWarning', 'Could not copy to clipboard')
        })
    }

    // Capture errors from child components
    onErrorCaptured(handleError)

    return {
      hasError,
      errorMessage,
      errorDetails,
      showDetails,
      retrying,
      retry,
      reportError,
    }
  },
}
</script>

<style scoped>
.error-boundary {
  padding: 20px;
  text-align: center;
}

.error-message {
  margin-top: 8px;
  font-size: 1rem;
}

.error-details {
  text-align: left;
}

.v-code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

pre {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.4;
}
</style>
