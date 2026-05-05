from geopy.distance import geodesic
from geopy.geocoders import Nominatim

class Node: 
    def __init__(self, ponto, eixo, esquerda=None, direita=None):
        self.ponto = ponto
        self.eixo = eixo
        self.esquerda = esquerda
        self.direita = direita


# https://www.geeksforgeeks.org/dsa/search-and-insertion-in-k-dimensional-tree/
def construir_KDTree(lista_pontos, profundidade=0):
    if not lista_pontos:
        return None

    # A cada profundidade trocamos o eixo ordenado entre lat=0 e lon=1
    # k = 2
    eixo = profundidade % 2 

    # https://courses.physics.illinois.edu/cs225/sp2021/resources/kd-tree/
    lista_pontos.sort(key=lambda p: p[eixo])
    mediana = len(lista_pontos) // 2

    return Node(
        ponto=lista_pontos[mediana],
        eixo=eixo,
        esquerda=construir_KDTree(lista_pontos[:mediana], profundidade + 1),
        direita=construir_KDTree(lista_pontos[mediana + 1:], profundidade + 1)
    )

def butecos_regiao (raiz_arvore, lat_min, lat_max, lon_min, lon_max, profundidade=0):
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
            lista_pontos.extend(butecos_regiao(raiz_arvore.esquerda, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
            
        # Se o retângulo de busca tem qualquer parte à direita da linha de corte
        if lat_max >= lat_ponto:
            lista_pontos.extend(butecos_regiao(raiz_arvore.direita, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
                
    else: # Corte na Longitude
        # Se o retângulo tem qualquer parte "abaixo" da linha de corte
        if lon_min <= lon_ponto:
            lista_pontos.extend(butecos_regiao(raiz_arvore.esquerda, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
            
        # Se o retângulo tem qualquer parte "acima" da linha de corte
        if lon_max >= lon_ponto:
            lista_pontos.extend(butecos_regiao(raiz_arvore.direita, lat_min, lat_max, lon_min, lon_max, profundidade + 1))
        

    return lista_pontos


def butecos_circulo(raiz_arvore, lat_centro, lon_centro, raio_km, profundidade=0):
    lista_pontos = []

    if raiz_arvore is None:
        return lista_pontos

    lat_ponto = raiz_arvore.ponto[0]
    lon_ponto = raiz_arvore.ponto[1]

    # Verifica se o ponto está dentro do círculo
    distancia = geodesic((lat_centro, lon_centro), (lat_ponto, lon_ponto)).kilometers
    if distancia <= raio_km:
        lista_pontos.append(raiz_arvore.ponto)

    eixo = profundidade % 2
    raio_dg = raio_km / 111.11 # raio convertido para graus
    
    if eixo == 0:  # Corte na Latitude
        # Verifica se o círculo intersecta a faixa de latitude à esquerda
        if lat_centro - raio_dg <= lat_ponto:
            lista_pontos.extend(butecos_circulo(raiz_arvore.esquerda, lat_centro, lon_centro, raio_km, profundidade + 1))
        # Verifica se o círculo intersecta a faixa de latitude à direita
        if lat_centro + raio_dg >= lat_ponto:
            lista_pontos.extend(butecos_circulo(raiz_arvore.direita, lat_centro, lon_centro, raio_km, profundidade + 1))
    else:  # Corte na Longitude
        # Verifica se o círculo intersecta a faixa de longitude à esquerda
        if lon_centro - raio_dg <= lon_ponto:
            lista_pontos.extend(butecos_circulo(raiz_arvore.esquerda, lat_centro, lon_centro, raio_km, profundidade + 1))
        # Verifica se o círculo intersecta a faixa de longitude à direita
        if lon_centro + raio_dg >= lon_ponto:
            lista_pontos.extend(butecos_circulo(raiz_arvore.direita, lat_centro, lon_centro, raio_km, profundidade + 1))

    return lista_pontos

# Ordena os bares pela distancia em relação ao ponto de busca.
def ordena_butecos(lista_tuplas, centro_tupla):
    resultado = []
    for lat, lon in lista_tuplas:
        # Calcula a distância usando as tuplas
        dist = geodesic(centro_tupla, (lat, lon)).kilometers
        
        # Cria o dicionário que o Dash-Leaflet e a Tabela esperam
        resultado.append({
            'lat': lat, 
            'lon': lon, 
            'distancia': dist,
            'popupContent': f"Distância: {dist:.2f} km"
        })

    # Ordena pelo campo 'distancia'
    resultado.sort(key=lambda x: x['distancia'])
    return resultado

# Recebe um endereço e devolve os pontos em lat e lon
def descobre_coordenadas(endereco):
    geolocator = Nominatim(user_agent="tp_algoritmos_2")

    local = geolocator.geocode(endereco + ", Belo Horizonte, MG, Brasil")
    if local: 
        print(f"Endereço encontrado: {local.address}")
        return {'lat': local.latitude, 'lon': local.longitude, 'address': local.address}
    else:
        print("Endereço não encontrado.")
        return None
