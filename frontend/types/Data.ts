interface SettingValue {
  type: string,
  value?: string,
  width?: number
}

interface DataModel {
  id: string,
  instance: string,
  tableName: string,
  description: string,
  layout: string,
  settings: { [key: string]: SettingValue },
  syncMode: string,
  value?: string,
  caption?: string,
  xAxis?: string,
  yAxis?: string,
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
  fixedValue?: string,
  callValue?: string,
}

interface DataInfo {
  gridColumns: GridColumn[],
  gridRows: [{ [key: string]: any }],
  allowLineAdditionAndRemoval: boolean,
}

interface Data {
  model: DataModel,
  info: DataInfo,
  table: Table
}
