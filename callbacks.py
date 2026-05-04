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
        Output('butecos-table', 'data'),
        [Input('search-input', 'value'),
         Input('search-state', 'data')]
    )
    def update_table(search_value, search_state):
        if not search_value or not search_value.strip():
            if search_state:
                centro = (search_state['lat'], search_state['lon'])
                # Retorna uma nova lista ordenada para não quebrar a variável global
                return sorted(butecos, key=lambda b: geodesic(centro, (b['lat'], b['lon'])).kilometers)
            return butecos

        resultado = filter_butecos(butecos, search_value)

        if search_state:
            centro = (search_state['lat'], search_state['lon'])
            resultado.sort(key=lambda b: geodesic(centro, (b['lat'], b['lon'])).kilometers)

        return resultado

    @app.callback(
        Output('map-geojson', 'data'),
        Input('search-bounds', 'bounds'),
        Input('search-state', 'data')
    )
    def update_points(bounds, search_state):
        if bounds is None or search_state is None:
            return geojson_data
        
        lat_min, lon_min = bounds[0][0], bounds[0][1]
        lat_max, lon_max = bounds[1][0], bounds[1][1]
        
        pontos_filtrados = butecos_regiao(
            arvore_global, lat_min, lat_max, lon_min, lon_max
        )

        centro_busca = (search_state['lat'], search_state['lon'])
        pontos_ordenados = ordena_butecos(pontos_filtrados, centro_busca)

        pontos_dict = [
            {
                'lat': p['lat'], 
                'lon': p['lon'], 
                'popupContent': f"Distância: {p['distancia']:.2f} km"
            }
            for p in pontos_ordenados
        ]
        
        return dlx.dicts_to_geojson(pontos_dict)

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
    