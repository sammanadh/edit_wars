from dash import register_page, html, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from prophet import Prophet
from src.helpers import fetch_all_revisions, format_timestamp_readable
import io
import base64
from datetime import datetime
import time
from src.constants import ids

register_page(__name__, path_template="/details/<article_name>")

def get_top_10_contributors(df):
    top_contributors = df["user"].value_counts().sort_values(ascending=False)
    return top_contributors.head(10)

def add_activity_timeline(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day


@callback(
    Output(ids.ARTICLE_DETAILS_CONTAINER, "children"),
    Input("layout-container", "children"),
    State("url", "pathname"),
    on_page_load=False
)
def on_page_load(_, pathname):
    article_name = pathname.split("/")[-1]
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
    matrics_table = dbc.Table([
        html.Tr([html.Th("Matrics"), html.Th("Value")]),
        html.Tr([html.Td("Total Edits"), html.Td(total_edits)]),
        html.Tr([html.Td("Number of Contributors"), html.Td(total_contributors)]),
        html.Tr([html.Td("Most Recent Edit"), html.Td(format_timestamp_readable(latest_rev_timestamp))]),
    ])

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
        lambda name: dcc.Link(name, href=f"/contributor/{name.replace(" ", "_")}", refresh=True),
    )

    contributors_table = dbc.Table.from_dataframe(
        df_top_contributors
    )

    daily_count = df_rev.groupby(df_rev["timestamp"].dt.date).size().reset_index(name="count")

    # Adds hour and day column for edit timeline
    add_activity_timeline(df_rev)
    timeline_fig = px.line(
        daily_count,
        x = "timestamp",
        y = "count",
        labels = { "count": "Total Edits", "timestamp": "Time" },
    )

    hour_fig = px.histogram(
        df_rev,
        x = "hour",
        nbins = 24,
        labels = { "hour": "Hour of the Day", "count": "Number of Edits" },
    )

    return html.Div([
        html.Div(
            children=[
                html.H1(f"{article_name}"),
            ],
            style={"width":"100%", "text-align": "center"}
        ),
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.H3("Matrics"),
                        html.Div(
                            children = [
                                matrics_table
                            ],
                            style = {
                                "padding": "20px",
                                "borderRadius": "10px",
                                "background": "#ffffff",
                                "width": "80%",
                                "margin": "auto",
                                "color": "black"
                            },
                        ),
                    ],
                ),
                html.Div([
                    html.H3("Edit Forecast"),
                    html.Div(
                        children=[
                            html.Img(src=f"data:image/png;base64,{forecast_fig_base64}", style={"margin": "auto"}), 
                        ],
                        style={"width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center"}
                    )
                ], style={"marginTop": "20px"}),
                html.Div([
                    html.H3("Top Contributors"),
                    html.Div(
                        children=[
                            contributors_table,
                        ],
                        style={"width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center"}
                    )
                ], style={"marginTop": "20px"}),
                html.Div([
                    html.H3("Edit activity over time"),
                    html.Div(
                        children=[
                            dcc.Graph(figure = timeline_fig)
                        ],
                        style={"width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center"}
                    )
                ], style={"marginTop": "20px"}),
                html.Div([
                    html.H3("Edit Activity By Hour of the Day"),
                    html.Div(
                        children=[
                            dcc.Graph(figure = hour_fig)
                        ],
                        style={"width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center"}
                    )
                ], style={"marginTop": "20px"}),
            ],
            style = {"color": "#fe6f1f"}
        )
    ])

def layout(article_name=None, **kwargs):
    return html.Div(
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Loading(
                id="loading-spinner",
                type="circle",
                children=[
                    html.Div(id=ids.ARTICLE_DETAILS_CONTAINER)
                ],
                style={"marginTop": "100px"}
            )
        ],
        id="layout-container",
        style={ "width" : "80vw", "margin": "auto" }  
    )

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    # buf.seek()
    return base64.b64encode(buf.getvalue()).decode()