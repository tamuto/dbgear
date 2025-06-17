import { useCallback } from 'react'
import { ApiErrorInfo, ErrorType, ErrorSeverity } from '@/types/api'
import { useToastNotifications } from '@/hooks/use-toast-notifications'

/**
 * Centralized error handling system
 * Provides consistent error processing and user feedback
 */

export interface ErrorHandlerConfig {
  // Global settings
  enableNotifications?: boolean
  enableConsoleLogging?: boolean
  enableErrorReporting?: boolean
  
  // Notification settings
  showNetworkErrors?: boolean
  showValidationErrors?: boolean
  showServerErrors?: boolean
  
  // Retry settings
  maxRetries?: number
  retryDelay?: number
}

const defaultConfig: ErrorHandlerConfig = {
  enableNotifications: true,
  enableConsoleLogging: true,
  enableErrorReporting: false,
  showNetworkErrors: true,
  showValidationErrors: true,
  showServerErrors: true,
  maxRetries: 3,
  retryDelay: 1000,
}

/**
 * Error handler hook
 */
export function useErrorHandler(config: ErrorHandlerConfig = {}) {
  const finalConfig = { ...defaultConfig, ...config }
  const { showToast, showError, showWarning, showInfo } = useToastNotifications()

  const handleError = useCallback((error: ApiErrorInfo) => {
    // Console logging
    if (finalConfig.enableConsoleLogging) {
      console.group(`🚨 API Error [${error.type}]`)
      console.error('Code:', error.code)
      console.error('Message:', error.message)
      console.error('Severity:', error.severity)
      if (error.details) {
        console.error('Details:', error.details)
      }
      console.groupEnd()
    }

    // Error reporting (if enabled)
    if (finalConfig.enableErrorReporting) {
      reportError(error)
    }

    // User notifications
    if (finalConfig.enableNotifications && error.shouldNotify) {
      showErrorNotification(error, { showToast, showError, showWarning, showInfo })
    }
  }, [finalConfig, showToast, showError, showWarning, showInfo])

  const handleValidationError = useCallback((
    fieldErrors: Record<string, string[]>,
    generalMessage?: string
  ) => {
    if (generalMessage) {
      showWarning({
        title: 'Validation Error',
        description: generalMessage,
      })
    }

    // Log field-specific errors for debugging
    if (finalConfig.enableConsoleLogging) {
      console.group('🔍 Validation Errors')
      Object.entries(fieldErrors).forEach(([field, errors]) => {
        console.warn(`${field}:`, errors.join(', '))
      })
      console.groupEnd()
    }
  }, [finalConfig.enableConsoleLogging, showWarning])

  const handleNetworkError = useCallback(() => {
    if (finalConfig.showNetworkErrors) {
      showError({
        title: 'Connection Error',
        description: 'Unable to connect to the server. Please check your internet connection and try again.',
        action: {
          label: 'Retry',
          onClick: () => window.location.reload(),
        },
      })
    }
  }, [finalConfig.showNetworkErrors, showError])

  return {
    handleError,
    handleValidationError,
    handleNetworkError,
  }
}

/**
 * Show appropriate notification based on error type and severity
 */
function showErrorNotification(
  error: ApiErrorInfo,
  notificationMethods: {
    showToast: (options: any) => void
    showError: (options: any) => void
    showWarning: (options: any) => void
    showInfo: (options: any) => void
  }
) {
  const { showToast, showError, showWarning, showInfo } = notificationMethods

  const baseOptions = {
    title: getErrorTitle(error),
    description: error.message,
  }

  switch (error.severity) {
    case ErrorSeverity.CRITICAL:
      showError({
        ...baseOptions,
        duration: 0, // Don't auto-dismiss critical errors
        action: error.retryable ? {
          label: 'Retry',
          onClick: () => window.location.reload(),
        } : undefined,
      })
      break

    case ErrorSeverity.ERROR:
      showError(baseOptions)
      break

    case ErrorSeverity.WARNING:
      showWarning(baseOptions)
      break

    case ErrorSeverity.INFO:
      showInfo(baseOptions)
      break

    default:
      showToast(baseOptions)
  }
}

/**
 * Get user-friendly error title based on error type
 */
function getErrorTitle(error: ApiErrorInfo): string {
  switch (error.type) {
    case ErrorType.NETWORK:
      return 'Connection Error'
    case ErrorType.VALIDATION:
      return 'Validation Error'
    case ErrorType.AUTHORIZATION:
      return 'Access Denied'
    case ErrorType.SERVER:
      return 'Server Error'
    default:
      return 'Unexpected Error'
  }
}

/**
 * Report error to external service (placeholder)
 */
function reportError(error: ApiErrorInfo) {
  // Integrate with error reporting service like Sentry, LogRocket, etc.
  // Example:
  // Sentry.captureException(new Error(error.message), {
  //   tags: {
  //     errorType: error.type,
  //     errorCode: error.code,
  //   },
  //   extra: error.details,
  // })
  
  console.info('📊 Error reported:', error.code)
}

/**
 * Global error boundary helper
 */
export function createErrorBoundaryHandler() {
  return (error: Error, errorInfo: { componentStack: string }) => {
    console.group('🔥 React Error Boundary')
    console.error('Error:', error)
    console.error('Component Stack:', errorInfo.componentStack)
    console.groupEnd()

    // Report to external service
    // reportError({
    //   type: ErrorType.UNKNOWN,
    //   severity: ErrorSeverity.CRITICAL,
    //   code: 'REACT_ERROR',
    //   message: error.message,
    //   details: { componentStack: errorInfo.componentStack },
    // })
  }
}

/**
 * Retry utility with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      
      if (attempt === maxRetries) {
        break
      }

      // Check if error is retryable
      const apiError = (error as Error & { apiErrorInfo?: ApiErrorInfo }).apiErrorInfo
      if (apiError && !apiError.retryable) {
        break
      }

      // Exponential backoff
      const delay = baseDelay * Math.pow(2, attempt)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  throw lastError!
}