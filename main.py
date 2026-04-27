import csv
from dash_extensions.javascript import assign
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy

# coordenadas centrais de belo horizonte
bhz = (-19.9102, -43.9266)

# Carregar coordenadas do arquivo results37-128.txt
points = []
with open('results37-128.txt', 'r', encoding='utf-8') as sample_file:
    for line in sample_file:
        line = line.strip()
        if not line or line == ',':
            continue
        
        try:
            partes = line.split(',')
            lat = float(partes[0].strip())
            lon = float(partes[1].strip())
            
            points.append({
                'lat': lat, 
                'lon': lon, 
                'popupContent': f"Coordenada: {lat:.4f}, {lon:.4f}"
            })
        except (ValueError, IndexError):
            continue

print(f"Carregadas {len(points)} coordenadas do arquivo results37-128.txt")

# Carregar butecos do CSV
butecos = []
with open('butecos_bh.csv', 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';')
    for i, row in enumerate(reader):
        butecos.append({
            'name': row['name'].strip(),
            'address': row['address'].strip(),
            'lat': points[i]['lat'],
            'lon': points[i]['lon']
        })


print(f"Carregados {len(butecos)} butecos do CSV")

# Criar geojson para o mapa
geojson_data = dlx.dicts_to_geojson(points)

app = DashProxy(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Mapa de Butecos - Belo Horizonte", className="main-title"),
        
        # Instruções
        html.Div([
            html.P("📍 Os pontos no mapa representam as coordenadas disponíveis no arquivo results37-128.txt", 
                   className="info-text"),

            html.P([
                "📋 A ",
                html.A("tabela", 
                       href="#butecos-table", 
                       style={'color': '#3498db', 'textDecoration': 'none', 'fontWeight': 'bold'},
                       title="Clique para ir à tabela"),
                " abaixo contém todos os butecos do arquivo ",
                html.Code("butecos_bh.csv", style={'backgroundColor': '#f4f4f4', 'padding': '2px 4px', 'borderRadius': '3px'})
            ], className="info-text")
        ]),
        
        # Barra de pesquisa
        html.Div([
            html.Label("Buscar buteco na tabela:", className="search-label"),
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='Digite o nome do buteco...',
                className="search-input"
            ),
            html.Div(id='search-partials', className='search-partials')
        ], className="search-container"),
        
        # Mapa
        html.Div([
            dl.Map([
                dl.TileLayer(),
                dl.GeoJSON(
                    id='map-geojson',
                    data=geojson_data,
                    cluster=True,
                    zoomToBoundsOnClick=True,
                    superClusterOptions={"radius": 100},
                    options={
                    'onEachFeature': assign("""
                        function(feature, layer) {
                            if (feature.properties && feature.properties.popupContent) {
                                layer.bindPopup(feature.properties.popupContent);
                            }
                        }
                    """)
                    }
                )
            ],  id="map-container", center=bhz, zoom=11.5, style={'height': '500px', 'width': '100%'})
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


# Callback para os resultados parciais de busca
@callback(
    Output('search-partials', 'children'),
    Input('search-input', 'value')
)
def search_partials(search_value):
    if not (search_value and search_value.strip()):
        return []
    
    search_lower = search_value.lower()
    filtered_butecos = [
        b for b in butecos 
        if search_lower in b['name'].lower() or search_lower in b['address'].lower()
    ]

    partial = lambda buteco: html.Div(className='partial-item', children=[
        html.Span(buteco['name'], className='partial-name'),
        html.Span(buteco['address'], className='partial-address')
    ])
    
    return [partial(buteco) for buteco in filtered_butecos]


# centralização do mapa após seleção de resultado
@callback(
    Output('map-container', 'center'),
    Output('map-container', 'zoom'),
    Output('search-input', 'value'),
    Input('search-input', 'n_submit'),
    State('search-input', 'value'),
    prevent_initial_call=True
)
def search_on_enter(n_submit, search_value):
    if n_submit and search_value and search_value.strip():
        search_lower = search_value.lower()
        filtered_butecos = [
            b for b in butecos 
            if search_lower in b['name'].lower() or search_lower in b['address'].lower()
        ][:10]

        # se existem sugestões de busca, selecione a primeira e centralize-a
        # no mapa com zoom 16
        if filtered_butecos:
            return (filtered_butecos[0]['lat'], filtered_butecos[0]['lon']), 16, ''

        # se não, retornar centro e zoom padrão (cuidado para deixar igual)
        else:
            return bhz, 11.5, ''

        # de qlq modo o campo de busca é limpo
        # e consequentemente as sugestões somem
    
    return bhz


# Callback para filtrar a tabela
@callback(
    Output('butecos-table', 'data'),
    Input('search-input', 'value')
)
def update_table(search_value):
    if search_value and search_value.strip():
        search_lower = search_value.lower()
        filtered_butecos = [
            b for b in butecos 
            if search_lower in b['name'].lower() or search_lower in b['address'].lower()
        ]
        return filtered_butecos
    return butecos

if __name__ == "__main__":
    app.run(debug=True)
