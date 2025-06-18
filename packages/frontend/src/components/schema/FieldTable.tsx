import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Edit, Trash2, Key, Link } from 'lucide-react'
import type { Field } from '@/types/schema'

interface FieldTableProps {
  fields: Field[]
  onEditField: (index: number) => void
  onDeleteField: (index: number) => void
}

export function FieldTable({ fields, onEditField, onDeleteField }: FieldTableProps) {
  if (fields.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No fields defined yet.</p>
        <p className="text-sm">Click "Add Field" to create the first field.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[140px]">Column Name</TableHead>
            <TableHead className="w-[140px]">Display Name</TableHead>
            <TableHead className="w-[130px]">Type</TableHead>
            <TableHead className="w-[80px]">Nullable</TableHead>
            <TableHead className="w-[100px]">Constraints</TableHead>
            <TableHead className="w-[120px]">Default</TableHead>
            <TableHead className="w-[140px]">Foreign Key</TableHead>
            <TableHead className="w-[150px]">Comment</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field, index) => (
            <TableRow key={`${field.column_name}-${index}`}>
              <TableCell>
                <div className="font-medium">{field.column_name}</div>
              </TableCell>
              <TableCell>
                <div className="text-muted-foreground">
                  {field.display_name || '-'}
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="secondary" className="text-xs">
                  {field.column_type}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={field.nullable ? "outline" : "default"} className="text-xs">
                  {field.nullable ? 'Yes' : 'No'}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center space-x-1">
                  {field.primary_key && (
                    <Badge variant="default" className="text-xs">
                      <Key className="h-3 w-3 mr-1" />
                      PK
                    </Badge>
                  )}
                  {field.auto_increment && (
                    <Badge variant="secondary" className="text-xs">
                      AI
                    </Badge>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="text-sm text-muted-foreground max-w-[120px] truncate">
                  {field.default_value || '-'}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center space-x-2">
                  {field.foreign_key ? (
                    <Badge variant="outline" className="text-xs">
                      <Link className="h-3 w-3 mr-1" />
                      {field.foreign_key}
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground text-sm">-</span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="text-sm text-muted-foreground max-w-[150px] truncate">
                  {field.comment || '-'}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center space-x-1">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="h-6 w-6 p-0"
                    onClick={() => onEditField(index)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                    onClick={() => onDeleteField(index)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}