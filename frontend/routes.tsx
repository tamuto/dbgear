import useProject from '~/api/useProject'

import BaseLayout from '~/cmp/BaseLayout'

import TopPage from './features/top_page/components/TopPage'
import EnvironPage from './features/environ_page/components/EnvironPage'
import EnvironSettings from './features/environ_settings/components/EnvironSettings'
import DataTab from './features/data_tab/components/DataTab'
import DataEditor from './features/data_editor/components/DataEditor'
import DataSettings from './features/data_settings/components/DataSettings'
import DataSettingsWrapper from './features/data_settings/components/DataSettingsWrapper'

const routes = [
  {
    element: <BaseLayout />,
    loader: async (opts: any) => {
      await useProject.getState().updateProjectInfo()
      await useProject.getState().updateEnvirons()
      if (opts.params.id) {
        // 既にIDがある場合は、データリストを更新する
        await useProject.getState().updateDataList(opts.params.id)
      }
      return null
    },
    children: [
      {
        index: true,
        element: <TopPage />
      },
      {
        path: '/add',
        element: <EnvironSettings />
      },
      {
        path: '/environs/:id',
        element: <EnvironPage />
      },
      {
        path: '/environs/:id/_init',
        element: <DataSettings data={null} reload={null} />
      },
      {
        path: '/environs/:id/:instance/:table',
        element: <DataTab />,
        children: [
          {
            path: '_data',
            element: <DataEditor />
          },
          {
            path: '_props',
            element: <DataSettingsWrapper />
          }
        ]
      }
    ]
  },
]

export default routes
