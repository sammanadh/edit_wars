from dash import register_page, html, dcc
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from prophet import Prophet
from src.helpers import fetch_all_revisions, format_timestamp_readable
import io
import base64
from datetime import datetime

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

    df_rev['timestamp'] = pd.to_datetime(df_rev['timestamp'], errors='coerce')
    # dataframe for making future prediction
    df_forecast = df_rev.resample('MS', on='timestamp').size().reset_index(name='y')  # 'MS' = Month Start
    df_forecast.columns = ['ds', 'y']

    # Removing timezone
    df_forecast['ds'] = df_forecast['ds'].dt.tz_localize(None)

    # Create a model and fit the dataframe
    model = Prophet()
    model.fit(df_forecast)

    # todays date
    today = datetime.today()

    # dataframe for future dates
    next_thirty_days = pd.date_range(start=today, periods=12, freq='M')
    future = pd.DataFrame({'ds': next_thirty_days})
    future_forecast = model.predict(future)

    # Plot to show the forecast
    forecast_fig = model.plot(future_forecast)
    axes = forecast_fig.gca()
    axes.set_xlim([today, future_forecast['ds'].max()]) # so that the plot only shows data from today onwards
    axes.set_xlabel("Date")
    axes.set_ylabel("Number of Edits")
    
    forecast_fig_base64 = fig_to_base64(forecast_fig)

    #  For top contributors table
    top_contributors_arr = get_top_10_contributors(df_rev)
    df_top_contributors = top_contributors_arr.reset_index()
    df_top_contributors.columns = ["Contributors", "No of Edits"]

    # set the contributor names as links
    df_top_contributors["Contributors"] = df_top_contributors["Contributors"].apply(
        lambda name: dcc.Link(name, href=f"/contributor/{name}", refresh=True),
    )

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
            html.H3("Edit Forecast"),
            # dcc.Graph(figure=forecast_fig)
            html.Img(src=f"data:image/png;base64,{forecast_fig_base64}"),  # Render Image in Dash
        ], style={"marginTop": "20px"}),
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

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    # buf.seek()
    return base64.b64encode(buf.getvalue()).decode()