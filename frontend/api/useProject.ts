import { create } from 'zustand'

import useAxios from '~/api/useAxios'

type parsedPathAndInfo = (currentPath: string, environs: MappingTree[]) => ({ mainMenu: boolean, currentMapping: Mapping | null })

const parsePathAndInfo: parsedPathAndInfo = (currentPath, environs) => {
  const p = currentPath.split('/')
  let mainMenu = true
  let currentMapping = null
  if (p.length > 2) {
    mainMenu = false
    const result = environs.flatMap(x => x.children).find(x => x.id == p[2])
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
  refs: [],
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
    return axios<MappingTree[]>('/environs').get((result) => {
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
    const axios = useAxios()
    const a = axios<DataFilename[]>(`/refs`).get(result => {
      set({
        refs: result
      })
    })
    if (id) {
      const b = axios<DataFilename[]>(`/environs/${id}/tables`).get((result) => {
        set({
          dataList: result
        })
      })
      return Promise.all([a, b])
    }
    return a
  }
}))

export default useProject
