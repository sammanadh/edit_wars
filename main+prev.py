import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import requests

# Initialize the Dash app
app = dash.Dash(__name__)

# Helper function to fetch article stats from Wikipedia API
def get_article_stats(article_name):
    try:
        # Wikipedia API request to fetch revision data
        url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": article_name,
            "rvprop": "timestamp|user|ids",
            "rvlimit": "max",
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        # Extract page data
        page = list(data["query"]["pages"].values())[0]
        if "revisions" not in page:
            return None  # Article not found
        
        # Process revisions
        revisions = page["revisions"]
        total_edits = len(revisions)
        contributors = set(rev["user"] for rev in revisions)
        last_edit = revisions[0]["timestamp"]
        
        # Simulate reverts percentage (not provided directly by API)
        reverts_percentage = min(30, total_edits // 10)  # Example logic
        
        return {
            "Article Name": article_name,
            "Total Edits": total_edits,
            "Number of Contributors": len(contributors),
            "Reverts Percentage": reverts_percentage,
            "Last Edit Timestamp": last_edit,
        }
    except Exception as e:
        print(f"Error fetching data for {article_name}: {e}")
        return None

# Initialize data storage
articles_data = []

# App layout
app.layout = html.Div([
    # Title
    html.H1("Wikipedia Wars Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Search Bar
    html.Div([
        html.Label("Search for an Article:"),
        dcc.Input(
            id="search-input",
            type="text",
            placeholder="Type an article name...",
            style={'width': '100%', 'padding': '10px', 'marginBottom': '20px'}
        ),
        html.Button("Search", id="search-button", style={'marginBottom': '20px'}),
        html.Div(id="error-message", style={'color': 'red', 'marginBottom': '20px'})
    ]),

    # Global Metrics (for up to 3 articles)
    html.Div(id="global-metrics", style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Recently Searched Articles Table
    html.Div([
        html.H3("Recently Searched Articles"),
        dash_table.DataTable(
            id="results-table",
            columns=[
                {"name": "Article Name", "id": "Article Name"},
                {"name": "Total Edits", "id": "Total Edits"},
                {"name": "Number of Contributors", "id": "Number of Contributors"},
                {"name": "Reverts Percentage", "id": "Reverts Percentage"},
                {"name": "Last Edit Timestamp", "id": "Last Edit Timestamp"},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': '#f4f4f4'}
        )
    ]),

    # Graphical Comparison
    html.Div([
        html.H3("Graphical Comparison of Searched Articles"),
        dcc.Graph(id="comparison-graph")
    ])
])

# Callbacks
@app.callback(
    [
        Output("results-table", "data"),
        Output("global-metrics", "children"),
        Output("comparison-graph", "figure"),
        Output("error-message", "children"),
    ],
    Input("search-button", "n_clicks"),
    Input("search-input", "value")
)
def update_dashboard(n_clicks, search_value):
    global articles_data

    if not search_value:
        return [], [], {}, ""

    # Fetch article stats
    new_article = get_article_stats(search_value)
    if not new_article:
        return (
            [article for article in articles_data],
            create_global_metrics(articles_data),
            create_comparison_graph(articles_data),
            f"Article '{search_value}' not found or no data available."
        )

    # Check for duplicates
    if new_article in articles_data:
        return (
            [article for article in articles_data],
            create_global_metrics(articles_data),
            create_comparison_graph(articles_data),
            f"Article '{search_value}' is already in the list."
        )

    # Add to history (up to 3 articles)
    if len(articles_data) == 3:
        articles_data.pop(0)  # Remove the oldest article
    articles_data.append(new_article)

    # Update table, metrics, and graphs
    return (
        [article for article in articles_data],
        create_global_metrics(articles_data),
        create_comparison_graph(articles_data),
        ""
    )

def create_global_metrics(data):
    # Create global metrics cards
    total_articles = len(data)
    total_edits = sum(article["Total Edits"] for article in data)
    total_contributors = sum(article["Number of Contributors"] for article in data)
    articles_with_edit_wars = sum(1 for article in data if article["Reverts Percentage"] > 20)

    metrics = [
        html.Div([
            html.H3("Total Articles"),
            html.P(total_articles, style={'fontSize': '24px'}),
        ], id='metric-card'),

        html.Div([
            html.H3("Total Edits"),
            html.P(total_edits, style={'fontSize': '24px'}),
        ], id='metric-card'),

        html.Div([
            html.H3("Total Contributors"),
            html.P(total_contributors, style={'fontSize': '24px'}),
        ], id='metric-card'),

        html.Div([
            html.H3("Articles with Edit Wars"),
            html.P(articles_with_edit_wars, style={'fontSize': '24px'}),
        ], id='metric-card'),
    ]
    return metrics

def create_comparison_graph(data):
    # Create comparison bar chart
    if not data:
        return {}
    df = pd.DataFrame(data)
    fig = {
        "data": [
            {"x": df["Article Name"], "y": df["Total Edits"], "type": "bar", "name": "Total Edits"},
            {"x": df["Article Name"], "y": df["Number of Contributors"], "type": "bar", "name": "Contributors"},
        ],
        "layout": {"title": "Comparison of Article Statistics"}
    }
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
