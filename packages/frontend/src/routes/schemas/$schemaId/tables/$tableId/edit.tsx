import { createFileRoute } from '@tanstack/react-router'
import { TableSchemaEditor } from '@/components/schema/TableSchemaEditor'

export const Route = createFileRoute('/schemas/$schemaId/tables/$tableId/edit')({
  component: TableSchemaEditorPage,
})

function TableSchemaEditorPage() {
  const { schemaId, tableId } = Route.useParams()

  return <TableSchemaEditor schemaId={schemaId} tableId={tableId} />
}