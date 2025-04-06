import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# Thème Bootstrap pour un beau design
external_stylesheets = [dbc.themes.LUX]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Fonction pour charger les données historiques
def load_data():
    path = "/home/ec2-user/Projet_DogeCoin/data.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, names=["datetime", "price"], parse_dates=["datetime"])
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df.dropna(subset=['price'], inplace=True)
        return df
    else:
        return pd.DataFrame(columns=["datetime", "price"])

# Fonction pour charger le rapport quotidien (pour le tableau)
def load_daily_report():
    path = "/home/ec2-user/Projet_DogeCoin/daily_report.csv"
    if os.path.exists(path):
        # On suppose que daily_report.csv est formaté avec l'en-tête : date,open,close,high,low,pct_change
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=["date", "open", "close", "high", "low", "pct_change"])

# Création du graphique principal : Prix, MA et bandes de Bollinger
def create_price_graph(df):
    df = df.sort_values("datetime")
    # Moyenne mobile sur 20 points et écart-type
    df['ma20'] = df['price'].rolling(window=20).mean()
    df['std20'] = df['price'].rolling(window=20).std()
    df['upper_band'] = df['ma20'] + 2 * df['std20']
    df['lower_band'] = df['ma20'] - 2 * df['std20']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['price'],
                             mode='lines', name='Prix'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['ma20'],
                             mode='lines', name='MA20'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['upper_band'],
                             mode='lines', name='Bollinger Upper', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['lower_band'],
                             mode='lines', name='Bollinger Lower', line=dict(dash='dash')))
    fig.update_layout(title="Évolution du prix avec MA20 et Bandes de Bollinger",
                      xaxis_title="Date", yaxis_title="Prix (USD)",
                      hovermode="x unified")
    return fig

# Création d'un graphique secondaire : moyennes mobiles (exemple sur 10 et 20 points)
def create_moving_average_graph(df):
    df = df.sort_values("datetime")
    df['ma10'] = df['price'].rolling(window=10).mean()
    df['ma20'] = df['price'].rolling(window=20).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['price'], mode='lines', name='Prix'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['ma10'], mode='lines', name='MA10'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['ma20'], mode='lines', name='MA20'))
    fig.update_layout(title="Moyennes Mobiles (MA10 & MA20)",
                      xaxis_title="Date", yaxis_title="Prix")
    return fig

# Calcul de KPI journaliers à partir des données
def compute_daily_kpi(df):
    if df.empty:
        return None, None, None, None, None
    # Re-échantillonnage par jour
    df_daily = df.set_index('datetime').resample('D').agg({
        'price': ['first', 'last', 'max', 'min', 'mean', 'std']
    })
    df_daily.columns = ['open', 'close', 'high', 'low', 'avg', 'std']
    df_daily = df_daily.dropna()
    # Dernière journée
    latest_day = df_daily.index.max()
    latest = df_daily.loc[latest_day]
    # Changement en pourcentage
    pct_change = ((latest['close'] - latest['open']) / latest['open']) * 100 if latest['open'] != 0 else None
    return latest_day.date(), latest['open'], latest['close'], latest['high'], latest['low'], pct_change

# Mise en page du dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Dogecoin", className="text-center my-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="price-graph", figure=create_price_graph(load_data())), width=6),
        dbc.Col(dcc.Graph(id="ma-graph", figure=create_moving_average_graph(load_data())), width=6)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Prix Actuel"),
                dbc.CardBody(html.H2(id="current-price", className="card-title"))
            ], color="info", inverse=True),
            width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Changement % Journée"),
                dbc.CardBody(html.H2(id="daily-change", className="card-title"))
            ], color="success", inverse=True),
            width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Max/Min Journée"),
                dbc.CardBody(html.H2(id="daily-highlow", className="card-title"))
            ], color="warning", inverse=True),
            width=4
        )
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(html.H3("Rapport quotidien"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id="daily-report-table",
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
                style_header={'backgroundColor': 'rgb(230,230,230)', 'fontWeight': 'bold'}
            ),
            width=12
        )
    ]),
    dcc.Interval(
        id="interval-component",
        interval=5 * 60 * 1000,  # 5 minutes
        n_intervals=0
    )
], fluid=True)

# Callback pour mettre à jour le dashboard
@app.callback(
    [Output("price-graph", "figure"),
     Output("ma-graph", "figure"),
     Output("current-price", "children"),
     Output("daily-change", "children"),
     Output("daily-highlow", "children"),
     Output("daily-report-table", "columns"),
     Output("daily-report-table", "data")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    df = load_data()
    price_fig = create_price_graph(df)
    ma_fig = create_moving_average_graph(df)
    
    # Calcul des KPI journaliers
    kpi = compute_daily_kpi(df)
    if kpi[0] is not None:
        date_str = str(kpi[0])
        current_price = f"{df['price'].iloc[-1]:.4f} USD"
        daily_change = f"{kpi[5]:.2f}%"
        daily_highlow = f"H: {kpi[3]:.4f} / L: {kpi[4]:.4f}"
    else:
        current_price = "N/A"
        daily_change = "N/A"
        daily_highlow = "N/A"
    
    # Charger le rapport quotidien depuis le CSV
    report_df = load_daily_report()
    if not report_df.empty:
        columns = [{"name": col.capitalize(), "id": col} for col in report_df.columns]
        data = report_df.to_dict('records')
    else:
        columns = [{"name": "Date", "id": "date"},
                   {"name": "Open", "id": "open"},
                   {"name": "Close", "id": "close"},
                   {"name": "High", "id": "high"},
                   {"name": "Low", "id": "low"},
                   {"name": "Pct Change", "id": "pct_change"}]
        data = []
    
    return price_fig, ma_fig, current_price, daily_change, daily_highlow, columns, data

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
