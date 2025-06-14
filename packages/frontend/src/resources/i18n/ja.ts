
const promptFillData = `あなたはシステム開発者です。
ユーザからの指示の元、既存データのうち指定されたカラムのデータ補完を行うタスクを実行しています。
作成するべきテーブルには以下のカラムを持っています。(括弧の中は論理カラム名。)
このうち、一つのカラム名が指示されますので、その該当カラムの補完データのみを生成してください。
{replace}
また、データの必要件数は{nn}件です。
なお、カラム名が具体的に指定されなかった場合には、聞き返してください。
`

export const ja = {
  caption: {
    addData: 'データ追加',
    addEnviron: '環境追加',
    append: '追加',
    baseEnviron: '継承元環境',
    cancel: 'キャンセル',
    captionField: 'キャプション',
    cells: 'セルカラム',
    columnSettings: 'カラム設定',
    create: '作成',
    close: '閉じる',
    dataName: 'データ名',
    dataSegment: 'データ分割管理',
    deploymentable: 'デプロイ可能',
    deployments: 'デプロイ一覧',
    description: '説明',
    download: 'ダウンロード',
    dropCreate: 'ドロップ＆作成',
    editor: 'データ編集',
    environGroup: '環境グループ',
    environID: '環境ID(物理DB名)',
    environName: '環境名',
    environs: '環境一覧',
    environSettings: '環境設定',
    fillData: 'データ補完',
    fillDataColumn: '補完対象',
    fillDataValue: '補完する値',
    forListDisplay: 'リスト表示用',
    host: '接続先',
    import: 'インポート',
    importSQL: 'SQLインポート',
    inputForm: '入力フォーム',
    instances: 'インスタンス',
    layout: 'レイアウト',
    managedData: '管理データ',
    matrix: 'マトリクス',
    message: 'メッセージ',
    nothing: 'なし',
    properties: 'プロパティ',
    remarks: '備考',
    remove: '削除',
    required: '(必須)',
    save: '保存',
    segment: 'セグメント',
    singleEntry: '単一入力',
    sql: '実行するSQL',
    syncMode: '同期モード',
    table: 'テーブル',
    targetTable: '対象テーブル',
    update: '更新',
    updateDiff: '差分更新',
    upload: 'アップロード',
    valueField: '値',
    width: '幅',
    xAxis: 'X軸カラム',
    yAxis: 'Y軸カラム',
  },
  message: {
    dataLines: '現在{nn}件です。{mm}件のデータが必要です。',
    fillDataDesc: 'データを補完します。対象カラムと値を指定してください。',
    fillDataSuccess: 'データを生成しました。左の欄をご確認ください。',
    importSQLDesc: 'SQLを実行してデータをインポートします。',
    importSuccess: 'インポートしました。',
    initFillDataMessage: 'こんにちは。<br>どのようなデータを生成しますか？',
    inputFormDesc: '入力フォームのレイアウトを設定します。',
    listDisplayDesc: '一覧表示時に使う値とキャプションのフィールドを設定します。',
    notApiKey: 'APIキーが設定されていません。',
    required: 'この項目は必須です。',
    saveSuccess: '保存しました。',
  },
  prompt: {
    fillData: {
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: promptFillData
        }
      ],
      functions: [
        {
          name: 'setData',
          description: '生成された補完データをセットします。',
          parameters: {
            type: 'object',
            properties: {
              column: {
                type: 'string',
                description: '指示された補完対象の論理カラム名を指定します。'
              },
              data: {
                type: 'string',
                description: '生成されたデータを改行コードで区切った文字列で指定します。'
              }
            },
            required: ['column', 'data']
          }
        }
      ]
    }
  }
}
