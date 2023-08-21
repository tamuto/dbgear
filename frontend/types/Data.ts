interface DataModel {
  id: string,
  instance: string,
  tableName: string,
  description: string,
  layout: string,
  settings: { [key: string]: object },
  sync_mode: string,
  value?: string,
  caption?: string,
  x_axis?: string,
  y_axis?: string,
  cells?: string[],
}

interface GridColumn {
  field: string,
  type: string,
  headerName: string,
  width: number,
  editable: boolean,
  hide: boolean,
  items: object[],
  fixed_value?: string,
  call_value?: string,
  reference?: string,
}

interface DataInfo {
  grid_columns: GridColumn[],
  grid_rows: [{ [key: string]: any }],
  allow_line_addition_and_removal: boolean,
}

interface Data {
  model: DataModel,
  info: DataInfo,
  table: Table
}
