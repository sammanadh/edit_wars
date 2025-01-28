from dash import dcc, html

def render(articles_data) :
    return html.Div([
        html.H3("Graphical Comparison of Searched Articles"),
        dcc.Graph(id="comparison-graph", figure = {
            "data": [
                {"x": articles_data["Article Name"], "y": articles_data["Total Edits"], "type": "bar", "name": "Total Edits"},
                {"x": articles_data["Article Name"], "y": articles_data["Number of Contributors"], "type": "bar", "name": "Contributors"},
            ],
            "layout": {"title": "Comparison of Article Statistics"}
        })
    ])