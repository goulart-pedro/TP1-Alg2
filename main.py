import csv

from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, no_update
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy
from KDTree import construir_KDTree

from utils.load_data import load_coordinates, load_butecos

from components.map import map as mapthing


from geopy.geocoders import Nominatim

def descobre_coordenadas(endereco):
    geolocator = Nominatim(user_agent="tp_algoritmos_2")

    local = geolocator.geocode(endereco + ", Belo Horizonte, MG, Brasil")
    if local: 
        print(f"Endereço encontrado: {local.address}")
        return {'lat': local.latitude, 'lon': local.longitude, 'address': local.address}
    else:
        print("Endereço não encontrado.")
        return None

# coordenadas centrais de belo horizonte
bhz = (-19.9102, -43.9266)

points = load_coordinates('coordinates.txt')
butecos = load_butecos(points, 'butecos_bh.csv')
print('Indice Carregado')


# Criar geojson para o mapa
geojson_data = dlx.dicts_to_geojson(points)


# Definir offset em graus (aproximadamente 0.01° = 1.1km)
offset_lat = 0.1   # ~11km
offset_lon = 0.1   # ~11km

# Calcular bounds
bounds = [
    [bhz[0] - offset_lat, bhz[1] - offset_lon],  # sudoeste (canto inferior esquerdo)
    [bhz[0] + offset_lat, bhz[1] + offset_lon]   # nordeste (canto superior direito)
]


app = DashProxy(__name__)

app.layout = html.Div([
    html.Div([
        # Componentes invisíveis para estado compartilhado
        dcc.Store(id='search-state', data=None),
        dcc.Store(id='search-radius', data=2), # Raio inicial de 2km
        html.H1("Mapa da Breja - Belo Horizonte", className="main-title"),
        
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
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='Digite um endereço',
                className="search-input"
            ),
            # value sincroniza com o estado inicial, dps tentar mudar isso no
            # runtime com alguma função
            dcc.Input(id='radius-input', type='number', value=2),
            dcc.Button(id='clear'),
            # html.Div(id='search-partials', className='search-partials')
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

# APENAS PARA TESTE
def filter_butecos(butecos, search_value):
    search_lower = search_value.lower()
    
    return [
        b for b in butecos 
        if search_lower in b['name'].lower() or search_lower in b['address'].lower()
    ]


@callback(
    Output('search-radius', 'data'),
    Input('radius-input', 'n_submit'),
    State('radius-input', 'value'),
    prevent_initial_call = True
)
def update_search_radius(nsubmit, new_radius):
    return new_radius


@callback(
    [Output('search-state', 'data', allow_duplicate=True),
     Output('search-input', 'value', allow_duplicate=True)],
    Input('clear', 'n_clicks'),
    prevent_initial_call=True
)
def clear_selection(n_clicks):
    if n_clicks:
        return None, ''

    return no_update, no_update


@callback(
    Output('clear', 'children'),
    Input('search-state', 'data')
)
def update_address_display(center):
    if center is None:
        return 'Nada selecionado'

    return center['address'] + ' ✕'


@callback(
    Output('center-marker', 'opacity'),
    Output('center-marker', 'position'),
    Input('search-state', 'data'),
    prevent_initial_callback = True
)
def update_center_marker(center):
    if center is None:
        return 0, [0,0]
    
    print("Mostrando marcador de centro")
    return 1, [center['lat'], center['lon']]
    


# centralização do mapa após seleção de resultado
@callback(
    Output('map-container', 'center'),
    Output('search-state', 'data'),
    Input('search-input', 'n_submit'),
    State('search-input', 'value'),
    prevent_initial_call=True
)
def update_map_center(n_submit, search_value):
    print(f"Enviando busca {search_value}")
    
    if n_submit and search_value and search_value.strip():
        fetched_center = descobre_coordenadas(search_value)

        # se existem sugestões de busca, selecione a primeira, centralize-a
        # e guarde o selecionado em search-state
        if fetched_center:
            print('Novo centro: ', fetched_center['address'])
            return fetched_center, fetched_center

        # se não, não modificar
        else:
            print("Nenhum resultado encontrado")
            return no_update, no_update

    return bhz


# EM HIPOTESE ALGUMA ATUALIZE O ZOOM E O CENTRO AO MESMO TEMPO
@callback(
    Output('map-container', 'zoom'),
    Input('map-container', 'center'),
    prevent_initial_call=True
)
def update_zoom(search_state):
    return no_update


# Callback para filtrar a tabela
@callback(
    Output('butecos-table', 'data'),
    Input('search-input', 'value')
)
def update_table(search_value):
    if search_value and search_value.strip():
        search_lower = search_value.lower()
        return filter_butecos(butecos, search_value)

    return butecos



def pontos_relevantes (raiz_arvore, lat_min, lat_max, lon_min, lon_max, profundidade=0):
    lista_pontos = []

    if raiz_arvore is None:
        return lista_pontos

    lat_ponto = raiz_arvore.ponto[0]
    lon_ponto = raiz_arvore.ponto[1]

    # Verifica se a raiz está dentro dos parâmetros e a adiciona ou não na lista
    if (lat_min <= lat_ponto <= lat_max) and (lon_min <= lon_ponto <= lon_max):
        lista_pontos.append(raiz_arvore.ponto)

    eixo = profundidade % 2

    if eixo == 0: # Corte na Latitude
        # Se o retângulo de busca tem qualquer parte à esquerda da linha de corte
        if lat_min <= lat_ponto:
            lista_pontos.extend(pontos_relevantes(raiz_arvore.esquerda, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
            
        # Se o retângulo de busca tem qualquer parte à direita da linha de corte
        if lat_max >= lat_ponto:
            lista_pontos.extend(pontos_relevantes(raiz_arvore.direita, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
                
    else: # Corte na Longitude
        # Se o retângulo tem qualquer parte "abaixo" da linha de corte
        if lon_min <= lon_ponto:
            lista_pontos.extend(pontos_relevantes(raiz_arvore.esquerda, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
            
        # Se o retângulo tem qualquer parte "acima" da linha de corte
        if lon_max >= lon_ponto:
            lista_pontos.extend(pontos_relevantes(raiz_arvore.direita, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
        

    return lista_pontos



@callback(
    Output('map-geojson', 'data'),
    Input('search-bounds', 'bounds'),
    Input('search-state', 'data')
)
def update_points(bounds, search_state):
    pontos_tupla = [(p['lat'], p['lon']) for p in points]
    arvore_kdtree = construir_KDTree(pontos_tupla)
    
    print(f"Atualização com limites {bounds}")
    
    if bounds is None or search_state is None:
        return geojson_data
    
    # bounds = [[lat_min, lon_min], [lat_max, lon_max]]
    lat_min = bounds[0][0]
    lon_min = bounds[0][1]
    lat_max = bounds[1][0]
    lon_max = bounds[1][1]
    
    pontos_filtrados = pontos_relevantes(
        arvore_kdtree, 
        lat_min, lat_max, 
        lon_min, lon_max
    )
    
    # Converter pontos filtrados para o formato original
    pontos_dict = [
        {'lat': p[0], 'lon': p[1], 'popupContent': f"Coordenada: {p[0]:.4f}, {p[1]:.4f}"}
        for p in pontos_filtrados
    ]
    
    return dlx.dicts_to_geojson(pontos_dict)


@callback(
    [Output('search-bounds', 'bounds'),
     Output('search-bounds', 'pathOptions')],
    [Input('search-state', 'data'),
     Input('search-radius', 'data')],
    prevent_initial_call=True
)
def update_rectangle(center, radius):
    """Muda a cidad e geometria do r, ou o torna invisívelvisível) quando não há seleção"""
    # Caso sem seleção
    # estilo de rect só é mutável através de pathOptions no runtime
    if not center:
        print('Nenhum centro armazenado; Escondendo retângulo')
        return no_update, {'opacity': 0, 'fillOpacity': 0}
    
    # Calcular bounds convertendo radius (km) para graus
    # 1 grau ≈ 111.11 km
    offset_lat = radius / 111.11
    offset_lon = radius / 111.11
    
    bounds = [
        [center['lat'] - offset_lat, center['lon'] - offset_lon],
        [center['lat'] + offset_lat, center['lon'] + offset_lon]
    ]
    
    print(f"Retângulo atualizado: {bounds}")
    return bounds, {'opacity': 0.6, 'fillOpacity': 0.2}


if __name__ == "__main__":
    app.run(debug=True)
