import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from '@/components/ui/sonner'

/**
 * Application providers setup
 * Configures TanStack Query and toast notifications
 */

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Default to 5 minutes stale time
      staleTime: 5 * 60 * 1000,
      // Default to 10 minutes cache time
      cacheTime: 10 * 60 * 1000,
      // Don't refetch on window focus by default
      refetchOnWindowFocus: false,
      // Retry failed requests up to 3 times
      retry: (failureCount, error) => {
        // Don't retry validation errors (4xx except 429)
        if (error instanceof Error) {
          const apiError = (error as Error & { apiErrorInfo?: any }).apiErrorInfo
          if (apiError && !apiError.retryable) {
            return false
          }
        }
        return failureCount < 3
      },
      // Use exponential backoff for retries
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // Retry mutations less aggressively
      retry: (failureCount, error) => {
        if (error instanceof Error) {
          const apiError = (error as Error & { apiErrorInfo?: any }).apiErrorInfo
          if (apiError && !apiError.retryable) {
            return false
          }
        }
        return failureCount < 1 // Only retry once for mutations
      },
    },
  },
})

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster 
        position="top-right"
        closeButton
        richColors
        expand
        visibleToasts={5}
      />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export { queryClient }