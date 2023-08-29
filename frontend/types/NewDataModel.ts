interface NewDataModel {
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
