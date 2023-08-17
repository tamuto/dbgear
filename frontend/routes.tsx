import BaseLayout from "~/cmp/BaseLayout"

import TopPage from './features/toppage/components/TopPage'

const routes = [
  {
    element: <BaseLayout />,
    children: [
      {
        index: true,
        element: <TopPage />
      },
      {
        path: "/add",
        element: <div>test</div>
      },
      {
        path: '/environs/:id',
        element: <div>test</div>,
        children: [
          {
            path: '_init',
            element: <div>test</div>
          },
          {
            path: ':instance/:table',
            element: <div>test</div>,
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
      }
    ]
  },
]

export default routes
