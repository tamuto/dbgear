export interface Field {
  column_name: string
  display_name: string | null
  column_type: string
  nullable: boolean
  primary_key: number | null
  default_value: string | null
  foreign_key: string | null
  comment: string | null
  expression: string | null
  stored: boolean | null
  auto_increment: boolean | null
  charset: string | null
  collation: string | null
}

export interface Index {
  index_name: string
  columns: string[]
}

export interface Table {
  instance: string
  table_name: string
  display_name: string | null
  fields: Field[]
  indexes: Index[]
}

export interface Schema {
  name: string
  tables: Record<string, Table>
  views: Record<string, any>
}

export interface TableFormData {
  table_name: string
  display_name: string
  fields: Field[]
  indexes: Index[]
}

export interface FieldFormData {
  column_name: string
  display_name: string
  column_type: string
  nullable: boolean
  primary_key: string
  auto_increment: boolean
  default_value: string
  foreign_key_table: string
  foreign_key_column: string
  comment: string
  expression: string
  stored: string
  charset: string
  collation: string
}