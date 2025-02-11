from dash import html, dcc
import dash_bootstrap_components as dbc
from src.constants import ids
from src.helpers import format_timestamp_readable

def render(articles_data):
    articleButtons = []
    for article_name in articles_data["Article Name"].to_list():
        articleButtons.append(
            html.Div(
                children=[
                    dcc.Link(article_name, href=f"/details/{article_name}", className="btn btn-primary", refresh=True),
                    dbc.Button("X", color="danger", id={"type": ids.REMOVE_BUTTON, "index": article_name}),
                ]
            )
        )

    return html.Div(articleButtons, style={"display":"flex", "gap": "10px", "justifyContent": "center", "marginBottom": "10px"})
