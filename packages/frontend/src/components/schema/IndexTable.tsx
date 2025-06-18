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
import { Trash2, Database } from 'lucide-react'
import type { Index } from '@/types/schema'

interface IndexTableProps {
  indexes: Index[]
  onDeleteIndex: (index: number) => void
}

export function IndexTable({ indexes, onDeleteIndex }: IndexTableProps) {
  if (indexes.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No indexes defined yet.</p>
        <p className="text-sm">Click "Add Index" to create the first index.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px]">Index Name</TableHead>
            <TableHead>Columns</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {indexes.map((index, indexKey) => (
            <TableRow key={`${index.index_name}-${indexKey}`}>
              <TableCell>
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  <div className="font-medium">{index.index_name}</div>
                  {index.index_name === 'PRIMARY' && (
                    <Badge variant="default" className="text-xs">
                      Primary
                    </Badge>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center space-x-1 flex-wrap gap-1">
                  {index.columns.map((column, columnIndex) => (
                    <Badge key={`${column}-${columnIndex}`} variant="secondary" className="text-xs">
                      {column}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                  disabled={index.index_name === 'PRIMARY'}
                  onClick={() => onDeleteIndex(indexKey)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}