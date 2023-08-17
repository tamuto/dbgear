import { create } from 'zustand'

import useAxios from '~/api/useAxios'

type parsedPathAndInfo = (currentPath: string, environs: Mapping[]) => ({ mainMenu: boolean, subMenuTitle: string })

const parsePathAndInfo: parsedPathAndInfo = (currentPath, environs) => {
  const p = currentPath.split('/')
  let mainMenu = true
  let subMenuTitle = ''
  if (p.length > 2) {
    mainMenu = false
    const result = environs.find(x => x.id == p[2])
    if (result) {
      subMenuTitle = result.name
    }
  }
  return { mainMenu, subMenuTitle }
}

const useProject = create<ProjectState>((set, get) => ({
  mainMenu: false,
  subMenuTitle: '',
  projectInfo: null,
  currentPath: null,
  environs: [],
  updateProjectInfo: () => {
    useAxios<ProjectInfo>('/project').get(result => {
      console.log(result)
      set({
        projectInfo: result
      })
    })
  },
  setCurrentPath: (path) => {
    console.log(path)
    set({
      currentPath: path
    })
    if (get().environs.length > 0) {
      const parsed = parsePathAndInfo(path, get().environs)
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
  updateEnvirons: () => {
    useAxios<Mapping[]>('/environs').get((result) => {
      console.log(result)
      if (get().currentPath) {
        const parsed = parsePathAndInfo(get().currentPath!, result)
        set({
          environs: result,
          ...parsed
        })
      } else {
        set({
          environs: result
        })
      }
    })
  }
}))

export default useProject
