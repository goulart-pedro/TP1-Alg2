from dash import html, dcc, dash_table
from components.map import map as mapthing

def get_layout(geojson_data, bhz, points, butecos):
    return html.Div([
        html.Div([
            # Componentes invisíveis para estado compartilhado
            dcc.Store(id='search-state', data=None),
            dcc.Store(id='search-radius', data=2), # Raio inicial de 2km
            html.H1("Mapa da Breja - Belo Horizonte", className="main-title"),
            
            # Instruções
            html.Div([
                html.P("📍 Os pontos no mapa representam os bares participantes do Comida di Buteco - BH 2026", 
                       className="info-text"),
                html.P([
                    "📋 A ",
                    html.A("tabela", 
                           href="#butecos-table", 
                           style={'color': '#3498db', 'textDecoration': 'none', 'fontWeight': 'bold'},
                           title="Clique para ir à tabela"),
                    " abaixo contém todos os butecos da competição ",
                    html.Code("butecos_bh.csv", style={'backgroundColor': '#f4f4f4', 'padding': '2px 4px', 'borderRadius': '3px'})
                ], className="info-text")
            ]),
            
            # Barra de pesquisa
            html.Div([
                html.Div([
                    dcc.Input(
                        id='search-input', 
                        type='text', 
                        placeholder='Digite um endereço em Belo Horizonte...', 
                        className="search-input"
                    ),
                ], className="search-box"),
                
                html.Div([
                    html.Span("Distância: ", className="radius-label"),
                    dcc.Input(
                        id='radius-input', 
                        type='number', 
                        value=2,
                        min=1,
                        step=1,
                        className='radius-input',
                    ),
                    html.Span("km", className="radius-label"),
                ], className="radius-box"),

                dcc.Button(id='clear', children=html.Span('x')),
            
            ], className="search-container"),


            # Mapa
            html.Div([
                mapthing(geojson_data, None, bhz)
            ], className="map-container"),
            
            # Contadores
            html.Div([
                html.P([
                    html.Strong(f"Total de coordenadas no mapa: {len(points)}"),
                    html.Br(),
                    html.Strong(f"Total de butecos na tabela: {len(butecos)}")
                ], className="counters-text")
            ], className="counters-container"),
            
            # Tabela
            html.Div([
                html.H2("Lista de Butecos", className="section-title"),
                html.Div([
                    dash_table.DataTable(
                        id='butecos-table',
                        columns=[
                            {'name': 'Nome', 'id': 'name'},
                            {'name': 'Endereço', 'id': 'address'}
                        ],
                        data=butecos,
                        style_table={'overflowX': 'auto', 'maxHeight': '400px', 'width': '100%'},
                        page_size=15,
                        filter_action='native',
                        sort_action='native',
                        export_format='csv',
                        export_headers='display',
                    )
                ], className="table-wrapper")
            ])
        ], className="content-wrapper")
    ], className="main-container")