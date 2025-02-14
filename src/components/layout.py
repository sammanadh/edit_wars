from dash import html, page_container 
from src.constants import ids

def create_layout():
    return html.Div(
        id=ids.MAIN_LAYOUT,
        children=[
            page_container
        ],
        style={
            "width": "95%", 
            "margin": "auto", 
            "backgroundColor": "#0f111e", 
            "color": "#be22e5", 
            "width": "100vw", 
            "minHeight": "100vh"
        }
    )