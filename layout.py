from dash import html, dcc, dash_table
from components.map import map as mapthing

def get_layout(geojson_data, bhz, points, butecos):
    return html.Div([
        html.Div([
            # Componentes invisíveis para estado compartilhado
            dcc.Store(id='search-state', data=None),
            dcc.Store(id='search-radius', data=2), # Raio inicial de 2km
            dcc.Store(id='search-geometry', data='circle'), # circle | rect
            html.H1("Mapa de Butecos - Belo Horizonte", className="main-title"),
            
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
                    html.Button('🔍', id='search-button', className="search-icon-button")
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

                html.Div([
                    html.Span("Formato:", className="radius-label"),
                    dcc.RadioItems(
                        id='search-shape',
                        options=[
                            {'label': '□', 'value': 'rect'},
                            {'label': '○', 'value': 'circle'}
                        ],
                        value='circle',  # padrão
                        className="shape-selector",
                        inline=True
                    ),
                ], className="radius-box"),
               
                dcc.Button(id='clear', children=html.Span('x')),
            
            ], className="search-container"),

            # No layout, adicione um componente de seleção
            


            # Mapa
            html.Div([
                mapthing(geojson_data, None, bhz)
            ], className="map-container"),
            
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
