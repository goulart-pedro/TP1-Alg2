import random
from dash import Dash, html, dcc, callback, Output, Input
import dash_leaflet as dl


import dash_leaflet.express as dlx


from dash_extensions.enrich import DashProxy
from dash_extensions.javascript import assign

bhz = (-19.9102, -43.9266) # coordenadas centrais de belo horizonte


points = []
with open('results37-128.txt') as sample_file:
    for line in sample_file:
        comma_location = line.find(',')

        # para locais onde não foi possível conseguir coordenadas
        if line == ',\n':
            continue
with open('results37-128.txt') as sample_file:
    for line in sample_file:
        comma_location = line.find(',')

        # para locais onde não foi possível conseguir coordenadas
        if line == ',\n':
            continue

        lat, lon = line.split(',')

        points.append({'lat': float(lat), 'lon': float(lon)})

# Pontos amostrais aleatórios
# delta = lambda: (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
# points = [dict(lat=bhz[0] + delta()[0], lon=bhz[1] + delta()[1]) for i in range(100)]
data = dlx.dicts_to_geojson(points)

# Create geojson.
# point_to_layer = assign("function(feature, latlng, context) {return L.circleMarker(latlng);}")
# geojson = dl.GeoJSON(data=data, pointToLayer=point_to_layer)

app = DashProxy()

app.layout = [
    html.Div(children=
             [html.H1(children="Título"),
              dcc.Input(),

              # https://www.dash-leaflet.com/docs/geojson_tutorial
              dl.Map([
                  dl.TileLayer(),
                  dl.GeoJSON(
                      data=dlx.dicts_to_geojson(points),
                      cluster=True,
                      zoomToBoundsOnClick=True,
                      superClusterOptions={"radius": 100})
              ],
                     center=bhz, zoom=11.5, style={'height': '100%', 'width': '100%'})
              ],
             style={"display": 'flex', 'flexDirection': 'column', "alignItems": "center", 'height': '100vh'})]

if __name__ == "__main__":
    app.run(debug=True)
