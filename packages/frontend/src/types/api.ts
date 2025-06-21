/**
 * API Response Types
 * Defines the structure of API responses and error handling
 */

// Base API Response structure
export type ApiResponse<T> = 
  | ApiSuccess<T>
  | ApiError

export interface ApiSuccess<T> {
  success: true
  data: T
  message?: string
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

// Error severity levels for different handling strategies
export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning', 
  ERROR = 'error',
  CRITICAL = 'critical'
}

// Error types for categorized handling
export enum ErrorType {
  NETWORK = 'network',
  VALIDATION = 'validation', 
  AUTHORIZATION = 'authorization',
  SERVER = 'server',
  UNKNOWN = 'unknown'
}

// Extended error information
export interface ApiErrorInfo {
  type: ErrorType
  severity: ErrorSeverity
  code: string
  message: string
  details?: Record<string, unknown>
  retryable?: boolean
  shouldNotify?: boolean
}

// HTTP Methods
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

// API Request configuration
export interface ApiRequestConfig {
  method: HttpMethod
  url: string
  data?: unknown
  params?: Record<string, unknown>
  headers?: Record<string, string>
}

// Loading state for specific requests
export interface LoadingState {
  isLoading: boolean
  error: ApiErrorInfo | null
  lastUpdated?: Date
}

// Query key factory for TanStack Query
export interface QueryKeyConfig {
  scope: string
  entity?: string
  id?: string | number
  params?: Record<string, unknown>
}

export type QueryKey = readonly [string, ...unknown[]]

// Mutation options
export interface MutationConfig<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: ApiErrorInfo, variables: TVariables) => void
  onSettled?: (data: TData | undefined, error: ApiErrorInfo | null, variables: TVariables) => void
}

// Query options
export interface QueryConfig<TData> {
  enabled?: boolean
  refetchOnWindowFocus?: boolean
  refetchInterval?: number
  staleTime?: number
  cacheTime?: number
  retry?: boolean | number | ((failureCount: number, error: ApiErrorInfo) => boolean)
  onSuccess?: (data: TData) => void
  onError?: (error: ApiErrorInfo) => void
}