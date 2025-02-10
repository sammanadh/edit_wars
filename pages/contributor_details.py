import dash
from dash import dcc, html, Input, Output, State, dash_table, register_page, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests
from src.helpers import fetch_contributor_data
from src.constants import ids

register_page(__name__, path_template="contributor/<contributor_username>")

@callback(
        Output(ids.CONTRIBUTOR_DETAILS_CONTAINER, "children"),
        Input("layout-container", "children"),
        State("url", "pathname"),
)
def on_page_load(_, pathname):
    contributor_username = pathname.split("/")[-1]
    print(contributor_username)

    if not contributor_username:
        return html.P("Please enter a username.")

    data = fetch_contributor_data(contributor_username)

    if data is None or data.empty:
        return "", {}, {}, [], f"No data found for user '{contributor_username}'."

    # Global Stats
    total_edits = len(data)
    unique_articles = data["title"].nunique()

    metrics = html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Total Edits"), dbc.CardBody(html.H4(total_edits))])),
            dbc.Col(dbc.Card([dbc.CardHeader("Articles Edited"), dbc.CardBody(html.H4(unique_articles))])),
        ], className="mb-3"),
    ])

    daily_count = data.groupby(data["timestamp"].dt.date).size().reset_index(name="count")
    # Activity Timeline
    timeline_fig = px.line(
        daily_count,
        x="timestamp",
        y="count",
        labels={"index": "Cumulative Edits", "timestamp": "Time"},
        title=f"Edit Activity Over Time for '{contributor_username}'"
    )

    # Edit Activity by Hour
    data["hour"] = data["timestamp"].dt.hour
    hour_fig = px.histogram(
        data,
        x="hour",
        nbins=24,
        title="Edit Activity by Hour of the Day",
        labels={"hour": "Hour", "count": "Number of Edits"}
    )

    # Top Articles Contributed To
    top_articles = data["title"].value_counts().reset_index()
    top_articles.columns = ["Article Name", "Edits"]
    table_data = top_articles.head(10).to_dict("records")

    return html.Div([
        html.H1("Contributor Details", style={'textAlign': 'center'}),
        
        html.Div([
            dcc.Input(id="username-input", type="text", placeholder="Enter Wikipedia Username"),
            html.Button("Search", id="search-button", n_clicks=0, style={'marginLeft': '10px'}),
        ], style={'textAlign': 'center', 'marginBottom': '20px'}) if contributor_username is None else None,
        
        html.Div(id=ids.GLOBAL_MATRICS, style={'marginBottom': '20px'}, children=metrics),
        
        dcc.Graph(id=ids.ACTIVITY_TIMELINE, figure=timeline_fig),
        
        dcc.Graph(id=ids.EDITS_BY_HOUR, figure=hour_fig),
        
        html.H3("Top Articles Contributed To"),
        dash_table.DataTable(id=ids.TOP_ARTICLES_TABLE, data=table_data)
    ])

# Layout
def layout(contributor_username=None, **kwargs):
   return html.Div(
      children=[
            dcc.Location(id="url", refresh=False),
            dcc.Loading(
                id="loading-spinner",
                type="circle",
                children=[
                    html.Div(id=ids.CONTRIBUTOR_DETAILS_CONTAINER)
                ],
                style={"marginTop": "100px"}
            )
        ],
        id="layout-container",  
   )