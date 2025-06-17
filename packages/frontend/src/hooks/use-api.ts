import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query'
import { api } from '@/lib/api-client'
import { ApiErrorInfo, QueryConfig, MutationConfig, QueryKey, HttpMethod } from '@/types/api'
import { useErrorHandler } from '@/lib/error-handler'

/**
 * Custom hooks for API operations using TanStack Query
 * Provides type-safe, declarative API state management
 */

/**
 * Query key factory for consistent key generation
 */
export const queryKeys = {
  // Base queries
  all: ['api'] as const,
  
  // Entity-specific queries
  projects: () => [...queryKeys.all, 'projects'] as const,
  project: (id: string) => [...queryKeys.projects(), id] as const,
  
  schemas: () => [...queryKeys.all, 'schemas'] as const,
  schema: (id: string) => [...queryKeys.schemas(), id] as const,
  
  tables: (schemaId?: string) => [...queryKeys.all, 'tables', { schemaId }] as const,
  table: (id: string) => [...queryKeys.all, 'tables', id] as const,
  
  environments: () => [...queryKeys.all, 'environments'] as const,
  environment: (id: string) => [...queryKeys.environments(), id] as const,
  
  // Custom query with parameters
  custom: (scope: string, params?: Record<string, unknown>) => 
    [...queryKeys.all, scope, params] as const,
}

/**
 * Generic query hook
 */
export function useApiQuery<TData>(
  queryKey: QueryKey,
  url: string,
  params?: Record<string, unknown>,
  options?: QueryConfig<TData>
): UseQueryResult<TData, ApiErrorInfo> {
  const { handleError } = useErrorHandler()

  return useQuery({
    queryKey,
    queryFn: () => api.get<TData>(url, params),
    enabled: options?.enabled ?? true,
    refetchOnWindowFocus: options?.refetchOnWindowFocus ?? false,
    refetchInterval: options?.refetchInterval,
    staleTime: options?.staleTime ?? 5 * 60 * 1000, // 5 minutes
    cacheTime: options?.cacheTime ?? 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      if (typeof options?.retry === 'function') {
        return options.retry(failureCount, (error as Error & { apiErrorInfo: ApiErrorInfo }).apiErrorInfo)
      }
      if (typeof options?.retry === 'number') {
        return failureCount < options.retry
      }
      if (options?.retry === false) {
        return false
      }
      
      // Default retry logic based on error type
      const apiError = (error as Error & { apiErrorInfo: ApiErrorInfo }).apiErrorInfo
      return apiError?.retryable === true && failureCount < 3
    },
    onSuccess: options?.onSuccess,
    onError: (error: Error & { apiErrorInfo: ApiErrorInfo }) => {
      const apiError = error.apiErrorInfo
      if (apiError?.shouldNotify) {
        handleError(apiError)
      }
      options?.onError?.(apiError)
    },
  })
}

/**
 * Generic mutation hook
 */
export function useApiMutation<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: MutationConfig<TData, TVariables>
): UseMutationResult<TData, ApiErrorInfo, TVariables> {
  const { handleError } = useErrorHandler()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn,
    onSuccess: (data, variables) => {
      options?.onSuccess?.(data, variables)
    },
    onError: (error: Error & { apiErrorInfo: ApiErrorInfo }, variables) => {
      const apiError = error.apiErrorInfo
      if (apiError?.shouldNotify) {
        handleError(apiError)
      }
      options?.onError?.(apiError, variables)
    },
    onSettled: (data, error, variables) => {
      const apiError = error ? (error as Error & { apiErrorInfo: ApiErrorInfo }).apiErrorInfo : null
      options?.onSettled?.(data, apiError, variables)
    },
  })
}

/**
 * HTTP method-specific mutation hooks
 */
export function useApiPost<TData, TVariables = unknown>(
  url: string,
  options?: MutationConfig<TData, TVariables>
) {
  return useApiMutation<TData, TVariables>(
    (variables: TVariables) => api.post<TData>(url, variables),
    options
  )
}

export function useApiPut<TData, TVariables = unknown>(
  url: string,
  options?: MutationConfig<TData, TVariables>
) {
  return useApiMutation<TData, TVariables>(
    (variables: TVariables) => api.put<TData>(url, variables),
    options
  )
}

export function useApiDelete<TData = void, TVariables = void>(
  url: string,
  options?: MutationConfig<TData, TVariables>
) {
  return useApiMutation<TData, TVariables>(
    () => api.delete<TData>(url),
    options
  )
}

export function useApiPatch<TData, TVariables = unknown>(
  url: string,
  options?: MutationConfig<TData, TVariables>
) {
  return useApiMutation<TData, TVariables>(
    (variables: TVariables) => api.patch<TData>(url, variables),
    options
  )
}

/**
 * Convenience hooks for common operations
 */

// Projects
export function useProjects(options?: QueryConfig<unknown[]>) {
  return useApiQuery(queryKeys.projects(), '/projects', undefined, options)
}

export function useProject(id: string, options?: QueryConfig<unknown>) {
  return useApiQuery(queryKeys.project(id), `/projects/${id}`, undefined, {
    enabled: !!id,
    ...options,
  })
}

// Schemas
export function useSchemas(options?: QueryConfig<unknown[]>) {
  return useApiQuery(queryKeys.schemas(), '/schemas', undefined, options)
}

export function useSchema(id: string, options?: QueryConfig<unknown>) {
  return useApiQuery(queryKeys.schema(id), `/schemas/${id}`, undefined, {
    enabled: !!id,
    ...options,
  })
}

// Tables
export function useTables(schemaId?: string, options?: QueryConfig<unknown[]>) {
  return useApiQuery(
    queryKeys.tables(schemaId),
    '/tables',
    schemaId ? { schema_id: schemaId } : undefined,
    options
  )
}

export function useTable(id: string, options?: QueryConfig<unknown>) {
  return useApiQuery(queryKeys.table(id), `/tables/${id}`, undefined, {
    enabled: !!id,
    ...options,
  })
}

// Environments
export function useEnvironments(options?: QueryConfig<unknown[]>) {
  return useApiQuery(queryKeys.environments(), '/environments', undefined, options)
}

export function useEnvironment(id: string, options?: QueryConfig<unknown>) {
  return useApiQuery(queryKeys.environment(id), `/environments/${id}`, undefined, {
    enabled: !!id,
    ...options,
  })
}

/**
 * Cache management utilities
 */
export function useInvalidateQueries() {
  const queryClient = useQueryClient()

  return {
    invalidateAll: () => queryClient.invalidateQueries({ queryKey: queryKeys.all }),
    invalidateProjects: () => queryClient.invalidateQueries({ queryKey: queryKeys.projects() }),
    invalidateSchemas: () => queryClient.invalidateQueries({ queryKey: queryKeys.schemas() }),
    invalidateTables: (schemaId?: string) => 
      queryClient.invalidateQueries({ queryKey: queryKeys.tables(schemaId) }),
    invalidateEnvironments: () => queryClient.invalidateQueries({ queryKey: queryKeys.environments() }),
    invalidateCustom: (scope: string) => 
      queryClient.invalidateQueries({ queryKey: [...queryKeys.all, scope] }),
  }
}