import dash
from dash import dcc, html, Input, Output, State, dash_table, register_page, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests
from src.helpers import fetch_contributor_data
from src.constants import ids

register_page(__name__, path_template="contributor")

# Layout
def layout(contributor_username=None, **kwargs):
    return html.Div([
        html.H1("Contributor Details", style={'textAlign': 'center'}),
        
        html.Div([
            dcc.Input(id="username-input", type="text", placeholder="Enter Wikipedia Username"),
            html.Button("Search", id="search-button", n_clicks=0, style={'marginLeft': '10px'}),
        ], style={'textAlign': 'center', 'marginBottom': '20px'}) if contributor_username is None else None,
        
        html.Div(id="global-metrics", style={'marginBottom': '20px'}),
        
        dcc.Graph(id="activity-timeline"),
        
        dcc.Graph(id="edits-by-hour"),
        
        html.H3("Top Articles Contributed To"),
        dash_table.DataTable(id="top-articles-table"),
        
        html.Div(id="error-message", style={"color": "red", "textAlign": "center", "marginTop": "10px"})
    ])

# Callbacks
@callback(
    [
        Output(ids.GLOBAL_MATRICS, "children"),
        Output(ids.ACTIVITY_TIMELINE, "figure"),
        Output(ids.EDITS_BY_HOUR, "figure"),
        Output(ids.TOP_ARTICLES_TABLE, "data"),
        Output(ids.ERROR_MESSAGE, "children"),
    ],
    [
        Input(ids.SEARCH_BUTTON, "n_clicks"),
    ],
    [
        State(ids.USERNAME_INPUT, "value"),
    ],
    prevent_initial_call=True
)
def update_contributor_page(n_clicks, input_username):
    ctx = dash.callback_context

    if(ctx.triggered_id == ids.SEARCH_BUTTON):
        username = input_username
    else:
        username = dash.get_current_app().server.config.get("contributor_username", None)

    if not username:
        return html.P("Please enter a username."), {}, {}, [], ""

    data = fetch_contributor_data(username)

    if data is None or data.empty:
        return "", {}, {}, [], f"No data found for user '{username}'."

    # Global Stats
    total_edits = len(data)
    unique_articles = data["title"].nunique()

    metrics = html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Total Edits"), dbc.CardBody(html.H4(total_edits))])),
            dbc.Col(dbc.Card([dbc.CardHeader("Articles Edited"), dbc.CardBody(html.H4(unique_articles))])),
        ], className="mb-3"),
    ])

    # Activity Timeline
    timeline_fig = px.line(
        data,
        x="timestamp",
        y=data.index,
        labels={"y": "Cumulative Edits", "timestamp": "Time"},
        title=f"Edit Activity Over Time for '{username}'"
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

    return metrics, timeline_fig, hour_fig, table_data, ""