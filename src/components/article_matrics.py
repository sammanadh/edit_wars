from dash import html
import dash_bootstrap_components as dbc
from src.constants import ids
from src.helpers import format_timestamp_readable

def render(articles_data):
    articles_data_copy = articles_data.copy()
    total_edits = articles_data_copy["Total Edits"]
    total_contributors = articles_data_copy["Number of Contributors"]
    if not articles_data.empty:
        articles_data_copy["Last Edit Timestamp"] = articles_data_copy["Last Edit Timestamp"].apply(format_timestamp_readable)

    table = dbc.Table.from_dataframe(
        articles_data_copy,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )

    return html.Div([
        table
    ])
