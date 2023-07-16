import { create } from 'zustand'
import axios from 'axios'

const parsePathAndInfo = (currentPath, projectInfo) => {
  const p = currentPath.split('/')
  let mainMenu = true
  let dataType = null
  let subMenuTitle = ''
  let subBasePath = ''
  if (p.length > 2) {
    mainMenu = false
    subBasePath = [p[0], p[1], p[2]].join('/')
    if (p[1] === 'templates') {
      const result = projectInfo.templates.find(x => x.id == p[2])
      if (result) {
        dataType = 'template'
        subMenuTitle = result.name
      }
      // FIXME 例外？見つからなかったら無効なパス
    }
    if (p[1] === 'environs') {
      dataType = 'environ'

    }
  }
  return { mainMenu, dataType, subMenuTitle, subBasePath }
}

const useProject = create((set, get) => ({
  mainMenu: true,
  dataType: null,
  subMenuTitle: '',
  subBasePath: null,
  projectInfo: null,
  currentPath: null,
  templateDataList: [],
  environDataList: [],
  updateProjectInfo: async () => {
    const result = await axios.get('/project')
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
  },
  updateDataList: async (dataType, id) => {
    if (dataType === 'template') {
      const result = await axios.get(`/templates/${id}`)
      console.log(result.data)
      set({
        templateDataList: result.data
      })
    }
    if (dataType === 'environ') {

    }
  }
}))

export default useProject
