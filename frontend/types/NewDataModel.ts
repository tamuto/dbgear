interface NewDataModel {
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
