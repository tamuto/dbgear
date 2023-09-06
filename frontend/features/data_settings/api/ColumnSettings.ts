
interface FieldItem {
  value: string,
  caption: string,
}

interface ColumnSettings {
  key: string,
  label: string,
  name: string,
  defValue: string
  width: string,
}

type FormValues = {
  table: string
  description: string
  syncMode: string
  value: string
  caption: string
  layout: string
  xAxis: string
  yAxis: string
  cells: string[]
  fields: { [key: string]: string }
}
