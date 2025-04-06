import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

# Utiliser un thème Bootstrap, par exemple "LUX"
external_stylesheets = [dbc.themes.LUX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def load_data():
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv", names=["datetime", "price"], parse_dates=["datetime"])
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["datetime", "price"])

# Exemple de graphique
def create_price_graph():
    df = load_data()
    fig = px.line(df, x="datetime", y="price", title="Évolution du prix de Dogecoin (USD)")
    return fig

# Layout enrichi
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Dogecoin", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Prix Actuel", className="card-title"),
                    html.H2(id="current-price", className="card-text")
                ])
            ], color="primary", inverse=True),
            width=4
        ),
        dbc.Col(
            dcc.Graph(id='price-graph', figure=create_price_graph()),
            width=8
        )
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Données en temps réel"),
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in ["datetime", "price"]],
                data=load_data().to_dict('records'),
                style_table={'overflowX': 'auto'}
            )
        ], width=12)
    ]),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Mise à jour toutes les minutes
        n_intervals=0
    )
], fluid=True)

# Callback pour mettre à jour le graphique et l'indicateur
@app.callback(
    [dash.Output('price-graph', 'figure'),
     dash.Output('current-price', 'children'),
     dash.Output('data-table', 'data')],
    [dash.Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = load_data()
    fig = px.line(df, x="datetime", y="price", title="Évolution du prix de Dogecoin (USD)")
    current_price = df['price'].iloc[-1] if not df.empty else "N/A"
    return fig, f"{current_price} USD", df.to_dict('records')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)

