from dash import html, page_container 
from src.constants import ids

def create_layout():
    return html.Div(
        id=ids.MAIN_LAYOUT,
        children=[
            page_container
        ],
        style={"width": "95%", "margin": "auto"}
    )