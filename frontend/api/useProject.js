import { create } from 'zustand'
import axios from 'axios'

const parsePathAndInfo = (currentPath, projectInfo) => {
  const p = currentPath.split('/')
  const routePath = [projectInfo.projectName]
  let mainMenu = true
  let subMenuTitle = ''
  let subBasePath = ''
  if (p.length > 2) {
    mainMenu = false
    subBasePath = [p[0], p[1], p[2]].join('/')
    if (p[1] === 'templates') {
      const result = projectInfo.templates.find(x => x.id == p[2])
      if (result) {
        subMenuTitle = result.name
        routePath.push(result.name)
      }
      // FIXME 例外？見つからなかったら無効なパス
    }
    if (p[1] === 'environs') {

    }
  }
  return { mainMenu, subMenuTitle, subBasePath, routePath }
}

const useProject = create((set, get) => ({
  routePath: [],
  mainMenu: true,
  subMenuTitle: '',
  subBasePath: null,
  projectInfo: null,
  currentPath: null,
  updateProjectInfo: async () => {
    const result = await axios.get('/project')
    console.log(result.data)
    if (get().currentPath) {
      const parsed = parsePathAndInfo(get().currentPath, result.data)
      set({
        projectInfo: result.data,
        ...parsed
      })
    } else {
      set({
        projectInfo: result.data
      })
    }
  },
  setCurrentPath: (path) => {
    if (get().projectInfo) {
      const parsed = parsePathAndInfo(path, get().projectInfo)
      set({
        currentPath: path,
        ...parsed
      })
    } else {
      set({
        currentPath: path
      })
    }
  }
}))

export default useProject
