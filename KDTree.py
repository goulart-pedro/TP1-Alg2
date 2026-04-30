# https://www.geeksforgeeks.org/dsa/search-and-insertion-in-k-dimensional-tree/

class Node: 
    def __init__(self, ponto, eixo, esquerda=None, direita=None):
        self.ponto = ponto
        self.eixo = eixo
        self.esquerda = esquerda
        self.direita = direita


def construir_KDTree(lista_pontos, profundidade=0):
    if not lista_pontos:
        return None

    # A cada profundidade trocamos o eixo ordenado entre lat=0 e lon=1
    # k = 2
    eixo = profundidade % 2 

    # Ordenação da lista de acordo com https://courses.physics.illinois.edu/cs225/sp2021/resources/kd-tree/
    lista_pontos.sort(key=lambda p: p[eixo])
    mediana = len(lista_pontos) // 2

    return Node(
        ponto = lista_pontos[mediana],
        eixo = eixo,
        esquerda = construir_KDTree(lista_pontos[:mediana], profundidade + 1),
        direita = construir_KDTree(lista_pontos[mediana + 1:], profundidade + 1)
    )

# debug
def imprimir_arvore(no, nivel=0, prefixo="Raiz: "):
    if no is not None:
        # Mostra qual eixo está dividindo o espaço (0 = Lat, 1 = Lon)
        nome_eixo = "Latitude" if no.eixo == 0 else "Longitude"

        print("    " * nivel + prefixo + str(no.ponto) + f" [{nome_eixo}]")
        imprimir_arvore(no.esquerda, nivel + 1, "Esq: ")
        imprimir_arvore(no.direita, nivel + 1, "Dir: ")

def teste():
    pontos_teste = []

    with open('teste_KDTree.txt', 'r', encoding='utf-8') as lista_teste:
        for linha in lista_teste:
            linha = linha.strip()
            if not linha:
                continue
                # Divide o texto por ponto-e-vírgula
            partes = linha.split(';')
            if len(partes) >= 2:
                lat, lon = float(partes[0]), float(partes[1])
                pontos_teste.append((lat, lon))
                    
    print(f"Foram carregados {len(pontos_teste)} pontos para o teste.\n")
        
    # Constrói a árvore
    arvore = construir_KDTree(pontos_teste)

    # Imprime a árvore no terminal
    imprimir_arvore(arvore)
        
        

if __name__ == "__main__":
    teste()    