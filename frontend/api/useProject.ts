import { create } from 'zustand'

import useAxios from '~/api/useAxios'

type parsedPathAndInfo = (currentPath: string, environs: Mapping[]) => ({ mainMenu: boolean, currentMapping: Mapping | null })

const parsePathAndInfo: parsedPathAndInfo = (currentPath, environs) => {
  const p = currentPath.split('/')
  let mainMenu = true
  let currentMapping = null
  if (p.length > 2) {
    mainMenu = false
    const result = environs.find(x => x.id == p[2])
    if (result) {
      currentMapping = result
    }
  }
  return { mainMenu, currentMapping }
}

const useProject = create<ProjectState>((set, get) => ({
  mainMenu: true,
  projectInfo: null,
  currentPath: null,
  currentMapping: null,
  environs: [],
  dataList: [],
  updateProjectInfo: async () => {
    const axios = useAxios()
    return axios<ProjectInfo>('/project').get(result => {
      console.log(result)
      set({
        projectInfo: result
      })
    })
  },
  setCurrentPath: (path) => {
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
  updateEnvirons: async () => {
    const axios = useAxios()
    return axios<Mapping[]>('/environs').get((result) => {
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
  },
  updateDataList: async (id) => {
    if (id) {
      const axios = useAxios()
      return axios<DataFilename[]>(`/environs/${id}/tables`).get((result) => {
        set({
          dataList: result
        })
      })
    }
  }
}))

export default useProject
