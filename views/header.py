from dash import html


def make_header():
    header = html.Div(
        [
            html.H1("Trading-tool", className="title"),
            html.Div(
                [
                    html.P("Lucas de Lecea", className="subtitle"),
                    html.P("Boosting group", className="description"),
                ]
            ),
        ],
        id="header",
    )

    return header
