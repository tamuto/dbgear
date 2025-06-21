
interface Field {
  columnName: string,
  displayName: string,
  columnType: string,
  nullable: boolean,
  primaryKey?: number,
  defaultValue?: string,
  foreignKey?: string,
  comment?: string,
}

interface Index {
  indexName: string,
  columns: string[],
}

interface Table {
  tableName: string,
  displayName: string,
  fields: Field[],
  indexes: Index[],
}
