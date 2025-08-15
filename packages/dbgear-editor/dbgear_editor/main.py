import argparse
from uuid import uuid4

import uvicorn
from fasthtml.common import *  # noqa
from monsterui.all import *  # noqa

from .layout import layout

app, rt = fast_app(hdrs=Theme.blue.headers(), secret_key=str(uuid4()))


@rt('/mt_common_label')
def mt_common_label():
    return layout(P('MT Common Label'))


@rt
def index():
    return layout(P('DBGear Editor is a web-based editor for DBGear.'))


def main():
    """Main entry point for the dbgear-editor command."""
    parser = argparse.ArgumentParser(description='DBGear FastHTML Editor')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    uvicorn.run(
        "dbgear_editor.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
