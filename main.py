from dataclasses import dataclass, field
from flask import Flask, render_template, request
from typing import Dict, Optional

app = Flask(__name__)

@app.route("/")
def handle_search(methods=['POST', 'GET']):
    _query: str = request.args.get('query', '')

    if _query == '':
        return render_template('index.html')
    else:
        return render_template('results.html', query=_query)

        
# ((key) (labels))
# test tester testing tesla


# node padrão: {id, dict("test", {...})}
# node folha:  {id, dict()}
# id é algo como o nome do arquivo
@dataclass
class trie_node:
   
    index: list[str]
    branches: Dict[str, 'trie_node'] = field(default_factory=dict)

# retorna um nó vazio
def trie():
    return trie_node([], dict())


def compute_common_prefix(w1:str, w2:str):
    common_prefix = ""
    for i in range(min(len(w1), len(w2))):
        if w1[i] != w2[i]:
            break
        common_prefix += w1[i]

    return common_prefix

def has_common_prefix(w1: str, w2: str):
    if compute_common_prefix(w1, w2):
        return True
    return False


def trie_insert(root: trie_node, word: str, filename: str):
    for key, node in root.branches.items():
        if word.startswith(key):
            restof_word = word[len(key):]
            return trie_insert(node, restof_word, filename)
        else:
            common_prefix = compute_common_prefix(key, word)
            if common_prefix:
                restof_key = key[len(common_prefix):]
                restof_word = word[len(common_prefix):]
                root.branches.pop(key)
                # o prefixo nao possui indice a principio
                # se ele está sendo criado é pq nao achei
                # palavra igual antes
                root.branches[common_prefix] = trie_node(
                    [], {restof_key: node
                })
                return trie_insert(
                    root.branches[common_prefix], restof_word, filename
                )
        
    root.branches[word] = trie_node([filename], {})
    return root


# visualizaçao
def print_trie(node: trie_node, prefix=""):
    if len(node.index) != 0:
        print(f"{prefix} -> (Arquivo: {node.index})")
    for key, child in node.branches.items():
        print(f"{prefix}[{key}]")
        print_trie(child, prefix + "  ")



# TODO: adaptar testes para o caso onde o node é dividido
t = trie()
trie_insert(t, 'peter', 't1')
assert t == trie_node(
    index=[],
    branches={'peter': trie_node(index=['t1'], branches={})}
)
trie_insert(t, 'dampf', 't2')
assert t == trie_node(
    index=[],
    branches={
        'peter': trie_node(index=['t1'], branches={}),
        'dampf': trie_node(index=['t2'], branches={})
    }
)
trie_insert(t, 'donau', 't3')
trie_insert(t, 'donaudampfschiff', 't3')
trie_insert(t, 'donaudampfschiffahrt', 't3')
assert t == trie_node(
    index=[],
    branches={
        'peter': trie_node(['t1'], {}),
        'dampf': trie_node(['t2'], {}),
        'donau': trie_node(['t3'], {
                    'dampfschiff': trie_node(['t3'], {
                        'ahrt': trie_node(['t3'], {})
                        })
            })
        })
