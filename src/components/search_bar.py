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
                        placeholder="Type an article name...",
                        # style={'width': '100%', 'padding': '10px', 'marginBottom': '20px'}
                    ),
                    dbc.Button(
                        "Search", id=ids.SEARCH_BUTTON
                    )
                ],
                style={"display": "flex", "flex-direction": "row", "width": "40%", "gap": "2px", "margin": "auto"}
            ),
            # html.Button("Search", id="search-button", style={'marginBottom': '20px'}),
            html.Div(id=ids.SEARCH_ERROR_MESSAGE, style={'color': 'red', 'marginBottom': '20px'})
        ]
    )