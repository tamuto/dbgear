interface Binding {
  type: string,
  value: string,
  items: {[key: string]: string}[],
}

interface ProjectInfo {
  projectName: string,
  description: string,
  bindings: {[key: string]: Binding},
  rules: {[key: string]: string},
  instances: string[],
  apiKey: string | null
}

interface MappingTree {
  name: string,
  children: Mapping[],
}

interface ProjectState {
  mainMenu: boolean,
  projectInfo: ProjectInfo | null,
  currentPath: string | null,
  currentMapping: Mapping | null,
  environs: MappingTree[],
  dataList: DataFilename[],
  refs: DataFilename[],
  updateProjectInfo: () => void,
  setCurrentPath: (path: string) => void,
  updateEnvirons: () => void,
  updateDataList: (id: string | undefined) => void,
}
