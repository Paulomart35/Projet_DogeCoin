import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import os

app = dash.Dash(__name__)

def load_data():
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv", names=["datetime", "price"], parse_dates=["datetime"])
        # Convertir la colonne "price" en numérique
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["datetime", "price"])

# Définir le layout du dashboard
app.layout = html.Div(children=[
    html.H1(children='Dashboard Dogecoin'),
    dcc.Graph(id='price-graph'),
    # Intervalle pour mettre à jour le graphique automatiquement (toutes les minutes)
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # 1 minute en millisecondes
        n_intervals=0
    )
])

# Callback pour mettre à jour le graphique
@app.callback(
    dash.Output('price-graph', 'figure'),
    [dash.Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    df = load_data()
    fig = px.line(df, x="datetime", y="price", title="Évolution du prix de Dogecoin (USD)")
    return fig

if __name__ == '__main__':
    # Pour rendre l'application accessible depuis l'extérieur, écoute sur 0.0.0.0
    app.run(debug=False, host='0.0.0.0', port=8050)
