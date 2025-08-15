from fasthtml.common import *

# CSS スタイル
css = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0; padding: 20px; background-color: #f5f5f5;
}
.container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.header { border-bottom: 3px solid #2563eb; margin-bottom: 30px; padding-bottom: 15px; }
.title { color: #1e293b; margin: 0; font-size: 2rem; font-weight: 700; }
.subtitle { color: #64748b; margin: 5px 0 0 0; font-size: 1.1rem; }
.meta-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
.meta-card { background: #f8fafc; padding: 15px; border-radius: 6px; border-left: 4px solid #2563eb; }
.meta-label { font-weight: 600; color: #374151; font-size: 0.9rem; margin-bottom: 5px; }
.meta-value { color: #1f2937; font-size: 1rem; }
.table-container { overflow-x: auto; border-radius: 8px; border: 1px solid #e5e7eb; }
.definition-table { width: 100%; border-collapse: collapse; background: white; }
.definition-table th { background: linear-gradient(to bottom, #3b82f6, #2563eb); color: white; padding: 12px; text-align: left; font-weight: 600; font-size: 0.9rem; }
.definition-table td { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem; }
.definition-table tr:hover { background-color: #f8fafc; }
.definition-table tr:last-child td { border-bottom: none; }
.column-name { font-family: 'Monaco', 'Courier New', monospace; font-weight: 600; color: #059669; }
.data-type { font-family: 'Monaco', 'Courier New', monospace; color: #dc2626; font-weight: 500; }
.required { color: #dc2626; font-weight: 600; }
.optional { color: #059669; }
.constraint { font-family: 'Monaco', 'Courier New', monospace; background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 0.8rem; }
.index-badge { background: #fbbf24; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
.primary-badge { background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
.foreign-badge { background: #8b5cf6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
"""

# サンプルデータ
table_info = {
    "table_name": "users",
    "description": "ユーザー情報を管理するテーブル",
    "database": "myapp_production",
    "schema": "public",
    "created_date": "2024-01-15",
    "updated_date": "2024-12-20",
    "record_count": "1,247 件"
}

columns_data = [
    {
        "column_name": "id",
        "data_type": "BIGINT",
        "nullable": False,
        "default": "AUTO_INCREMENT",
        "description": "ユーザーの一意識別子",
        "constraints": "PRIMARY KEY",
        "index_type": "PRIMARY"
    },
    {
        "column_name": "email",
        "data_type": "VARCHAR(255)",
        "nullable": False,
        "default": "",
        "description": "ユーザーのメールアドレス（ログイン用）",
        "constraints": "UNIQUE",
        "index_type": "UNIQUE"
    },
    {
        "column_name": "username",
        "data_type": "VARCHAR(100)",
        "nullable": False,
        "default": "",
        "description": "ユーザー名（表示用）",
        "constraints": "UNIQUE",
        "index_type": "INDEX"
    },
    {
        "column_name": "password_hash",
        "data_type": "VARCHAR(255)",
        "nullable": False,
        "default": "",
        "description": "パスワードのハッシュ値",
        "constraints": "",
        "index_type": ""
    },
    {
        "column_name": "first_name",
        "data_type": "VARCHAR(50)",
        "nullable": True,
        "default": "NULL",
        "description": "名前",
        "constraints": "",
        "index_type": ""
    },
    {
        "column_name": "last_name",
        "data_type": "VARCHAR(50)",
        "nullable": True,
        "default": "NULL",
        "description": "姓",
        "constraints": "",
        "index_type": ""
    },
    {
        "column_name": "date_of_birth",
        "data_type": "DATE",
        "nullable": True,
        "default": "NULL",
        "description": "生年月日",
        "constraints": "",
        "index_type": ""
    },
    {
        "column_name": "phone",
        "data_type": "VARCHAR(20)",
        "nullable": True,
        "default": "NULL",
        "description": "電話番号",
        "constraints": "",
        "index_type": ""
    },
    {
        "column_name": "status",
        "data_type": "ENUM('active','inactive','suspended')",
        "nullable": False,
        "default": "'active'",
        "description": "ユーザーの状態",
        "constraints": "",
        "index_type": "INDEX"
    },
    {
        "column_name": "department_id",
        "data_type": "BIGINT",
        "nullable": True,
        "default": "NULL",
        "description": "所属部署ID",
        "constraints": "FOREIGN KEY",
        "index_type": "FOREIGN"
    },
    {
        "column_name": "created_at",
        "data_type": "TIMESTAMP",
        "nullable": False,
        "default": "CURRENT_TIMESTAMP",
        "description": "レコード作成日時",
        "constraints": "",
        "index_type": "INDEX"
    },
    {
        "column_name": "updated_at",
        "data_type": "TIMESTAMP",
        "nullable": False,
        "default": "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        "description": "レコード更新日時",
        "constraints": "",
        "index_type": "INDEX"
    }
]

def create_badge(index_type):
    if index_type == "PRIMARY":
        return Span("PRIMARY", cls="primary-badge")
    elif index_type == "UNIQUE":
        return Span("UNIQUE", cls="index-badge")
    elif index_type == "INDEX":
        return Span("INDEX", cls="index-badge")
    elif index_type == "FOREIGN":
        return Span("FOREIGN", cls="foreign-badge")
    else:
        return ""

def create_table_row(col):
    return Tr(
        Td(Span(col["column_name"], cls="column-name")),
        Td(Span(col["data_type"], cls="data-type")),
        Td(
            Span("必須", cls="required") if not col["nullable"] else Span("任意", cls="optional")
        ),
        Td(Span(col["default"], cls="constraint") if col["default"] else ""),
        Td(col["description"]),
        Td(Span(col["constraints"], cls="constraint") if col["constraints"] else ""),
        Td(create_badge(col["index_type"]))
    )

app = FastHTML(hdrs=[Style(css)])

@app.route("/")
def home():
    return Div(
        Div(
            H1(f"テーブル定義書: {table_info['table_name']}", cls="title"),
            P(table_info["description"], cls="subtitle"),
            cls="header"
        ),

        # メタ情報
        Div(
            Div(
                Div("データベース", cls="meta-label"),
                Div(table_info["database"], cls="meta-value"),
                cls="meta-card"
            ),
            Div(
                Div("スキーマ", cls="meta-label"),
                Div(table_info["schema"], cls="meta-value"),
                cls="meta-card"
            ),
            Div(
                Div("作成日", cls="meta-label"),
                Div(table_info["created_date"], cls="meta-value"),
                cls="meta-card"
            ),
            Div(
                Div("最終更新", cls="meta-label"),
                Div(table_info["updated_date"], cls="meta-value"),
                cls="meta-card"
            ),
            Div(
                Div("レコード数", cls="meta-label"),
                Div(table_info["record_count"], cls="meta-value"),
                cls="meta-card"
            ),
            cls="meta-info"
        ),

        # カラム定義テーブル
        Div(
            Table(
                Thead(
                    Tr(
                        Th("カラム名"),
                        Th("データ型"),
                        Th("NULL許可"),
                        Th("デフォルト値"),
                        Th("説明"),
                        Th("制約"),
                        Th("インデックス")
                    )
                ),
                Tbody(*[create_table_row(col) for col in columns_data]),
                cls="definition-table"
            ),
            cls="table-container"
        ),

        cls="container"
    )

if __name__ == "__main__":
    serve()
