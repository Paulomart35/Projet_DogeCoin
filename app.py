import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

external_stylesheets = [dbc.themes.LUX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def load_data():
    path = "/home/ec2-user/Projet_DogeCoin/data.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, names=["datetime", "price"], parse_dates=["datetime"])
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["datetime", "price"])

def load_daily_report():
    path = "/home/ec2-user/Projet_DogeCoin/daily_report.csv"
    if os.path.exists(path):
        # On suppose que le CSV contient les colonnes : date, open, close, volatility
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=["date", "open", "close", "volatility"])

def create_price_graph():
    df = load_data()
    fig = px.line(df, x="datetime", y="price", title="Évolution du prix de Dogecoin (USD)")
    return fig

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Dogecoin", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='price-graph', figure=create_price_graph()), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H3("Rapport quotidien"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='daily-report-table',
                columns=[
                    {"name": "Date", "id": "date"},
                    {"name": "Open", "id": "open"},
                    {"name": "Close", "id": "close"},
                    {"name": "Volatility", "id": "volatility"}
                ],
                data=load_daily_report().to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
            width=12
        )
    ]),
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes en millisecondes
        n_intervals=0
    )
], fluid=True)

@app.callback(
    [Output('price-graph', 'figure'),
     Output('daily-report-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    fig = create_price_graph()
    report_df = load_daily_report()
    data = report_df.to_dict('records')
    return fig, data

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
