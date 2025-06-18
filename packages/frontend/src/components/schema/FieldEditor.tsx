import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Save, X, Key, Link, AlertCircle } from 'lucide-react'
import type { Field, FieldFormData } from '@/types/schema'

interface FieldEditorProps {
  open: boolean
  onClose: () => void
  onSave: (field: Field) => void
  mode: 'create' | 'edit'
  fieldData?: Field
}

export function FieldEditor({ open, onClose, onSave, mode, fieldData }: FieldEditorProps) {
  const form = useForm<FieldFormData>({
    defaultValues: {
      column_name: '',
      display_name: '',
      column_type: 'VARCHAR(255)',
      nullable: true,
      primary_key: '',
      auto_increment: false,
      default_value: '',
      foreign_key_table: '',
      foreign_key_column: '',
      comment: '',
      expression: '',
      stored: '',
      charset: '',
      collation: ''
    }
  })

  // Reset form when dialog opens or fieldData changes
  useEffect(() => {
    if (fieldData && mode === 'edit') {
      const [fkTable, fkColumn] = fieldData.foreign_key?.split('.') || ['', '']
      form.reset({
        column_name: fieldData.column_name,
        display_name: fieldData.display_name || '',
        column_type: fieldData.column_type,
        nullable: fieldData.nullable,
        primary_key: fieldData.primary_key?.toString() || '',
        auto_increment: fieldData.auto_increment || false,
        default_value: fieldData.default_value || '',
        foreign_key_table: fkTable,
        foreign_key_column: fkColumn,
        comment: fieldData.comment || '',
        expression: fieldData.expression || '',
        stored: fieldData.stored?.toString() || '',
        charset: fieldData.charset || '',
        collation: fieldData.collation || ''
      })
    } else if (mode === 'create') {
      form.reset({
        column_name: '',
        display_name: '',
        column_type: 'VARCHAR(255)',
        nullable: true,
        primary_key: '',
        auto_increment: false,
        default_value: '',
        foreign_key_table: '',
        foreign_key_column: '',
        comment: '',
        expression: '',
        stored: '',
        charset: '',
        collation: ''
      })
    }
  }, [fieldData, mode, form, open])

  const handleSave = (data: FieldFormData) => {
    const field: Field = {
      column_name: data.column_name,
      display_name: data.display_name || null,
      column_type: data.column_type,
      nullable: data.nullable,
      primary_key: data.primary_key ? parseInt(data.primary_key) : null,
      auto_increment: data.auto_increment || null,
      default_value: data.default_value || null,
      foreign_key: data.foreign_key_table && data.foreign_key_column
        ? `${data.foreign_key_table}.${data.foreign_key_column}`
        : null,
      comment: data.comment || null,
      expression: data.expression || null,
      stored: data.stored ? data.stored === 'true' : null,
      charset: data.charset || null,
      collation: data.collation || null
    }
    onSave(field)
  }

  const handleClose = () => {
    form.reset()
    onClose()
  }
  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <form onSubmit={form.handleSubmit(handleSave)}>
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <span>{mode === 'create' ? 'Add New Field' : `Edit Field: ${fieldData?.column_name}`}</span>
              {mode === 'edit' && fieldData && (
                <Badge variant="outline" className="text-xs">
                  {fieldData.column_name}
                </Badge>
              )}
            </DialogTitle>
          </DialogHeader>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="column-name">Column Name *</Label>
                  <Input
                    id="column-name"
                    placeholder="e.g., user_id, email, created_at"
                    {...form.register('column_name', { required: 'Column name is required' })}
                  />
                  {form.formState.errors.column_name && (
                    <p className="text-sm text-destructive">{form.formState.errors.column_name.message}</p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="display-name">Display Name</Label>
                  <Input
                    id="display-name"
                    placeholder="Human-readable name (optional)"
                    {...form.register('display_name')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="column-type">Data Type *</Label>
                  <Controller
                    name="column_type"
                    control={form.control}
                    rules={{ required: 'Data type is required' }}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="INT">INT</SelectItem>
                          <SelectItem value="BIGINT">BIGINT</SelectItem>
                          <SelectItem value="VARCHAR(255)">VARCHAR(255)</SelectItem>
                          <SelectItem value="VARCHAR(50)">VARCHAR(50)</SelectItem>
                          <SelectItem value="TEXT">TEXT</SelectItem>
                          <SelectItem value="LONGTEXT">LONGTEXT</SelectItem>
                          <SelectItem value="DATETIME">DATETIME</SelectItem>
                          <SelectItem value="TIMESTAMP">TIMESTAMP</SelectItem>
                          <SelectItem value="DATE">DATE</SelectItem>
                          <SelectItem value="TIME">TIME</SelectItem>
                          <SelectItem value="BOOLEAN">BOOLEAN</SelectItem>
                          <SelectItem value="DECIMAL(10,2)">DECIMAL(10,2)</SelectItem>
                          <SelectItem value="DECIMAL(15,4)">DECIMAL(15,4)</SelectItem>
                          <SelectItem value="FLOAT">FLOAT</SelectItem>
                          <SelectItem value="DOUBLE">DOUBLE</SelectItem>
                          <SelectItem value="JSON">JSON</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {form.formState.errors.column_type && (
                    <p className="text-sm text-destructive">{form.formState.errors.column_type.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="comment">Comment</Label>
                  <Input
                    id="comment"
                    placeholder="Description of this field"
                    {...form.register('comment')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Constraints & Properties */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Constraints & Properties</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="nullable">Nullable</Label>
                  <Controller
                    name="nullable"
                    control={form.control}
                    render={({ field }) => (
                      <Select value={field.value.toString()} onValueChange={(value) => field.onChange(value === 'true')}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="true">Yes (NULL allowed)</SelectItem>
                          <SelectItem value="false">No (NOT NULL)</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="primary-key">Primary Key</Label>
                  <div className="flex items-center space-x-2">
                    <Controller
                      name="primary_key"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger>
                            <SelectValue placeholder="Not a primary key" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Not a primary key</SelectItem>
                            <SelectItem value="1">Primary Key (1st)</SelectItem>
                            <SelectItem value="2">Primary Key (2nd)</SelectItem>
                            <SelectItem value="3">Primary Key (3rd)</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                    <Key className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="auto-increment">Auto Increment</Label>
                  <Controller
                    name="auto_increment"
                    control={form.control}
                    render={({ field }) => (
                      <Select value={field.value.toString()} onValueChange={(value) => field.onChange(value === 'true')}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="false">No</SelectItem>
                          <SelectItem value="true">Yes</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="default-value">Default Value</Label>
                  <Input
                    id="default-value"
                    placeholder="e.g., NULL, '', 0, CURRENT_TIMESTAMP"
                    {...form.register('default_value')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Foreign Key */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Link className="h-5 w-5" />
                  <span>Foreign Key Relationship</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="fk-table">Referenced Table</Label>
                    <Controller
                      name="foreign_key_table"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select table" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">No foreign key</SelectItem>
                            <SelectItem value="users">users</SelectItem>
                            <SelectItem value="departments">departments</SelectItem>
                            <SelectItem value="projects">projects</SelectItem>
                            <SelectItem value="categories">categories</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="fk-column">Referenced Column</Label>
                    <Controller
                      name="foreign_key_column"
                      control={form.control}
                      render={({ field }) => (
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select column" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">No column</SelectItem>
                            <SelectItem value="id">id</SelectItem>
                            <SelectItem value="code">code</SelectItem>
                            <SelectItem value="slug">slug</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>
                </div>

                <div className="flex items-start space-x-2 p-3 bg-muted/50 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5" />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium">Foreign Key Format</p>
                    <p>Will be saved as: <code className="bg-background px-1 rounded">table_name.column_name</code></p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Advanced Properties */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Advanced Properties</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="charset">Character Set</Label>
                  <Controller
                    name="charset"
                    control={form.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Default" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Default</SelectItem>
                          <SelectItem value="utf8mb4">utf8mb4</SelectItem>
                          <SelectItem value="utf8">utf8</SelectItem>
                          <SelectItem value="latin1">latin1</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="collation">Collation</Label>
                  <Controller
                    name="collation"
                    control={form.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Default" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Default</SelectItem>
                          <SelectItem value="utf8mb4_unicode_ci">utf8mb4_unicode_ci</SelectItem>
                          <SelectItem value="utf8mb4_general_ci">utf8mb4_general_ci</SelectItem>
                          <SelectItem value="utf8_general_ci">utf8_general_ci</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="stored">Stored</Label>
                  <Controller
                    name="stored"
                    control={form.control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Default" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Default</SelectItem>
                          <SelectItem value="true">Yes</SelectItem>
                          <SelectItem value="false">No</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Generated Column */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Generated Column</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="expression">Expression</Label>
                  <Input
                    id="expression"
                    placeholder="e.g., CONCAT(first_name, ' ', last_name)"
                    {...form.register('expression')}
                  />
                </div>
                <div className="flex items-start space-x-2 p-3 bg-muted/50 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5" />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium">Generated Columns</p>
                    <p>Values are automatically calculated based on the expression. Leave empty for regular columns.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Separator />

          <DialogFooter className="flex justify-between">
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <AlertCircle className="h-4 w-4" />
              <span>Fields marked with * are required</span>
            </div>
            <div className="flex space-x-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button type="submit">
                <Save className="h-4 w-4 mr-2" />
                Save Field
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}