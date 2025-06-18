import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">DBGear Table Schema Editor</h1>
        <p className="text-muted-foreground">
          Test the table schema editor with the sample links below
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Test Schema Editor</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3">
            <Link to="/schemas/main/tables/users/edit">
              <Button variant="outline" className="w-full justify-start">
                Edit Users Table (main schema)
              </Button>
            </Link>
            
            <Link to="/schemas/main/tables/products/edit">
              <Button variant="outline" className="w-full justify-start">
                Edit Products Table (main schema)
              </Button>
            </Link>
            
            <Link to="/schemas/inventory/tables/items/edit">
              <Button variant="outline" className="w-full justify-start">
                Edit Items Table (inventory schema)
              </Button>
            </Link>
            
            <Link to="/schemas/test/tables/new_table/edit">
              <Button variant="default" className="w-full justify-start">
                Create New Table (test schema)
              </Button>
            </Link>
          </div>
          
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              <strong>Note:</strong> These are test links for development. 
              Remove this page in production and implement proper navigation.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
