import BaseLayout from "./components/BaseLayout"

const routes = [
  {
    element: <BaseLayout />,
    children: [
      {
        index: true,
        element: <div>root</div>
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
