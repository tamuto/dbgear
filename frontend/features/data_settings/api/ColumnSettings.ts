
interface FieldItem {
  value: string,
  caption: string,
}

interface ColumnSettings {
  key: string,
  label: string,
  name: string,
  defValue: string | object
  width: number | string,
}
