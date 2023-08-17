interface Binding {
  type: string,
  value: string | null,
  items: {[key: string]: string}[],
}

interface ProjectInfo {
  projectName: string,
  bindings: {[key: string]: Binding},
  rules: {[key: string]: string}
}

interface ProjectState {
  mainMenu: boolean,
  subMenuTitle: string,
  projectInfo: ProjectInfo | null,
  currentPath: string | null,
  environs: Mapping[],
  updateProjectInfo: () => void,
  setCurrentPath: (path: string) => void,
  updateEnvirons: () => void,
}
