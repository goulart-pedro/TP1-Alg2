from dataclasses import dataclass, field
from flask import Flask, render_template, request
from src.search import corpus_search, search_tokenizer
from src.insert import trie_node

app = Flask(__name__)

@app.route("/")
def handle_search(methods=['POST', 'GET']):
    _query: str = request.args.get('query', '')

    if _query == '':
        return render_template('index.html')
    else:
        ttrie = trie_node(set(), {
            'h': trie_node(set(), {
                'onolulu': trie_node({'Havaí'}, {}),
                'amburgo': trie_node({'Alemanha'}, {})
            }),
            'mo': trie_node(set(), {
                'coca': trie_node({'Brasil'}, {}),
                'n': trie_node(set(), {
                    'aco': trie_node({'Monaco'}, {}),    
                    'tevideu': trie_node({'Uruguai'}, {})
                })
            }),
            'adelaide': trie_node({'Austrália'}, {}),
            'cairo': trie_node({'Egito'}, {})
        })
        
        
        search_tokens = search_tokenizer(_query)
        _results = list(corpus_search(ttrie, search_tokens))
        print(search_tokens)
        print(_results)
        
        return render_template('results.html', query=_query, results=_results)
