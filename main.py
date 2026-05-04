import dash_leaflet.express as dlx
from dash_extensions.enrich import DashProxy

# Imports locais
from utils.load_data import load_coordinates, load_butecos
from FuncoesAuxiliares import construir_KDTree
from layout import get_layout
from callbacks import register_callbacks

# 1. Configurações Iniciais e Carregamento de Dados
bhz = (-19.9102, -43.9266)

points = load_coordinates('coordinates.txt')
butecos = load_butecos(points, 'butecos_bh.csv')
print('Indice Carregado')

arvore_global = construir_KDTree([(p['lat'], p['lon']) for p in points])
print('Índice KD-Tree construído com sucesso!')

geojson_data = dlx.dicts_to_geojson(points)

# 2. Inicialização do App Dash
app = DashProxy(__name__)

# 3. Definição do Layout (Chamando a função do layout.py)
app.layout = get_layout(geojson_data, bhz, points, butecos)

# 4. Registro dos Callbacks (Passando os dados que eles precisam)
register_callbacks(app, butecos, arvore_global, geojson_data, bhz)

# 5. Execução do Servidor
if __name__ == "__main__":
    app.run(debug=True)