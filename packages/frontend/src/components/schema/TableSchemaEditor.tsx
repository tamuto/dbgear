import { useEffect, useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { useNavigate } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { FieldTable } from './FieldTable'
import { IndexTable } from './IndexTable'
import { FieldEditor } from './FieldEditor'
import { ArrowLeft, Save, X, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { useTable, useUpdateTable } from '@/hooks/api'
import type { TableFormData, Field, Index } from '@/types/schema'

interface TableSchemaEditorProps {
  schemaId: string
  tableId: string
}

export function TableSchemaEditor({ schemaId, tableId }: TableSchemaEditorProps) {
  const navigate = useNavigate()
  const [isFieldEditorOpen, setIsFieldEditorOpen] = useState(false)
  const [editingFieldIndex, setEditingFieldIndex] = useState<number | null>(null)

  // API hooks
  const { data: tableData, isLoading, error } = useTable(schemaId, tableId)
  const updateTableMutation = useUpdateTable(schemaId, tableId)

  const form = useForm<TableFormData>({
    defaultValues: {
      table_name: tableId,
      display_name: '',
      fields: [],
      indexes: []
    }
  })

  const { fields, append: appendField, remove: removeField, update: updateField } = useFieldArray({
    control: form.control,
    name: 'fields'
  })

  const { fields: indexes, append: appendIndex, remove: removeIndex } = useFieldArray({
    control: form.control,
    name: 'indexes'
  })

  // Load table data when it's available
  useEffect(() => {
    if (tableData) {
      const formData: TableFormData = {
        table_name: tableData.table_name,
        display_name: tableData.display_name || '',
        fields: tableData.fields || [],
        indexes: tableData.indexes || []
      }
      form.reset(formData)
    }
  }, [tableData, form])

  // Handle API errors
  useEffect(() => {
    if (error) {
      toast.error('Failed to load table data')
      console.error('Error loading table:', error)
    }
  }, [error])

  const handleSave = async (data: TableFormData) => {
    try {
      await updateTableMutation.mutateAsync({
        instance: schemaId,
        table_name: data.table_name,
        display_name: data.display_name || undefined
      })
      
      toast.success('Table saved successfully')
      navigate({ to: `/schemas/${schemaId}` })
    } catch (error) {
      toast.error('Failed to save table')
      console.error('Error saving table:', error)
    }
  }

  const handleCancel = () => {
    navigate({ to: `/schemas/${schemaId}` })
  }

  const handleAddField = () => {
    setEditingFieldIndex(null)
    setIsFieldEditorOpen(true)
  }

  const handleEditField = (index: number) => {
    setEditingFieldIndex(index)
    setIsFieldEditorOpen(true)
  }

  const handleDeleteField = (index: number) => {
    removeField(index)
    toast.success('Field deleted')
  }

  const handleFieldSave = (fieldData: Field) => {
    if (editingFieldIndex !== null) {
      updateField(editingFieldIndex, fieldData)
      toast.success('Field updated')
    } else {
      appendField(fieldData)
      toast.success('Field added')
    }
    setIsFieldEditorOpen(false)
    setEditingFieldIndex(null)
  }

  const handleAddIndex = () => {
    const newIndex: Index = {
      index_name: `idx_${Date.now()}`,
      columns: []
    }
    appendIndex(newIndex)
    toast.success('Index added')
  }

  const handleDeleteIndex = (index: number) => {
    removeIndex(index)
    toast.success('Index deleted')
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center text-destructive">
          Failed to load table data. Please try again.
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={form.handleSubmit(handleSave)}>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button type="button" variant="ghost" size="sm" onClick={handleCancel}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Schema
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Edit Table</h1>
              <p className="text-muted-foreground">
                Schema: <Badge variant="secondary">{schemaId}</Badge>
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button type="button" variant="outline" onClick={handleCancel}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button type="submit" disabled={updateTableMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {updateTableMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>

        {/* Table Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Table Information</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="table-name">Table Name *</Label>
              <Input
                id="table-name"
                placeholder="Enter table name"
                {...form.register('table_name', { required: 'Table name is required' })}
              />
              {form.formState.errors.table_name && (
                <p className="text-sm text-destructive">{form.formState.errors.table_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="display-name">Display Name</Label>
              <Input
                id="display-name"
                placeholder="Enter display name (optional)"
                {...form.register('display_name')}
              />
            </div>
          </CardContent>
        </Card>

        {/* Fields Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Fields</CardTitle>
              <Button type="button" size="sm" onClick={handleAddField}>
                <Plus className="h-4 w-4 mr-2" />
                Add Field
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <FieldTable
              fields={fields}
              onEditField={handleEditField}
              onDeleteField={handleDeleteField}
            />
          </CardContent>
        </Card>

        {/* Indexes Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Indexes</CardTitle>
              <Button type="button" size="sm" variant="outline" onClick={handleAddIndex}>
                <Plus className="h-4 w-4 mr-2" />
                Add Index
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <IndexTable
              indexes={indexes}
              onDeleteIndex={handleDeleteIndex}
            />
          </CardContent>
        </Card>

        <Separator />

        {/* Footer Actions */}
        <div className="flex justify-end space-x-2">
          <Button type="button" variant="outline" onClick={handleCancel}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          <Button type="submit" disabled={updateTableMutation.isPending}>
            <Save className="h-4 w-4 mr-2" />
            {updateTableMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Field Editor Dialog */}
      <FieldEditor
        open={isFieldEditorOpen}
        onClose={() => setIsFieldEditorOpen(false)}
        onSave={handleFieldSave}
        mode={editingFieldIndex !== null ? 'edit' : 'create'}
        fieldData={editingFieldIndex !== null ? fields[editingFieldIndex] : undefined}
      />
    </form>
  )
}