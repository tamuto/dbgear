import { useCallback } from 'react'
import { toast } from 'sonner'

/**
 * Toast notification integration using Sonner
 * Provides consistent notification interface for the application
 */

export interface ToastOptions {
  title?: string
  description: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

export interface ToastMethods {
  showToast: (options: ToastOptions) => void
  showSuccess: (options: ToastOptions) => void
  showError: (options: ToastOptions) => void
  showWarning: (options: ToastOptions) => void
  showInfo: (options: ToastOptions) => void
  showLoading: (message: string) => string | number
  dismiss: (id?: string | number) => void
  dismissAll: () => void
}

/**
 * Toast notifications hook
 */
export function useToastNotifications(): ToastMethods {
  const showToast = useCallback((options: ToastOptions) => {
    toast(options.title || options.description, {
      description: options.title ? options.description : undefined,
      duration: options.duration || 4000,
      action: options.action ? {
        label: options.action.label,
        onClick: options.action.onClick,
      } : undefined,
    })
  }, [])

  const showSuccess = useCallback((options: ToastOptions) => {
    toast.success(options.title || options.description, {
      description: options.title ? options.description : undefined,
      duration: options.duration || 4000,
      action: options.action ? {
        label: options.action.label,
        onClick: options.action.onClick,
      } : undefined,
    })
  }, [])

  const showError = useCallback((options: ToastOptions) => {
    toast.error(options.title || options.description, {
      description: options.title ? options.description : undefined,
      duration: options.duration || 6000, // Longer duration for errors
      action: options.action ? {
        label: options.action.label,
        onClick: options.action.onClick,
      } : undefined,
    })
  }, [])

  const showWarning = useCallback((options: ToastOptions) => {
    toast.warning(options.title || options.description, {
      description: options.title ? options.description : undefined,
      duration: options.duration || 5000,
      action: options.action ? {
        label: options.action.label,
        onClick: options.action.onClick,
      } : undefined,
    })
  }, [])

  const showInfo = useCallback((options: ToastOptions) => {
    toast.info(options.title || options.description, {
      description: options.title ? options.description : undefined,
      duration: options.duration || 4000,
      action: options.action ? {
        label: options.action.label,
        onClick: options.action.onClick,
      } : undefined,
    })
  }, [])

  const showLoading = useCallback((message: string) => {
    return toast.loading(message)
  }, [])

  const dismiss = useCallback((id?: string | number) => {
    if (id) {
      toast.dismiss(id)
    } else {
      toast.dismiss()
    }
  }, [])

  const dismissAll = useCallback(() => {
    toast.dismiss()
  }, [])

  return {
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
    dismiss,
    dismissAll,
  }
}

/**
 * Convenience functions for quick notifications
 */
export const notifications = {
  success: (message: string, title?: string) => {
    toast.success(title || message, {
      description: title ? message : undefined,
    })
  },

  error: (message: string, title?: string) => {
    toast.error(title || message, {
      description: title ? message : undefined,
      duration: 6000,
    })
  },

  warning: (message: string, title?: string) => {
    toast.warning(title || message, {
      description: title ? message : undefined,
      duration: 5000,
    })
  },

  info: (message: string, title?: string) => {
    toast.info(title || message, {
      description: title ? message : undefined,
    })
  },

  loading: (message: string) => {
    return toast.loading(message)
  },

  promise: <T>(
    promise: Promise<T>,
    messages: {
      loading: string
      success: string | ((data: T) => string)
      error: string | ((error: any) => string)
    }
  ) => {
    return toast.promise(promise, messages)
  },
}

/**
 * Toast configuration for different scenarios
 */
export const toastConfig = {
  // API operation success
  apiSuccess: (operation: string) => ({
    title: 'Success',
    description: `${operation} completed successfully`,
    duration: 3000,
  }),

  // API operation error
  apiError: (operation: string, error: string) => ({
    title: `${operation} Failed`,
    description: error,
    duration: 6000,
  }),

  // Form validation error
  validationError: (message: string) => ({
    title: 'Validation Error',
    description: message,
    duration: 5000,
  }),

  // Network error
  networkError: () => ({
    title: 'Connection Error',
    description: 'Unable to connect to the server. Please check your internet connection.',
    duration: 0, // Don't auto-dismiss
    action: {
      label: 'Retry',
      onClick: () => window.location.reload(),
    },
  }),

  // Data saved
  dataSaved: () => ({
    title: 'Saved',
    description: 'Your changes have been saved successfully',
    duration: 3000,
  }),

  // Data loading error
  loadingError: (resource: string) => ({
    title: 'Loading Error',
    description: `Failed to load ${resource}. Please try again.`,
    duration: 5000,
    action: {
      label: 'Retry',
      onClick: () => window.location.reload(),
    },
  }),
}