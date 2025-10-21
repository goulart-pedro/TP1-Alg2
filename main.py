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
   
    index: Optional[str]
    branches: Dict[str, 'trie_node'] = field(default_factory=dict)
    
def trie():
    return trie_node(None, dict())


def trie_insert(root: trie_node, word: str, filename: str):
    
    # CASO BASE
    if not word:
        root.index = filename
        return
    for key, child_node in root.branches.items():
        common_prefix = ""
        for i in range(min(len(word), len(key))):
            if word[i] != key[i]:
                break
            common_prefix += word[i]
        if not common_prefix:
            continue
        
        # CASO 1: a palavra inteira cabe perfeitamente em um galho que ja existe
        if common_prefix == key:
            rest_of_word = word[len(key):]
            trie_insert(child_node, rest_of_word, filename)
            return 
        
        # CASO 2: a inserção precisa da divisao de um galho
        else: 
            root.branches.pop(key)
            intermediate_node = trie_node(None, dict())
            rest_of_key = key[len(common_prefix):]
            intermediate_node.branches[rest_of_key] = child_node
            rest_of_word = word[len(common_prefix):]
            new_leaf_node = trie_node(filename, dict())
            intermediate_node.branches[rest_of_word] = new_leaf_node
            root.branches[common_prefix] = intermediate_node
            return 

    root.branches[word] = trie_node(filename, dict())

# visualizaçao
def print_trie(node: trie_node, prefix=""):
    if node.index is not None:
        print(f"{prefix} -> (Arquivo: {node.index})")
    for key, child in node.branches.items():
        print(f"{prefix}[{key}]")
        print_trie(child, prefix + "  ")