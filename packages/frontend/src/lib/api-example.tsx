import React from 'react'
import { useProjects, useApiPost, useInvalidateQueries } from '@/hooks/use-api'
import { notifications, toastConfig } from '@/hooks/use-toast-notifications'

/**
 * Example component showing how to use the new API system
 * This replaces the old nxio.ts callback-based approach
 */

interface Project {
  id: string
  name: string
  description: string
  created_at: string
}

interface CreateProjectData {
  name: string
  description: string
}

export function ApiExampleComponent() {
  // Query hook - automatically handles loading, error states, and caching
  const { 
    data: projects, 
    isLoading, 
    error, 
    refetch 
  } = useProjects({
    onError: (error) => {
      notifications.error('Failed to load projects', 'Loading Error')
    }
  })

  // Mutation hook - handles creating new projects
  const { invalidateProjects } = useInvalidateQueries()
  const createProjectMutation = useApiPost<Project, CreateProjectData>('/projects', {
    onSuccess: (data) => {
      notifications.success(`Project "${data.name}" created successfully`)
      // Invalidate and refetch projects list
      invalidateProjects()
    },
    onError: (error) => {
      notifications.error(error.message, 'Failed to create project')
    }
  })

  const handleCreateProject = async () => {
    createProjectMutation.mutate({
      name: 'New Project',
      description: 'Created via new API system'
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <span className="ml-2">Loading projects...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-red-800 font-medium">Error loading projects</h3>
        <p className="text-red-600 text-sm mt-1">{error.message}</p>
        <button 
          onClick={() => refetch()}
          className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Projects</h2>
        <button
          onClick={handleCreateProject}
          disabled={createProjectMutation.isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {createProjectMutation.isLoading ? 'Creating...' : 'Create Project'}
        </button>
      </div>

      <div className="grid gap-4">
        {projects?.map((project: Project) => (
          <div key={project.id} className="p-4 border rounded-lg">
            <h3 className="font-medium">{project.name}</h3>
            <p className="text-gray-600 text-sm">{project.description}</p>
            <p className="text-gray-400 text-xs mt-2">
              Created: {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Comparison with old nxio.ts approach:
 * 
 * OLD WAY (callback-based):
 * ```typescript
 * const [loading, setLoading] = useState(false)
 * const [projects, setProjects] = useState([])
 * const [error, setError] = useState(null)
 * 
 * useEffect(() => {
 *   setLoading(true)
 *   nxio('/projects').get((data) => {
 *     setProjects(data)
 *     setLoading(false)
 *   })
 * }, [])
 * 
 * const createProject = (projectData) => {
 *   nxio('/projects').post(projectData, (data) => {
 *     setProjects(prev => [...prev, data])
 *     enqueueSnackbar('Project created', { variant: 'success' })
 *   })
 * }
 * ```
 * 
 * NEW WAY (declarative with hooks):
 * ```typescript
 * const { data: projects, isLoading, error } = useProjects()
 * const createProject = useApiPost('/projects', {
 *   onSuccess: () => notifications.success('Project created')
 * })
 * ```
 * 
 * Benefits of new approach:
 * ✅ Declarative data fetching
 * ✅ Automatic loading states
 * ✅ Built-in error handling
 * ✅ Automatic caching and background updates
 * ✅ Type safety throughout
 * ✅ Consistent error notifications
 * ✅ Request deduplication
 * ✅ Background refetch on stale data
 * ✅ Optimistic updates support
 * ✅ Better DevTools integration
 */