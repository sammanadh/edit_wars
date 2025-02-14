from dash import html, dcc
import dash_bootstrap_components as dbc 
from src.constants import ids

def render():
    return html.Div(
        id=ids.SEARCH_BAR,
        children=[
            html.Div(
                children = [
                    dbc.Input(
                        id=ids.SEARCH_INPUT,
                        type="text",
                        placeholder="enter article name",
                    ),
                    dbc.Button(
                        "search", id=ids.SEARCH_BUTTON
                    )
                ],
                style = {
                    "flex-direction": "row", 
                    "margin": "auto",
                    "display": "flex", 
                    "gap": "2px", 
                    "width": "40%"
                }
            ),
            html.Div(id=ids.SEARCH_ERROR_MESSAGE, style={'marginBottom': '20px', 'color': 'red'})
        ]
    )