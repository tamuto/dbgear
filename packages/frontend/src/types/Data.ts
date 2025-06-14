interface SettingValue {
  type: string,
  id?: string,
  instance?: string,
  table?: string,
  width?: number
}

interface ListItem {
  value: string,
  caption: string,
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
  segment: string,
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
  items: ListItem[],
  fixedValue?: string,
  callValue?: string,
}

interface DataInfo {
  segments: ListItem[],
  current: string,
  gridColumns: GridColumn[],
  gridRows: [{ [key: string]: object }],
  allowLineAdditionAndRemoval: boolean,
}

interface Data {
  model: DataModel,
  info: DataInfo,
  table: Table
}
