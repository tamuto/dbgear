# DBGear Frontend

このプロジェクトはDBGearの新しいフロントエンドパッケージです。

> ⚡️ **Rspack** + **React 19** + **TailwindCSS** + **shadcn/ui** + **TanStack Query** + **TanStack Router** を使用した現代的なWebアプリケーション

## 🚀 クイックスタート

### 開発環境の起動

```bash
# 依存関係のインストール
pnpm install

# 開発サーバーの起動（http://localhost:8080）
pnpm dev
```

### プロダクションビルド

```bash
# 最適化されたビルドを作成（../dbgear-web/dbgear_web/static/ に出力）
pnpm build
```

## 🎨 shadcn/uiコンポーネントの追加

プロジェクトにはshadcn/uiが事前設定されています。以下のコマンドで美しいコンポーネントを追加できます：

```bash
# 基本的なコンポーネントを追加
pnpx shadcn@latest add button
pnpx shadcn@latest add card
pnpx shadcn@latest add input
pnpx shadcn@latest add form

# 利用可能なコンポーネント一覧を確認
pnpx shadcn@latest add
```

### 使用例

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function ExampleComponent() {
  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Welcome!</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>Get Started</Button>
      </CardContent>
    </Card>
  )
}
```

## 🔌 API管理システム

このプロジェクトは旧`nxio.ts`に代わる新しいAPI管理システムを使用しています。

### 基本的な使用方法

#### 1. アプリのセットアップ

まず、`main.tsx`でProvidersを設定してください：

```tsx
import { Providers } from '@/lib/providers'
import { Toaster } from '@/components/ui/sonner'

// アプリ全体をProvidersでラップ
ReactDOM.render(
  <Providers>
    <App />
  </Providers>,
  document.getElementById('root')
)
```

#### 2. データフェッチング（読み取り）

宣言的なAPIフックを使用：

```tsx
import { useProjects, useProject } from '@/hooks/use-api'

function ProjectList() {
  // 自動的にローディング状態、エラー状態、キャッシュを管理
  const { data: projects, isLoading, error, refetch } = useProjects()

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      {projects?.map(project => (
        <div key={project.id}>{project.name}</div>
      ))}
    </div>
  )
}
```

#### 3. データ変更（作成・更新・削除）

ミューテーションフックを使用：

```tsx
import { useApiPost, useInvalidateQueries } from '@/hooks/use-api'
import { notifications } from '@/hooks/use-toast-notifications'

function CreateProject() {
  const { invalidateProjects } = useInvalidateQueries()
  
  const createProject = useApiPost('/projects', {
    onSuccess: (data) => {
      notifications.success(`Project "${data.name}" created!`)
      invalidateProjects() // リストを更新
    },
    onError: (error) => {
      notifications.error(error.message)
    }
  })

  const handleSubmit = (formData) => {
    createProject.mutate(formData)
  }

  return (
    <button 
      onClick={() => handleSubmit({ name: 'New Project' })}
      disabled={createProject.isLoading}
    >
      {createProject.isLoading ? 'Creating...' : 'Create Project'}
    </button>
  )
}
```

#### 4. 通知システム

Sonnerベースの通知システム：

```tsx
import { notifications } from '@/hooks/use-toast-notifications'

// 成功通知
notifications.success('Operation completed successfully')

// エラー通知
notifications.error('Something went wrong')

// 警告通知
notifications.warning('Please check your input')

// 情報通知
notifications.info('New feature available')

// プロミスベース通知（非同期処理用）
notifications.promise(
  apiCall(),
  {
    loading: 'Processing...',
    success: 'Done!',
    error: 'Failed!'
  }
)
```

#### 5. カスタムAPIエンドポイント

独自のAPIエンドポイント用：

```tsx
import { useApiQuery, useApiMutation } from '@/hooks/use-api'

// カスタムクエリ
function useCustomData(id: string) {
  return useApiQuery(
    ['custom', id],
    `/custom-endpoint/${id}`,
    undefined,
    {
      enabled: !!id,
      staleTime: 10 * 60 * 1000, // 10分間キャッシュ
    }
  )
}

// カスタムミューテーション
function useCustomAction() {
  return useApiMutation(
    (data) => api.post('/custom-action', data),
    {
      onSuccess: () => {
        notifications.success('Action completed')
      }
    }
  )
}
```

### 旧システムとの比較

| 項目 | 旧 nxio.ts | 新システム |
|------|------------|------------|
| **データフェッチ** | `nxio('/api').get(callback)` | `useProjects()` |
| **エラーハンドリング** | 手動 | 自動 + カスタマイズ可能 |
| **ローディング状態** | 手動管理 | 自動 |
| **キャッシュ** | なし | 自動キャッシュ + 無効化 |
| **型安全性** | 弱い | 完全な型安全性 |
| **リトライ** | なし | 自動リトライ |

## 🛠️ 開発のヒント

### TailwindCSSクラスの活用

```tsx
// レスポンシブデザイン
<div className="w-full md:w-1/2 lg:w-1/3">
  <h1 className="text-2xl md:text-4xl font-bold">
    Responsive Heading
  </h1>
</div>

// ダークモード対応
<div className="bg-white dark:bg-gray-800 text-black dark:text-white">
  Dark mode ready!
</div>
```

### ルーティングシステム

TanStack Routerを使用した型安全なルーティング：

```tsx
// src/routes/projects/$projectId.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/projects/$projectId')({
  component: ProjectDetail,
})

function ProjectDetail() {
  const { projectId } = Route.useParams()
  const { data: project } = useProject(projectId)
  
  return <div>Project: {project?.name}</div>
}
```

## 📁 プロジェクト構造

```
src/
├── components/          # Shadcn/UI コンポーネント
│   └── ui/             # 自動生成UIコンポーネント
├── hooks/              # カスタムReactフック
│   ├── use-api.ts      # API管理フック
│   └── use-toast-notifications.ts  # 通知システム
├── lib/                # ユーティリティとプロバイダー
│   ├── api-client.ts   # Axios設定
│   ├── error-handler.ts # エラーハンドリング
│   ├── providers.tsx   # アプリプロバイダー
│   └── utils.ts        # 共通ユーティリティ
├── routes/             # TanStack Router ルート定義
├── types/              # TypeScript型定義
│   └── api.ts          # API関連の型
├── globals.css         # グローバルスタイル
└── main.tsx           # アプリエントリーポイント
```

## 📚 詳細情報

- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [TanStack Router](https://tanstack.com/router/latest)
- [Rspack Documentation](https://rspack.dev/)
- [Sonner Notifications](https://sonner.emilkowal.ski/)

---

**Happy coding! 🎉**
