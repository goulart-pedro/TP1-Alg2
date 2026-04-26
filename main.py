import random
from dash import Dash, html, dcc, callback, Output, Input
import dash_leaflet as dl


import dash_leaflet.express as dlx


from dash_extensions.enrich import DashProxy
from dash_extensions.javascript import assign

bhz = (-19.9102, -43.9266)

# Create some markers.
delta = lambda: (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
points = [dict(lat=bhz[0] + delta()[0], lon=bhz[1] + delta()[1]) for i in range(100)]
data = dlx.dicts_to_geojson(points)

# Create geojson.
point_to_layer = assign("function(feature, latlng, context) {return L.circleMarker(latlng);}")
geojson = dl.GeoJSON(data=data, pointToLayer=point_to_layer)

app = DashProxy()

app.layout = [
    html.Div(children=
             [html.H1(children="Título"),
              dcc.Input(),
              dl.Map([dl.TileLayer(), geojson], center=bhz, zoom=11, style={'height': '100%', 'width': '100%'})
              ],
             style={"display": 'flex', 'flexDirection': 'column', "alignItems": "center", 'height': '100vh'})]

if __name__ == "__main__":
    app.run(debug=True)
