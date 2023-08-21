interface Binding {
  type: string,
  value: string | null,
  items: {[key: string]: string}[],
}

interface ProjectInfo {
  projectName: string,
  description: string,
  bindings: {[key: string]: Binding},
  rules: {[key: string]: string},
  instances: string[],
}

interface ProjectState {
  mainMenu: boolean,
  projectInfo: ProjectInfo | null,
  currentPath: string | null,
  currentMapping: Mapping | null,
  environs: Mapping[],
  dataList: DataFilename[],
  updateProjectInfo: () => void,
  setCurrentPath: (path: string) => void,
  updateEnvirons: () => void,
  updateDataList: (id: string | undefined) => void,
}
