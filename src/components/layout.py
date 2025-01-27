from dash import html, Input, Output, State
import pandas as pd
import dash_bootstrap_components as dbc 
from src.constants import ids
from . import search_bar, article_matrics
from src.helpers import get_article_stats
from . import comparison_graph

articles_data = pd.DataFrame(columns=[
    "Article Name",
    "Total Edits",
    "Number of Contributors",
    "Last Edit Timestamp"
])

def create_layout(app):

    @app.callback(
        [
            Output(ids.ARTICLE_MATRICS_CONTAINER, "children"),
            Output(ids.COMPARISON_GRAPH_CONTAINER, "children"),
        ],
        Input(ids.SEARCH_BUTTON, "n_clicks"),
        State(ids.SEARCH_INPUT, "value"),
    )
    def update_matrics(_, search_value):
        global articles_data

        if not search_value:
            return ""

        searched_article_data = get_article_stats(app, search_value)
        print(searched_article_data)
        if not searched_article_data:
            return (
                f"Article '{search_value}' not found or no data available.",
                ""
            )

        # # Add to history (up to 3 articles)
        if len(articles_data) == 3:
            articles_data = articles_data.iloc[1:]  # Remove the oldest article
        articles_data = pd.concat([articles_data, pd.DataFrame([searched_article_data])], ignore_index=True)
        print(articles_data)

        # Update table, metrics, and graphs
        return (
            article_matrics.render(app, articles_data),
            comparison_graph.render(app, articles_data)
        )

    return html.Div(
        id=ids.MAIN_LAYOUT,
        children=[
            html.Div(
                id=ids.MAIN_HEADER,
                children=[
                    html.H1(["Wikipedia Wars"])
                ],
                style={"width":"100vw", "text-align": "center"}
            ),
            search_bar.render(app),
            html.Div(id=ids.ARTICLE_MATRICS_CONTAINER),
            html.Div(id=ids.COMPARISON_GRAPH_CONTAINER)
        ],
        style={"width": "95%", "margin": "auto"}
    )