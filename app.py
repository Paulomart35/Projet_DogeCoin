import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

external_stylesheets = [dbc.themes.LUX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def load_data():
    if os.path.exists("/home/ec2-user/Projet_DogeCoin/data.csv"):
        df = pd.read_csv("/home/ec2-user/Projet_DogeCoin/data.csv", names=["datetime", "price"], parse_dates=["datetime"])
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["datetime", "price"])

def load_daily_report():
    if os.path.exists("/home/ec2-user/Projet_DogeCoin/daily_report.csv"):
        return pd.read_csv("/home/ec2-user/Projet_DogeCoin/daily_report.csv", header=None, names=["report"])
    else:
        return pd.DataFrame(columns=["report"])

def create_price_graph():
    df = load_data()
    fig = px.line(df, x="datetime", y="price", title="Évolution du prix de Dogecoin (USD)")
    return fig

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Dogecoin", className="text-center mb-4"), width=12)
    ]),
    dbc.Tabs([
        dbc.Tab(label="Suivi en temps réel", tab_id="realtime"),
        dbc.Tab(label="Rapport quotidien", tab_id="daily")
    ], id="tabs", active_tab="realtime"),
    html.Div(id="tab-content", className="p-4"),
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # 5 minutes
        n_intervals=0
    )
], fluid=True)

@app.callback(
    dash.Output("tab-content", "children"),
    [dash.Input("tabs", "active_tab"),
     dash.Input("interval-component", "n_intervals")]
)
def render_tab_content(active_tab, n):
    if active_tab == "realtime":
        df = load_data()
        current_price = df['price'].iloc[-1] if not df.empty else "N/A"
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Prix Actuel"),
                        dbc.CardBody(html.H3(f"{current_price} USD", className="card-title"))
                    ], color="primary", inverse=True),
                    width=4
                )
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='price-graph', figure=create_price_graph()), width=12)
            ])
        ])
    elif active_tab == "daily":
        report_df = load_daily_report()
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H3("Rapport quotidien"), width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        id='daily-report-table',
                        columns=[{"name": i, "id": i} for i in report_df.columns],
                        data=report_df.to_dict('records'),
                        style_table={'overflowX': 'auto'}
                    ),
                    width=12
                )
            ])
        ])
    else:
        return "Aucun contenu à afficher."

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
