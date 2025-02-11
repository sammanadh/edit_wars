from dash import dcc, html

def render(articles_data) :
    return html.Div(
        children = [
            dcc.Graph(
                id="comparison-graph", 
                figure = {
                    "data": [
                        {"x": articles_data["Article Name"], "y": articles_data["Total Edits"], "type": "bar", "name": "Total Edits"},
                        {"x": articles_data["Article Name"], "y": articles_data["Number of Contributors"], "type": "bar", "name": "Contributors"},
                    ],
                    "layout": {
                        "title": "Graphical Comparison of Searched Articles",
                        "paper_bgcolor": "rgba(0,0,0,0)",  # Makes the graph's outer background transparent
                        "plot_bgcolor": "rgba(0,0,0,0)",   # Makes the inner plot background transparent
                    },
                },
            ),
        ],
        style={
            "padding": "20px",  # Padding inside the card
            "borderRadius": "10px",  # Rounded corners
            "backgroundColor": "#ffffff",
            "margin": "auto",  # Centers the card
        }
    )