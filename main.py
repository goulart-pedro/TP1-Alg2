from dataclasses import dataclass, field
from flask import Flask, render_template, request
from src.search import corpus_search, search_tokenizer
from src.insert import trie_node

app = Flask(__name__)

@app.route("/")
def handle_search(methods=['POST', 'GET']):
    _query: str = request.args.get('query', '')
    
    ttrie = trie_node()
    
    if _query == '':
        return render_template(
            'index.html',
            corpus_was_indexed = len(ttrie.branches)!= 0
        )
    else:
        _page_num = request.args.get('page', 1, type=int)
        current_page = request.args.get('page', 1, type=int)
        

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
        total_pages = (len(_results) + 10 - 1) // 10

        return render_template(
            'results.html',
            length=len(_results),
            query=_query,
            results=_results[(_page_num -1) * 10: _page_num * 10 - 1],
            total_pages=total_pages,
            current_page=current_page
        )
