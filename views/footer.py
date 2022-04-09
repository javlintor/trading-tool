from dash import html


def make_footer():

    footer = html.Div(
        [
            html.P("Copyright © 2022"),
            html.A(
                "javlintor",
                href="https://github.com/javlintor",
                target="_blank",
                id="github-link"
            ),
        ],
        className="footer flex-container",
    )

    return footer
    