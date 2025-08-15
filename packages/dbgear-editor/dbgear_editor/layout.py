from fasthtml.common import Title, Main, Div, Li
from monsterui.all import NavContainer, NavHeaderLi, Container, H3, A


def sidebar():
    sidebar = NavContainer(
        NavHeaderLi(H3('Tables'), cls='p-3'),
        Li(A('Test', href='/mt_common_label')),
    )
    return sidebar


def layout(content):
    return (
        Title('DBGear'),
        Container(
            Div(cls='mx-auto p-4')(
                sidebar(),
                Main(content, id='content')
            )
        )
    )
