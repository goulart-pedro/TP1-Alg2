from dash import Input, Output, State, callback, no_update, html
import dash_leaflet.express as dlx
from FuncoesAuxiliares import butecos_regiao, ordena_butecos, descobre_coordenadas
from geopy.distance import geodesic

def register_callbacks(app, butecos, arvore_global, geojson_data, bhz):

    def filter_butecos(lista_butecos, search_value):
        search_lower = search_value.lower()
        return [
            b for b in lista_butecos 
            if search_lower in b['name'].lower() or search_lower in b['address'].lower()
        ]

    mapa_butecos = {(b['lat'], b['lon']): b for b in butecos}

    @app.callback(
        [Output('butecos-table', 'data'),
         Output('butecos-table', 'columns'),
         Output('map-geojson', 'data')],
        [Input('search-bounds', 'bounds'),
         Input('search-state', 'data'),
         Input('search-input', 'value')]
    )
    def update_map_and_table(bounds, search_state, search_value): 
        colunas_padrao = [
            {"name": "Nome", "id": "name"},
            {"name": "Endereço", "id": "address"},
        ]
        
        # 1. SEM BUSCA: Retorna a tabela alfabética e o mapa original
        if not search_state or not bounds:
            butecos_ordenados = sorted(butecos, key=lambda b: b['name'].lower())

            if search_value and search_value.strip():
                butecos_ordenados = filter_butecos(butecos_ordenados, search_value)

            return butecos_ordenados, colunas_padrao, geojson_data
        
        # 2. COM BUSCA: A KD-Tree entra em ação!
        lat_min, lon_min = bounds[0][0], bounds[0][1]
        lat_max, lon_max = bounds[1][0], bounds[1][1]
        
        pontos_filtrados = butecos_regiao(
            arvore_global, lat_min, lat_max, lon_min, lon_max
        )
        
        # Ordena os pontos por distância
        centro_busca = (search_state['lat'], search_state['lon'])
        pontos_ordenados = ordena_butecos(pontos_filtrados, centro_busca)
        
        # Monta as informações para Tabela e Mapa no mesmo loop
        resultado_tabela = []
        pontos_mapa = []
        
        for p in pontos_ordenados:
            chave = (p['lat'], p['lon'])
            if chave in mapa_butecos:
                bar = mapa_butecos[chave].copy() 
                distancia_formatada = f"{p['distancia']:.2f} km"
                
                # Arruma Tabela
                bar['distancia_str'] = distancia_formatada
                resultado_tabela.append(bar)
                
                # Arruma Mapa
                popup_html = (
                    f"<b>{bar['name']}</b><br>"
                    f"{bar['address']}<br>"
                    f"<i style='color: #666; font-size: 12px;'>Distância: {distancia_formatada}</i>"
                )
                pontos_mapa.append({
                    'lat': p['lat'], 
                    'lon': p['lon'], 
                    'popupContent': popup_html
                })

        colunas_com_distancia = colunas_padrao + [
            {'name': 'Distância', 'id': 'distancia_str'}
        ]

        return resultado_tabela, colunas_com_distancia, dlx.dicts_to_geojson(pontos_mapa)

    @app.callback(
        [Output('search-state', 'data', allow_duplicate=True),
         Output('search-input', 'value', allow_duplicate=True)],
        Input('clear', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_selection(n_clicks):
        if n_clicks:
            return None, ''
        return no_update, no_update

    @app.callback(
        Output('clear', 'children'),
        Output('clear', 'style'),
        Input('search-state', 'data')
    )
    def update_address_display(center):
        if center is None:
            return 'Nada selecionado', {'display': 'none'}
        
        return [html.Span(children=center['address'], className='address-text'), html.Span(children=' ✕')], {'display': 'flex'}

    @app.callback(
        Output('center-marker', 'opacity'),
        Output('center-marker', 'position'),
        Input('search-state', 'data'),
        prevent_initial_call=True
    )
    def update_center_marker(center):
        if center is None:
            return 0, [0,0]
        return 1, [center['lat'], center['lon']]

    @app.callback(
        Output('map-container', 'center'),
        Output('search-state', 'data'),
        [Input('search-input', 'n_submit'),
        Input('search-button', 'n_clicks')],
        State('search-input', 'value'),
        prevent_initial_call=True
    )
    def update_map_center(n_submit, n_clicks, search_value):

        if search_value and search_value.strip():
            fetched_center = descobre_coordenadas(search_value)
            if fetched_center:
                return fetched_center, fetched_center
            else:
                return no_update, no_update
        return bhz

    @app.callback(
        Output('map-container', 'zoom'),
        Input('map-container', 'center'),
        prevent_initial_call=True
    )
    def update_zoom(search_state):
        return no_update
   
    @app.callback(
        [Output('search-bounds', 'bounds'),
         Output('search-bounds', 'pathOptions')],
        [Input('search-state', 'data'),
         Input('radius-input', 'value')],
        prevent_initial_call=True
    )
    def update_rectangle(center, radius):
        if not center:
            return no_update, {'opacity': 0, 'fillOpacity': 0}

        if radius is None:
            radius = 2
        
        offset_lat = radius / 111.11
        offset_lon = radius / 111.11
        
        bounds = [
            [center['lat'] - offset_lat, center['lon'] - offset_lon],
            [center['lat'] + offset_lat, center['lon'] + offset_lon]
        ]
        return bounds, {'opacity': 0.6, 'fillOpacity': 0.2}
    