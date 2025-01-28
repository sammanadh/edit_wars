from dash import dcc, html, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from src.helpers import fetch_all_revisions, format_timestamp_readable

register_page(__name__, path_template="/details/<article_name>")

# Helper to calculate top contributors
def get_top_contributors(revisions_df):
    contributor_counts = revisions_df["user"].value_counts().reset_index()
    contributor_counts.columns = ["Contributor", "Edits"]
    top_contributors = contributor_counts.head(10)
    return top_contributors


# Helper to calculate edit activity by hour or day
def get_activity_trends(revisions_df):
    revisions_df["timestamp"] = pd.to_datetime(revisions_df["timestamp"])
    revisions_df["hour"] = revisions_df["timestamp"].dt.hour
    revisions_df["day"] = revisions_df["timestamp"].dt.day_name()
    return revisions_df


# Article Details Layout
def layout(article_name=None, **kwargs):
    # Fetch data for the article
    revisions_df = fetch_all_revisions(article_name)
    if revisions_df is None or revisions_df.empty:
        return html.Div([
            html.H1(f"Article Details: {article_name}", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.P("No data available for this article.", style={'textAlign': 'center', 'color': 'red'})
        ])

    # Metrics
    total_edits = len(revisions_df)
    contributors = revisions_df["user"].nunique()
    most_recent_edit = format_timestamp_readable(revisions_df["timestamp"].max())

    metrics = dbc.Table(
        [
            html.Tr([html.Th("Metric"), html.Th("Value")]),
            html.Tr([html.Td("Total Edits"), html.Td(total_edits)]),
            html.Tr([html.Td("Number of Contributors"), html.Td(contributors)]),
            html.Tr([html.Td("Most Recent Edit"), html.Td(most_recent_edit)]),
        ],
        bordered=True,
        hover=True,
        striped=True,
        className="mb-3"
    )

    # Top Contributors
    top_contributors_df = get_top_contributors(revisions_df)
    contributors_table = dbc.Table.from_dataframe(
        top_contributors_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )

    # Edit Activity Timeline
    revisions_df["timestamp"] = pd.to_datetime(revisions_df["timestamp"])
    timeline_fig = px.line(
        revisions_df,
        x="timestamp",
        y=revisions_df.index,
        labels={"y": "Cumulative Edits", "timestamp": "Time"},
        title=f"Edit Activity Over Time for '{article_name}'"
    )

    # Edit Activity by Hour
    revisions_df = get_activity_trends(revisions_df)
    hour_fig = px.histogram(
        revisions_df,
        x="hour",
        nbins=24,
        title="Edit Activity by Hour of the Day",
        labels={"hour": "Hour", "count": "Number of Edits"}
    )

    return html.Div([
        # Title
        html.H1(f"Article Details: {article_name}", style={'textAlign': 'center', 'marginBottom': '20px'}),

        # Article Metrics
        html.Div([
            html.H3("Article Metrics"),
            metrics
        ], style={'marginBottom': '20px'}),

        # Top Contributors Table
        html.Div([
            html.H3("Top Contributors"),
            contributors_table
        ], style={'marginBottom': '20px'}),

        # Edit Activity Timeline
        html.Div([
            html.H3("Edit Activity Timeline"),
            dcc.Graph(figure=timeline_fig)
        ], style={'marginBottom': '20px'}),

        # Edit Activity by Hour
        html.Div([
            html.H3("Edit Activity by Hour"),
            dcc.Graph(figure=hour_fig)
        ])
    ])
