from dash import html, Input, Output, State, page_container, register_page, callback, ALL, ctx
import pandas as pd
import dash_bootstrap_components as dbc 
from src.constants import ids
from src.components import search_bar, article_matrics
from src.helpers import get_article_stats
from src.components import comparison_graph, article_name_badges

register_page(__name__, path="/")

articles_data = pd.DataFrame(columns=[
    "Article Name",
    "Total Edits",
    "Number of Contributors",
    "Last Edit Timestamp"
])

@callback(
    [
        Output(ids.ARTICLE_MATRICS_CONTAINER, "children"),
        Output(ids.COMPARISON_GRAPH_CONTAINER, "children"),
        Output(ids.BADGE_CONTAINER, "children"),
    ],
    Input(ids.SEARCH_BUTTON, "n_clicks"),
    Input({"type": ids.REMOVE_BUTTON, "index": ALL}, "n_clicks"),
    State(ids.SEARCH_INPUT, "value"),
)
def update_matrics(_a, _b,search_value):
    global articles_data

    if ctx.triggered_id == ids.SEARCH_BUTTON:
        if not search_value:
            return ""
        searched_article_data = get_article_stats(search_value)
        if not searched_article_data:
            return (
                f"Article '{search_value}' not found or no data available.",
                ""
            )

        # # Add to history (up to 3 articles)
        if len(articles_data) == 3:
            articles_data = articles_data.iloc[1:]  # Remove the oldest article
        articles_data = pd.concat([articles_data, pd.DataFrame([searched_article_data])], ignore_index=True)

    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == ids.REMOVE_BUTTON:
        deleted_article = ctx.triggered_id["index"]
        articles_data = articles_data[articles_data["Article Name"] != deleted_article]


    # Update table, metrics, and graphs
    return (
        article_matrics.render(articles_data),
        comparison_graph.render(articles_data),
        article_name_badges.render(articles_data)
    )


layout = html.Div([
    html.Div(
        id=ids.MAIN_HEADER,
        children=[
            html.H1(["Wikipedia Wars"])
        ],
        style={"width":"100vw", "text-align": "center"}
    ),
    search_bar.render(),
    html.Div(id=ids.BADGE_CONTAINER),
    html.Div(id=ids.ARTICLE_MATRICS_CONTAINER),
    html.Div(id=ids.COMPARISON_GRAPH_CONTAINER),
])