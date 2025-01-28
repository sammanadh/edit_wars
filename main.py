from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP
from src.components.layout import create_layout

if __name__ == "__main__":
    app = Dash(external_stylesheets=[BOOTSTRAP], use_pages=True)
    app.title = "Wikipedia Wars"
    app.layout = create_layout()
    app.run()