import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ApiResponse, ApiError, ApiErrorInfo, ErrorType, ErrorSeverity } from '@/types/api'

/**
 * API Client configuration and instance
 * Provides configured axios instance with interceptors and error handling
 */

// Create axios instance with default configuration
export const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Transform axios error to standardized API error
 */
function transformAxiosError(error: AxiosError): ApiErrorInfo {
  // Network error (no response)
  if (!error.response) {
    return {
      type: ErrorType.NETWORK,
      severity: ErrorSeverity.ERROR,
      code: 'NETWORK_ERROR',
      message: 'Network connection failed. Please check your internet connection.',
      retryable: true,
      shouldNotify: true,
    }
  }

  const { status, data } = error.response

  // Server returned an error response
  switch (status) {
    case 400:
      return {
        type: ErrorType.VALIDATION,
        severity: ErrorSeverity.WARNING,
        code: 'BAD_REQUEST',
        message: (data as any)?.message || 'Invalid request data',
        details: (data as any)?.details,
        retryable: false,
        shouldNotify: true,
      }

    case 401:
      return {
        type: ErrorType.AUTHORIZATION,
        severity: ErrorSeverity.ERROR,
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
        retryable: false,
        shouldNotify: true,
      }

    case 403:
      return {
        type: ErrorType.AUTHORIZATION,
        severity: ErrorSeverity.ERROR,
        code: 'FORBIDDEN',
        message: 'Access denied',
        retryable: false,
        shouldNotify: true,
      }

    case 404:
      return {
        type: ErrorType.VALIDATION,
        severity: ErrorSeverity.WARNING,
        code: 'NOT_FOUND',
        message: 'Resource not found',
        retryable: false,
        shouldNotify: true,
      }

    case 422:
      return {
        type: ErrorType.VALIDATION,
        severity: ErrorSeverity.WARNING,
        code: 'VALIDATION_ERROR',
        message: (data as any)?.message || 'Validation failed',
        details: (data as any)?.details,
        retryable: false,
        shouldNotify: true,
      }

    case 429:
      return {
        type: ErrorType.SERVER,
        severity: ErrorSeverity.WARNING,
        code: 'RATE_LIMITED',
        message: 'Too many requests. Please try again later.',
        retryable: true,
        shouldNotify: true,
      }

    case 500:
    case 502:
    case 503:
    case 504:
      return {
        type: ErrorType.SERVER,
        severity: ErrorSeverity.CRITICAL,
        code: 'SERVER_ERROR',
        message: 'Server error occurred. Please try again later.',
        retryable: true,
        shouldNotify: true,
      }

    default:
      return {
        type: ErrorType.UNKNOWN,
        severity: ErrorSeverity.ERROR,
        code: 'UNKNOWN_ERROR',
        message: (data as any)?.message || `HTTP ${status}: ${error.message}`,
        details: { status, statusText: error.response.statusText },
        retryable: false,
        shouldNotify: true,
      }
  }
}

/**
 * Request interceptor - Add common headers, authentication, etc.
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add timestamp for cache busting if needed
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }

    // Add authorization header if token exists
    // const token = localStorage.getItem('authToken')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - Transform responses and handle common errors
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse<ApiResponse<unknown>> => {
    // Transform successful responses to standard format
    return {
      ...response,
      data: {
        success: true,
        data: response.data,
      },
    }
  },
  (error: AxiosError) => {
    // Transform error to standardized format and reject
    const apiError = transformAxiosError(error)
    
    // Create standardized error response for debugging
    // const errorResponse: ApiError = {
    //   success: false,
    //   error: {
    //     code: apiError.code,
    //     message: apiError.message,
    //     details: apiError.details,
    //   },
    // }

    // Attach additional error info for error handlers
    const enhancedError = new Error(apiError.message) as Error & { apiErrorInfo: ApiErrorInfo }
    enhancedError.apiErrorInfo = apiError

    return Promise.reject(enhancedError)
  }
)

/**
 * API request helper function
 */
export async function apiRequest<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await apiClient.request<ApiResponse<T>>(config)
    
    if (response.data.success) {
      return response.data.data
    } else {
      // This shouldn't happen due to interceptor, but just in case
      throw new Error('API returned unsuccessful response')
    }
  } catch (error) {
    // Re-throw the error with API error info attached
    throw error
  }
}

/**
 * Convenience methods for different HTTP methods
 */
export const api = {
  get: <T>(url: string, params?: Record<string, unknown>): Promise<T> =>
    apiRequest<T>({ method: 'GET', url, params }),

  post: <T>(url: string, data?: unknown, params?: Record<string, unknown>): Promise<T> =>
    apiRequest<T>({ method: 'POST', url, data, params }),

  put: <T>(url: string, data?: unknown, params?: Record<string, unknown>): Promise<T> =>
    apiRequest<T>({ method: 'PUT', url, data, params }),

  delete: <T>(url: string, params?: Record<string, unknown>): Promise<T> =>
    apiRequest<T>({ method: 'DELETE', url, params }),

  patch: <T>(url: string, data?: unknown, params?: Record<string, unknown>): Promise<T> =>
    apiRequest<T>({ method: 'PATCH', url, data, params }),
}

export default api