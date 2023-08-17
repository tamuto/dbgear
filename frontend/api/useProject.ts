import { create } from 'zustand'

import useAxios from './useAxios'

// type parsedPathAndInfo = (currentPath: string | null, projectInfo: object | null) => ({ mainMenu: boolean, dataType: string | null, subMenuTitle: string })

// const parsePathAndInfo: parsedPathAndInfo = (currentPath, projectInfo) => {
//   const p = currentPath?.split('/')
//   let mainMenu = true
//   let dataType = null
//   let subMenuTitle = ''
//   if (p.length > 2) {
//     mainMenu = false
//     if (p[1] === 'templates') {
//       const result = projectInfo?.templates.find(x => x.id == p[2])
//       if (result) {
//         dataType = 'template'
//         subMenuTitle = result.name
//       }
//       // FIXME 例外？見つからなかったら無効なパス
//     }
//     if (p[1] === 'environs') {
//       dataType = 'environ'

//     }
//   }
//   return { mainMenu, dataType, subMenuTitle }
// }

const useProject = create<ProjectState>((set, get) => ({
  mainMenu: false,
  subMenuTitle: '',
  projectInfo: null,
  currentPath: null,
  environs: [],
  environDataList: [],
  updateProjectInfo: () => {
    useAxios<ProjectInfo>('/project').get(result => {
      console.log(result)
      if (get().currentPath) {
        // const parsed = parsePathAndInfo(get().currentPath, result)
        set({
          projectInfo: result,
          // ...parsed
        })
      } else {
        set({
          projectInfo: result
        })
      }
    })
  },
  setCurrentPath: (path) => {
    console.log(path)
    set({
      currentPath: path
    })
    // if (get().projectInfo) {
    //   const parsed = parsePathAndInfo(path, get().projectInfo)
    //   set({
    //     currentPath: path,
    //     ...parsed
    //   })
    // } else {
    //   set({
    //     currentPath: path
    //   })
    // }
  },
  updateEnvirons: () => {
    useAxios<Mapping[]>('/environs').get((result) => {
      console.log(result)
      set({
        environs: result
      })
    })
  },
  updateDataList: async (dataType, id) => {
    // if (dataType === 'template') {
    //   const result = await axios.get(`/templates/${id}`)
    //   console.log(result.data)
    //   set({
    //     templateDataList: result.data
    //   })
    // }
    // if (dataType === 'environ') {

    // }
  }
}))

export default useProject
