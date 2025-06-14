import { create } from 'zustand'

import nxio from '~/api/nxio'

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
    return nxio<ProjectInfo>('/project').get(result => {
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
    return nxio<MappingTree[]>('/environs').get((result) => {
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
    const a = nxio<DataFilename[]>(`/refs`).get(result => {
      set({
        refs: result
      })
    })
    if (id) {
      const b = nxio<DataFilename[]>(`/environs/${id}/tables`).get((result) => {
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
