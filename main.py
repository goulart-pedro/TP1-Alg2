from dataclasses import dataclass, field
from flask import Flask, render_template, request
from src.search import corpus_search, search_tokenizer
from src.insert import trie_node
from file_upload import upload_and_extract_direct
import zipfile
import os

app = Flask(__name__)

@app.route('/upload-direct', methods=['POST'])
def upload_and_extract_direct():
    if 'zip_file' not in request.files:
        return 'Nenhum arquivo selecionado', 400
    
    file = request.files['zip_file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    
    if file:
        try:
            # Criar pasta de extração com nome corpus
            # considerar um nome único caso seja interessante ter vários
            extract_folder_name = "corpus"
            extract_path = os.path.join('extractions', extract_folder_name)
            os.makedirs(extract_path, exist_ok=True)
            
            # Extrair diretamente do arquivo em memória
            with zipfile.ZipFile(file.stream, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            return render_template('index.html', corpus_was_indexed=True)

        except:
            return "Algo deu errado"

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
