# Recebe um ponto central e um raio de busca

endereco = input("Digite o endereço para busca: ")
diagonal = float(input("Digite a diagonal de busca em km: "))


# Transforma o endereço em coordenadas (latitude, longitude)

from geopy.geocoders import Nominatim

def descobre_coordenadas(endereco):
    geolocator = Nominatim(user_agent="tp_algoritmos_2")

    local = geolocator.geocode(endereco + ", Belo Horizonte, MG, Brasil")
    if local: 
        print(f"Endereço encontrado: {local.address}")
        return (local.latitude, local.longitude)
    else:
        print("Endereço não encontrado.")
        return None
    

centro = descobre_coordenadas(endereco)
print(f"Coordenadas do centro: {centro}")

# Converte km para graus geográficos
diagonal = diagonal / 111.11

# Com o ponto central em mãos, calculamos os pontos que limitam a área de busca a partir da diagonal fornecida

superior_direito = (centro[0] + diagonal / 2, centro[1] + diagonal / 2) # (latMax, lonMax)
inferior_direito = (centro[0] + diagonal / 2, centro[1] - diagonal / 2) # (latMax, lonMin)

inferior_esquerdo = (centro[0] - diagonal / 2, centro[1] - diagonal / 2) # (latMin, lonMin)
superior_esquerdo = (centro[0] - diagonal / 2, centro[1] + diagonal / 2) # (latMin, lonMax)


# Estabelece os máximos e minimos da latitude e longitude 

lat_max = superior_direito[0]
lat_min = inferior_esquerdo[0]
lon_max = superior_direito[1]
lon_min = inferior_esquerdo[1]


# Confere quais pontos da árvore KD estão dentro dos parâmetros estabelecidos

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

####################################################################################
################################### TESTES #########################################
####################################################################################


from KDTree import Node, construir_KDTree

def teste2():
    pontos_teste = []

    with open('coordinates.txt', 'r', encoding='utf-8') as lista_teste:
        for linha in lista_teste:
            linha = linha.strip()
            if not linha:
                continue
            
            partes = linha.split(',')
            if len(partes) >= 2:
                lat, lon = float(partes[0]), float(partes[1])
                pontos_teste.append((lat, lon))
                    
    print(f"Foram carregados {len(pontos_teste)} pontos para o teste.\n")
        
 
    raiz_arvore = construir_KDTree(pontos_teste)

    return pontos_relevantes(raiz_arvore, lat_min, lat_max, lon_min, lon_max)


resultado = teste2()
print(f"Pontos relevantes encontrados: {resultado}")