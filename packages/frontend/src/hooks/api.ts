import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import type { Table, Schema, Field, Index } from '@/types/schema'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Query Keys
export const queryKeys = {
  schemas: () => ['schemas'],
  schema: (id: string) => ['schemas', id],
  tables: (schemaId: string) => ['schemas', schemaId, 'tables'],
  table: (schemaId: string, tableId: string) => ['schemas', schemaId, 'tables', tableId],
  fields: (schemaId: string, tableId: string) => ['schemas', schemaId, 'tables', tableId, 'fields'],
  indexes: (schemaId: string, tableId: string) => ['schemas', schemaId, 'tables', tableId, 'indexes'],
}

// Schema Hooks
export function useSchemas() {
  return useQuery({
    queryKey: queryKeys.schemas(),
    queryFn: async () => {
      const response = await api.get('/schemas')
      return response.data.data as string[]
    },
  })
}

export function useSchema(schemaId: string) {
  return useQuery({
    queryKey: queryKeys.schema(schemaId),
    queryFn: async () => {
      const response = await api.get(`/schemas/${schemaId}`)
      return response.data.data as Schema
    },
    enabled: !!schemaId,
  })
}

// Table Hooks
export function useTables(schemaId: string) {
  return useQuery({
    queryKey: queryKeys.tables(schemaId),
    queryFn: async () => {
      const response = await api.get(`/schemas/${schemaId}/tables`)
      return response.data.data as string[]
    },
    enabled: !!schemaId,
  })
}

export function useTable(schemaId: string, tableId: string) {
  return useQuery({
    queryKey: queryKeys.table(schemaId, tableId),
    queryFn: async () => {
      const response = await api.get(`/schemas/${schemaId}/tables/${tableId}`)
      return response.data.data as Table
    },
    enabled: !!schemaId && !!tableId,
  })
}

export function useCreateTable(schemaId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tableData: { instance: string; table_name: string; display_name?: string }) => {
      const response = await api.post(`/schemas/${schemaId}/tables`, tableData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tables(schemaId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.schema(schemaId) })
    },
  })
}

export function useUpdateTable(schemaId: string, tableId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tableData: { instance: string; table_name: string; display_name?: string }) => {
      const response = await api.put(`/schemas/${schemaId}/tables/${tableId}`, tableData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.tables(schemaId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.schema(schemaId) })
    },
  })
}

export function useDeleteTable(schemaId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tableId: string) => {
      const response = await api.delete(`/schemas/${schemaId}/tables/${tableId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tables(schemaId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.schema(schemaId) })
    },
  })
}

// Field Hooks
export function useFields(schemaId: string, tableId: string) {
  return useQuery({
    queryKey: queryKeys.fields(schemaId, tableId),
    queryFn: async () => {
      const response = await api.get(`/schemas/${schemaId}/tables/${tableId}/fields`)
      return response.data.data as string[]
    },
    enabled: !!schemaId && !!tableId,
  })
}

export function useCreateField(schemaId: string, tableId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (fieldData: Omit<Field, 'expression' | 'stored' | 'auto_increment' | 'charset' | 'collation'>) => {
      const response = await api.post(`/schemas/${schemaId}/tables/${tableId}/fields`, fieldData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.fields(schemaId, tableId) })
    },
  })
}

export function useUpdateField(schemaId: string, tableId: string, fieldName: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (fieldData: Partial<Field>) => {
      const response = await api.put(`/schemas/${schemaId}/tables/${tableId}/fields/${fieldName}`, fieldData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.fields(schemaId, tableId) })
    },
  })
}

export function useDeleteField(schemaId: string, tableId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (fieldName: string) => {
      const response = await api.delete(`/schemas/${schemaId}/tables/${tableId}/fields/${fieldName}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.fields(schemaId, tableId) })
    },
  })
}

// Index Hooks
export function useIndexes(schemaId: string, tableId: string) {
  return useQuery({
    queryKey: queryKeys.indexes(schemaId, tableId),
    queryFn: async () => {
      const response = await api.get(`/schemas/${schemaId}/tables/${tableId}/indexes`)
      return response.data.data as Index[]
    },
    enabled: !!schemaId && !!tableId,
  })
}

export function useCreateIndex(schemaId: string, tableId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (indexData: { index_name?: string; columns: string[] }) => {
      const response = await api.post(`/schemas/${schemaId}/tables/${tableId}/indexes`, indexData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.indexes(schemaId, tableId) })
    },
  })
}

export function useDeleteIndex(schemaId: string, tableId: string) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (indexName: string) => {
      const response = await api.delete(`/schemas/${schemaId}/tables/${tableId}/indexes/${indexName}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.table(schemaId, tableId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.indexes(schemaId, tableId) })
    },
  })
}

// Validation Hooks
export function useValidateTable() {
  return useMutation({
    mutationFn: async (tableData: Table) => {
      const response = await api.post('/schemas/validate/table', { table: tableData })
      return response.data
    },
  })
}

export function useValidateField() {
  return useMutation({
    mutationFn: async (fieldData: Field) => {
      const response = await api.post('/schemas/validate/field', { field: fieldData })
      return response.data
    },
  })
}

export function useValidateSchema(schemaId: string) {
  return useMutation({
    mutationFn: async () => {
      const response = await api.post(`/schemas/validate/schema?schema_name=${schemaId}`)
      return response.data
    },
  })
}