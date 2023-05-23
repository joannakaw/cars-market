import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pickle

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson') as\
        response:
    poland = json.load(response)
print(poland['features'][0])

with open('cars_model.pickle', 'rb') as file:
    cars_model = pickle.load(file)

df = pd.read_csv("cars_clean.csv")

df.drop(columns=['Unnamed: 0'])
dff = df.rename(columns={'province': 'nazwa'})
dff['nazwa'] = dff['nazwa'].str.lower()
df1 = dff.groupby(by="nazwa").mean('price')
df2 = (dff.groupby(by="nazwa").count())["mark"]
df_map = pd.merge(df1, df2, how="left", on="nazwa")
df_map.reset_index(inplace=True)

unique_mark = sorted(df["mark"].unique())
unique_year = sorted(df["year"].unique(), reverse=True)

# print(unique_year)
# print(unique_mark)

fuel_sum = df["fuel"].value_counts(ascending=False)
# print(fuel_sum)

liczba_rocznik = df["year"].value_counts(ascending=True)
# print(liczba_rocznik)

rows_num = len(df.index)
# print(rows_num)

wwa = df[df["province"] == "pomorskie"]["mark"].value_counts().sort_values(ascending=False)
# print(wwa)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "Rynek samochodów używanych w Polsce"

# WYKRESY
fig1 = px.histogram(df, x='year', y='price',
                    # title="Średnia cena aut według rocznika",
                    histfunc='avg',
                    labels={'year': 'rok produkcji', 'avg of price': 'średnia cena'},
                    log_y=False,
                    color_discrete_sequence=['#5DD39E']
                    )
fig1.update_layout(
    bargap=0.2,
    yaxis_title_text='Średnia cena [PLN]'
)

fig2 = px.histogram(df, x='mark',
                    # title="Liczba oferowanych aut według marki",
                    labels={'mark': 'marka samochodu', 'fuel': 'rodzaj paliwa'},
                    log_y=False,
                    color='fuel',
                    color_discrete_map={'Gasoline': '#5DD39E',
                                        'Diesel': '#BCE784',
                                        'Electric': '#348AA7',
                                        'Hybrid': '#795da3',
                                        'LPG': '#513B56',
                                        'CNG': '#407367'}
                    )
fig2.update_layout(
    bargap=0.2,
    yaxis_title_text='Liczba aut'
)
fig2.update_xaxes(categoryorder='total descending')

fig3 = px.histogram(df, x='fuel',
                    title="Liczba oferowanych aut według rodzaju paliwa",
                    labels={'fuel': 'marka samochodu', },
                    log_y=False,
                    color_discrete_sequence=['indianred']
                    )
fig3.update_layout(bargap=0.2)
fig3.update_xaxes(categoryorder='total descending')


df["mileage_cat"] = pd.cut(df["mileage"],
                           bins=[0., 50000, 100000, 150000, 200000, 3000000],
                           labels=['<50', '50-100', '100-150', '150', '>200'], ordered=False)
# '<50 000', '50 000-100 000', '100 000-150 000', '150 000-200 000', '>200 000'
df["mileage_cat"] = df["mileage_cat"].fillna(value='<50')

fig4 = px.histogram(
    df, x='mileage_cat',
    # title="Liczba oferowanych aut według przebiegu",
    labels={'mileage_cat': 'przebieg w tys. km', '1': '<50 tys. km'},
    log_y=False,
    color_discrete_sequence=['#5DD39E']
)
fig4.update_layout(bargap=0.2,
                   xaxis={'categoryorder': 'array', 'categoryarray': ['<50', '50-100', '100-150', '150', '>200']})
fig4.update_xaxes(categoryorder='array')

przebieg = df["mileage_cat"].value_counts(ascending=True)

fig5 = px.histogram(
    df, x='year',
    labels={'year': 'rok produkcji', 'count': 'ilość'},
    log_y=False,
    color_discrete_sequence=['#5DD39E']
)

fig5.update_layout(
    bargap=0.2,
    yaxis_title_text='Liczba aut'
)

fig6 = px.density_heatmap(
    df, x="year", y="mark", z="price",
    histfunc="avg",
    #color_continuous_scale="Viridis",
    color_continuous_scale=['#FFFFFF', '#319B6C'],
    labels={"avg of price": "średnia cena"})

fig6.update_layout(
    yaxis_title_text="Marka",
    xaxis_title_text="rok produkcji"
)

fig7 = px.histogram(df, x='mark', y='price',
                    # title="Średnia cena aut według marki",
                    histfunc='avg',
                    labels={'mark': 'marka', 'avg of price': 'średnia cena'},
                    log_y=False,
                    color_discrete_sequence=['#5DD39E']
                    )
fig7.update_layout(
    bargap=0.2,
    yaxis_title_text='Średnia cena [PLN]'
)
fig7.update_xaxes(categoryorder='total descending')

fig8 = px.histogram(df, x='fuel', y='price',
                    # title="Średnia cena aut ze względu na rodzaj paliwa",
                    histfunc='avg',
                    labels={'fuel': 'rodzaj paliwa', 'avg of price': 'średnia cena'},
                    log_y=False,
                    color_discrete_sequence=['#5DD39E']
                    )
fig8.update_layout(
    bargap=0.2,
    yaxis_title_text='Średnia cena [PLN]'
)
fig8.update_xaxes(categoryorder='total descending')

# MAPY
fig_a = px.choropleth(data_frame=df_map,
                      geojson=poland,
                      locations="nazwa",
                      featureidkey="properties.nazwa",
                      color="price",
                      color_continuous_scale="Viridis",
                      # range_color=(0, 200000),
                      projection="mercator")
fig_a.update_geos(fitbounds="locations", visible=False)


app.layout = dbc.Container([
    dbc.NavbarSimple(brand='Analiza rynku samochodów osobowych w Polsce wyprodukowanych w latach 1990-2022',
                     className="container-fluid", color='#A5F8D3'),
    dbc.Tabs([
            dbc.Tab(id='tab_1', label='Analiza rynku', children=[
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H6("Liczba oferowanych aut według rocznika",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph-5", figure=fig5)]),
                            className='class="card border-primary mb-3"',
                            style={"width": "100%"}
                        )],
                        width=6),
                    dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    html.H6("Liczba oferowanych aut według rodzaju paliwa",
                                            className="card-title",
                                            style={'fontSize': '16px', 'color': '#525174'}),
                                    dbc.Accordion([
                                        dbc.AccordionItem([html.P(f'{fuel_sum[0]} - {((fuel_sum[0]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[0]),
                                        dbc.AccordionItem([html.P(f'{fuel_sum[1]} - {((fuel_sum[1]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[1]),
                                        dbc.AccordionItem([html.P(f'{fuel_sum[2]} - {((fuel_sum[2]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[2]),
                                        dbc.AccordionItem([html.P(f'{fuel_sum[3]} - {((fuel_sum[3]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[3]),
                                        dbc.AccordionItem([html.P(f'{fuel_sum[4]} - {((fuel_sum[4]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[4]),
                                        dbc.AccordionItem([html.P(f'{fuel_sum[5]} - {((fuel_sum[5]/rows_num)*100).round(2)}% samochodów')], title=fuel_sum.index[5])
                                    ])
                                ]),
                                style={'height': '78vh'},
                                className='class="card border-primary mb-3"'
                            )],
                            width=2),
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H6("Średnia cena auta w poszczególnych rocznikach",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph-1", figure=fig1)
                            ]),
                            className='class="card border-primary mb-3"',
                            style={"width": "100%"}
                        )],
                        width=4),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                                dbc.CardBody([
                                    html.H6("Najpopularniejsze marki oferowanych samochodów",
                                            className="card-title",
                                            style={'fontSize': '16px', 'color': '#525174'}),
                                    dcc.Graph(id="graph-2", figure=fig2)
                                ]),
                            style={"width": "100%"},
                            className='class="card border-primary mb-3"')
                    ], width=6),
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H6("Średnia cena auta według marki i rocznika",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph-6", figure=fig6)
                            ]),
                            style={"width": "100%"},
                            className='class="card border-primary mb-3"'
                        )
                    ], width=6),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H6("Średnia cena auta według marki",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph-7", figure=fig7)
                            ]),
                            style={"width": "100%"},
                            className='class="card border-primary mb-3"')
                    ], width=6),
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                html.H6("Średnia cena auta według rodzaju paliwa",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph-8", figure=fig8)
                            ]),
                            style={"width": "100%"},
                            className='class="card border-primary mb-3"'
                        )
                    ], width=6),
                ]),
                html.Br(),
                html.Hr(),
                dbc.Row([
                    html.H6("Wykres zależności ceny i przebiegu wybranej marki i rocznika", style={'color': '#525174'}),
                    html.Br(),
                    dbc.Col([dcc.Graph(id="graph_scatter")], width=9),
                    dbc.Col([
                        html.P("Wybierz markę:"),
                        dcc.Dropdown(
                            id='dropdown_mark',
                            options=[{'label': i, 'value': i} for i in unique_mark]
                        ),
                        html.Br(),
                        html.P("Wybierz rok produkcji:"),
                        dcc.Dropdown(
                            id='dropdown_year',
                            options=[{'label': i, 'value': i} for i in unique_year]
                        ),
                    ], width=3),
                ])
            ]),
            dbc.Tab(id='tab_2', label='Analiza geograficzna', children=[
                html.Br(),
                dbc.Row([
                    dbc.Col([dbc.Card(
                            dbc.CardBody([
                                html.H6("Analiza ofert w ujęciu geograficznym",
                                        className="card-title",
                                        style={'fontSize': '16px', 'color': '#525174'}),
                                dcc.Graph(id="graph")]),
                        style={"width": "100%"}, className='class="card border-primary mb-3"')], width=7),
                    dbc.Col([
                        dbc.Row([dcc.Dropdown(
                            id='dropdown_1',
                            options=[{'label': i, 'value': j} for i, j in zip(['Średni rok produkcji', 'Średni przebieg', 'Średnia moc silnika', 'Średnia cena', 'Liczba ofert'],
                                                                              ['year', 'mileage', 'vol_engine', 'price', 'mark'])],
                            value='year'
                        )
                        ]),
                        dbc.Row([dcc.Graph(id="graph_7")]),
                    ], width=5),
                ]),
                html.Br(),
                dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    html.H6("Wnioski",
                                            className="card-title",
                                            style={'fontSize': '16px', 'color': '#525174'}),
                                    html.P("Powyższa grafika jest dużym uproszczeniem analizowanych danych i ma na celu przedstawienie zróżnicowania ofert w poszczególnych województwach. "
                                           "Największą liczbę ofert aut znajdziemy w woj. mazowieckim, najmniej z kolei w woj. opolskim i podlaskim."
                                           " Oferty z najstarszymi autami są z woj. świętokrzyskiego i lubelskiego, najnowsze natomiast ze śląskiego."
                                           " Również w woj. śląskim znajdują się auta z najniższą średnią przebiegu. Dla poszukujących aut o dużej mocy silnika, najatrakcyjniejszym rynkiem "
                                           "będzie woj. podlaskie. Najwyższa średnia cen oferowanych aut jest w woj. pomorskim i śląskim, najniższa natomiast w woj. lubelskim. ",
                                           style={'fontSize': '14px', 'color': '#525174'})
                                ]), className='class="card border-primary mb-3"')
                        ], width=12),
                ]),
                html.Br()
            ]),
            dbc.Tab(label='Prognozowanie ceny', children=[
                html.Br(),
                dbc.Row([
                    dbc.Col([html.Div([
                        dbc.Label("Rok produkcji:", html_for="slider_1", style={'fontSize': '16px', 'color': '#525174'}),
                        dcc.Slider(id="slider_1",
                                   min=df.year.min(),
                                   max=df.year.max(),
                                   step=1,
                                   marks={i: str(i) for i in range(df.year.min(), df.year.max()+1, 1)},
                                   tooltip={'placement': 'bottom', 'always_visible': True})
                    ])
                    ],
                        width=10, style={'marginLeft': '60px'}),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([html.Div([
                        dbc.Label("Przebieg [km]:", html_for="slider_2", style={'fontSize': '16px', 'color': '#525174'}),
                        dcc.Slider(id="slider_2",
                                   min=df.mileage.min(),
                                   max=300000,
                                   step=5000,
                                   marks={i: str(i) for i in range(df.mileage.min(), 300001, 20000)},
                                   tooltip={'placement': 'bottom', 'always_visible': True})
                    ])
                    ],
                        width=10, style={'marginLeft': '60px'}),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([html.Div([
                        dbc.Label("Moc silnika [cm3]:", html_for="slider_3", style={'fontSize': '16px', 'color': '#525174'}),
                        dcc.Slider(id="slider_3",
                                   min=df.vol_engine.min(),
                                   max=5000,
                                   step=100,
                                   marks={i: str(i) for i in range(df.vol_engine.min(), 5000 + 1, 500)},
                                   tooltip={'placement': 'bottom', 'always_visible': True})
                    ])
                    ],
                        width=10, style={'marginLeft': '60px'}),

                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([html.Div([
                        dbc.Label("Marka:", html_for="dropdown_2", style={'fontSize': '16px', 'color': '#525174'}),
                            dcc.Dropdown(
                                id='dropdown_2',
                                options=df['mark'].unique()
                            ),
                        html.Br(),
                        dbc.Label("Rodzaj paliwa:", html_for="dropdowan_3", style={'fontSize': '16px', 'color': '#525174'}),
                            dcc.Dropdown(
                                id='dropdown_3',
                                options=[{'label': i, 'value': j} for i, j in zip(['Diesel', 'CNG', 'Benzyna', 'LPG', 'Hybrydowy', 'Elektryczny'],
                                                                                  ['Diesel', 'CNG', 'Gasoline', 'LPG', 'Hybrid', 'Electric'])]
                            )
                            ])],
                        width=3, style={'marginLeft': '60px'}),
                    dbc.Col([
                        html.Div([
                            dbc.Label('Wybrane parametry auta:', style={'fontSize': '16px', 'color': '#525174'}),
                            html.Div(id='div_1')
                        ], style={'margin': '20px'}),
                    ],
                        width=3),
                    html.Br(),
                    dbc.Col([
                        html.Br(),
                        html.Div([
                            dbc.Label("Cena auta o wybranych parametrach to:", style={'margin': '15px', 'fontSize': '16px', 'color': '#525174'}),
                            html.Div(id='div_price', style={'margin': '15px'})
                        ], style={'borderStyle': 'solid', 'borderColor': '#5DD39E', 'borderWidth': '2px', 'borderRadius': '15px'})], width=3),
                ]),
            ], style={'margin': 'auto'}),
        ]),

], fluid=True)

# CALLBACK

# WYKRES


@app.callback(
    Output("graph_scatter", "figure"),
    [Input("dropdown_mark", "value"),
     Input("dropdown_year", "value")]
)
def update_scatter(mark_unique, year_unique):
    df_scatter = df[
        (df.mark == mark_unique) & (df.year == year_unique)
    ]

    traces = []
    for i in df_scatter.mark.unique():
        df_mark = df_scatter[df_scatter["mark"] == i]
        traces.append(go.Scatter(
            x=df_mark["mileage"],
            y=df_mark["price"],
            mode="markers",
            name=i,
            hovertemplate="Przebieg:%{x}<br>Cena:%{y}",
        ))

    return {
        "data": traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'Przebieg [km]'},
            yaxis={'title': 'Cena [PLN]'},
            margin={'l': 50, 'b': 40, 't': 10, 'r': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
        )
    }


# fig = px.scatter(df, x="mileage", y="price")

# MAPA

@app.callback(
    Output("graph", "figure"),
    Input("dropdown_1", "value"))
def display_choropleth(dropdown_1):

    fig = px.choropleth(data_frame=df_map,
                        geojson=poland,
                        locations="nazwa",
                        featureidkey="properties.nazwa",
                        color=dropdown_1,
                        color_continuous_scale="Viridis",
                        projection="mercator")
    fig.update_geos(fitbounds="locations",
                    visible=False)
    return fig


@app.callback(
    Output("graph_7", "figure"),
    Input("dropdown_1", "value"))
def display_figure(dropdown_1):
    if dropdown_1 == "mark":
        fig = px.histogram(df, x='province', y=dropdown_1,
                           histfunc='count',
                           log_y=False,
                           color_discrete_sequence=['#5DD39E']
                           )
        return fig
    else:

        fig = px.histogram(df, x='province', y=dropdown_1,
                           histfunc='avg',
                           log_y=True,
                           color_discrete_sequence=['#5DD39E']
                           )
        return fig

# PREDYKCJA CENY


fuel_pl = {'Diesel': 'Diesel', 'CNG': 'CNG', 'Gasoline': 'Benzyna', 'LPG': 'LPG', 'Hybrid': 'Hybrydowy', 'Electric': 'Elektryczny'}


@app.callback(
    Output('div_1', 'children'),
    [Input('slider_1', 'value'),
     Input('slider_2', 'value'),
     Input('slider_3', 'value'),
     Input('dropdown_2', 'value'),
     Input('dropdown_3', 'value')]
)
def display_par(par_1, par_2, par_3, par_4, par_5):
    if par_1 and par_2 and par_3 and par_4 and par_5:
        par_5 = fuel_pl[par_5]
        return html.Div([
            html.P(f'Rok produkcji: {par_1}', style={'fontSize': '14px', 'color': '#525174'}),
            html.P(f'Przebieg [km]: {par_2}', style={'fontSize': '14px', 'color': '#525174'}),
            html.P(f'Moc silnika [cm3]: {par_3}', style={'fontSize': '14px', 'color': '#525174'}),
            html.P(f'Marka: {par_4}', style={'fontSize': '14px', 'color': '#525174'}),
            html.P(f'Rodzaj paliwa: {par_5}', style={'fontSize': '14px', 'color': '#525174'}),
        ])
    else:
        return html.Div([
            html.P('Aby poznać przewidywaną cenę określ wszystkie parametry')
        ], style={"color": "red"})


@app.callback(
    Output('div_price', 'children'),
    [Input('slider_1', 'value'),
     Input('slider_2', 'value'),
     Input('slider_3', 'value'),
     Input('dropdown_2', 'value'),
     Input('dropdown_3', 'value')]
)
def predict_price(par_1, par_2, par_3, par_4, par_5):
    if par_1 and par_2 and par_3 and par_4 and par_5:

        par_4_1, par_4_2, par_4_3, par_4_4, par_4_5, par_4_6, par_4_7, par_4_8, par_4_9, par_4_10, par_4_11, par_4_12, \
            par_4_13, par_4_14, par_4_15, par_4_16, par_4_17, par_4_18, par_4_19, par_4_20, par_4_21, par_4_22 \
            = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        if par_4 == 'audi':
            par_4_1 = 1
        elif par_4 == 'bmw':
            par_4_2 = 1
        elif par_4 == 'chevrolet':
            par_4_3 = 1
        elif par_4 == 'citroen':
            par_4_4 = 1
        elif par_4 == 'fiat':
            par_4_5 = 1
        elif par_4 == 'ford':
            par_4_6 = 1
        elif par_4 == 'honda':
            par_4_7 = 1
        elif par_4 == 'hyundai':
            par_4_8 = 1
        elif par_4 == 'kia':
            par_4_9 = 1
        elif par_4 == 'mazda':
            par_4_10 = 1
        elif par_4 == 'mercedes-benz':
            par_4_11 = 1
        elif par_4 == 'mini':
            par_4_12 = 1
        elif par_4 == 'mitsubishi':
            par_4_13 = 1
        elif par_4 == 'nissan':
            par_4_14 = 1
        elif par_4 == 'opel':
            par_4_15 = 1
        elif par_4 == 'peugeot':
            par_4_16 = 1
        elif par_4 == 'renault':
            par_4_17 = 1
        elif par_4 == 'seat':
            par_4_18 = 1
        elif par_4 == 'skoda':
            par_4_19 = 1
        elif par_4 == 'toyota':
            par_4_20 = 1
        elif par_4 == 'volkswagen':
            par_4_21 = 1
        elif par_4 == 'volvo':
            par_4_22 = 1

        par_5_1, par_5_2, par_5_3, par_5_4, par_5_5 = 0, 0, 0, 0, 0

        if par_5 == 'Diesel':
            par_5_1 = 1
        elif par_5 == 'Electric':
            par_5_2 = 1
        elif par_5 == 'Gasoline':
            par_5_3 = 1
        elif par_5 == 'Hybrid':
            par_5_4 = 1
        elif par_5 == 'LPG':
            par_5_5 = 1

        df_sample = pd.DataFrame(
            data=[
                [par_1, par_2, par_3, par_4_1, par_4_2, par_4_3, par_4_4, par_4_5, par_4_6, par_4_7, par_4_8, par_4_9,
                 par_4_10, par_4_11, par_4_12, par_4_13, par_4_14, par_4_15, par_4_16, par_4_17, par_4_18, par_4_19,
                 par_4_20, par_4_21, par_4_22, par_5_1, par_5_2, par_5_3, par_5_4, par_5_5]
            ],
            columns=['year', 'mileage', 'vol_engine', 'mark_audi', 'mark_bmw', 'mark_chevrolet', 'mark_citroen',
                     'mark_fiat', 'mark_ford', 'mark_honda', 'mark_hyundai', 'mark_kia', 'mark_mazda',
                     'mark_mercedes-benz', 'mark_mini', 'mark_mitsubishi', 'mark_nissan', 'mark_opel', 'mark_peugeot',
                     'mark_renault', 'mark_seat', 'mark_skoda', 'mark_toyota', 'mark_volkswagen', 'mark_volvo',
                     'fuel_Diesel', 'fuel_Electric', 'fuel_Gasoline', 'fuel_Hybrid', 'fuel_LPG']
        )

        price = cars_model.predict(df_sample)[0]
        price = round(price, 2)

        return html.Div([
            html.P(f'{price} PLN (*sugerowana cena)', style={'fontSize': '16px', 'color': '#525174', 'fontWeight': 'bold'})
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
