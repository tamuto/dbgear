import BaseLayout from '~/cmp/BaseLayout'

import TopPage from './features/top_page/components/TopPage'
import EnvironPage from './features/environ_page/components/EnvironPage'
import EnvironSettings from './features/environ_settings/components/EnvironSettings'
import DataTab from './features/data_tab/components/DataTab'

const routes = [
  {
    element: <BaseLayout />,
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
        element: <div>test</div>
      },
      {
        path: '/environs/:id/:instance/:table',
        element: <DataTab />,
        children: [
          {
            path: '_data',
            element: <div>test</div>
          },
          {
            path: '_props',
            element: <div>test</div>
          }
        ]
      }
    ]
  },
]

export default routes
