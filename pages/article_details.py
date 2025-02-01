from dash import register_page, html, dcc
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from src.helpers import fetch_all_revisions, format_timestamp_readable

register_page(__name__, path_template="/details/<article_name>")

def get_top_10_contributors(df):
    top_contributors = df["user"].value_counts().sort_values(ascending=False)
    return top_contributors.head(10)

def add_activity_timeline(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day


def layout(article_name=None, **kwargs):
    df_rev = fetch_all_revisions(article_name)
    if(df_rev is None or df_rev.empty):
        return html.Div([
            html.H1(f"Article Details: {article_name}", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.P("No data available for this article.", style={'textAlign': 'center', 'color': 'red'})
        ])

    total_contributors = df_rev["user"].nunique()
    latest_rev_timestamp = df_rev["timestamp"].max()
    total_edits = df_rev.shape[0]

    # For matics table
    matrics_table = dbc.Table(
        [
            html.Tr([html.Th("Matrics"), html.Th("Value")]),
            html.Tr([html.Td("Total Edits"), html.Td(total_edits)]),
            html.Tr([html.Td("Number of Contributors"), html.Td(total_contributors)]),
            html.Tr([html.Td("Most Recent Edit"), html.Td(format_timestamp_readable(latest_rev_timestamp))]),
        ]
    )

    #  For top contributors table
    top_contributors_arr = get_top_10_contributors(df_rev)
    df_top_contributors = top_contributors_arr.reset_index()
    df_top_contributors.columns = ["Contributors", "No of Edits"]
    contributors_table = dbc.Table.from_dataframe(
        df_top_contributors
    )

    # Adds hour and day column for edit timeline
    add_activity_timeline(df_rev)
    timeline_fig = px.line(
        df_rev,
        x = "timestamp",
        y = df_rev.index,
        labels = { "index": "Total Edits", "timestamp": "Time" },
        title = "Edit activity Over Time"
    )

    hour_fig = px.histogram(
        df_rev,
        x = "hour",
        nbins = 24,
        labels = { "hour": "Hour of the Day", "count": "Number of Edits" },
        title = "Edit Activity By Hour of the Day"
    )

    return html.Div([
        html.H1(f"{article_name}"),
        html.Div([
            html.H3("Matrics"),
            matrics_table
        ]),
        html.Div([
            html.H3("Top Contributors"),
            contributors_table,
        ], style={"marginTop": "20px"}),
        html.Div([
            html.H3("Edit Timeline"),
            dcc.Graph(figure = timeline_fig)
        ], style={"marginTop": "20px"}),
        html.Div([
            html.H3("Hourly Edit Count"),
            dcc.Graph(figure = hour_fig)
        ], style={"marginTop": "20px"}),
    ])

    return html.Div()