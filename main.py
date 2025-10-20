from dataclasses import dataclass
from flask import Flask, render_template, request

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
    index: str
    branches
    
def trie():
    return trie_node('\0', dict())


def trie_insert(root:trie_node, word:str, filename:str):
    # caso: árvore vazia
    if len(root.branches) == 0:
        # insere um nó folha a partir da raiz
        root.branches[word] = trie_node(filename, dict())

    # there already is a suitable key to insert at
    for key in root.branches.keys():
        if word.startswith(key):
            trie_insert(root.branches[key], word[len(key):], filename)

    # if there isnt a a suitable key
    # find a common prefix and insert it into the tree
    prefix = []
    for c,k in zip(word, key):
        if c != k:
            break
        prefix.append(c)

    prefix_str = string(prefix)


    if len(prefix_str) != 0:
        temp = root.branches[key]
        root.branches[prefix_str] = trie_node("", dict())

        new_node = root.branches[prefix_str]
        new_node.branches[word[len(prefix_str):]] = trie_node(filename, dict())

        for key in root.branches[key].branches:
            root.branches[key[len(prefix_str:)]] = root.branches[key]
            root.branches.pop(key, None)
        
            
        
