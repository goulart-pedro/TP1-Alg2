from dash_extensions.javascript import assign
import dash_leaflet as dl
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, no_update


def map(geojson_data, bounds, center, zoom=11.5):
    """Cria o componente do mapa"""
    
    # Função JavaScript para popups
    on_each_feature = assign("""
        function(feature, layer) {
            if (feature.properties && feature.properties.popupContent) {
                layer.bindPopup(feature.properties.popupContent);
            }
        }
    """)
    
    # Camadas do mapa
    camadas = [dl.TileLayer(),
               # marcador de centro inicialmente escondido
               # https://leafletjs.com/examples/custom-icons/
               dl.Marker(id='center-marker', position=[0, 0], opacity=0,
                         icon={'iconUrl': 'assets/map-center.png', 'iconAnchor': [19,19], 'iconSize': [38,38]}),
               dl.Rectangle(id='search-bounds',
                            bounds=[[0,0],
                                    [0,0]],
                            color="#0000ff",
                            weight=2,
                            fillOpacity=0.1)]

                
    # Adicionar GeoJSON
    camadas.append(dl.GeoJSON(
        id='map-geojson',
        data=geojson_data,
        cluster=True,
        zoomToBoundsOnClick=True,
        superClusterOptions={"radius": 100},
        options={'onEachFeature': on_each_feature}
    ))
    
    return html.Div([
        dl.Map(camadas, id="map-container", center=center, 
               zoom=zoom, style={'height': '500px', 'width': '100%'})
    ], className="map-container")
