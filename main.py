import os
from flask import Flask, render_template, request
from src.insert import trie
from src.indexing import (
    build_index_from_zip, 
    save_index_to_disk,
    load_index_from_disk
)
from src.relevance import calculate_corpus_stats, rank_by_relevance
from src.search import corpus_search, search_tokenizer
from src.utils import generate_snippet, find_best_term_for_snippet
from werkzeug.utils import secure_filename

CORPUS_ZIP_FILE = 'bbc-fulltext.zip'
INDEX_FILE_PATH = 'index.idx'
RESULTS_PER_PAGE = 10

app = Flask(__name__)

app.config['CORPUS_PATH'] = 'bbc'
app.config['TRIE_ROOT'] = None  # Será inicializado na primeira requisição
app.config['CORPUS_STATS'] = None
app.config['CORPUS_NAME'] = os.path.basename(INDEX_FILE_PATH)
app.config['INITIALIZED'] = False

def initialize_search_system():
    """Inicializa o sistema de busca apenas uma vez"""
    if app.config['INITIALIZED']:
        return
        
    print("--- INICIANDO SERVIDOR DE BUSCA ---")
    
    if os.path.exists(INDEX_FILE_PATH):
        print(f"Passo 1/2: Carregando índice de '{INDEX_FILE_PATH}'...")
        app.config['TRIE_ROOT'] = load_index_from_disk(INDEX_FILE_PATH)
    else:
        print(f"Passo 1/2: Construindo índice de '{CORPUS_ZIP_FILE}'...")
        app.config['TRIE_ROOT'] = build_index_from_zip(app.config['CORPUS_PATH'], CORPUS_ZIP_FILE)
        save_index_to_disk(app.config['TRIE_ROOT'], INDEX_FILE_PATH)

    print("Passo 2/2: Calculando estatísticas do corpus para z-score...")
    app.config['CORPUS_STATS'] = calculate_corpus_stats(app.config['TRIE_ROOT'])
    app.config['INITIALIZED'] = True
    
    print("--- SERVIDOR PRONTO ---")

def render_index_page():
    """Renderiza a página inicial de forma consistente"""
    trie_is_empty = app.config['TRIE_ROOT'] is None or app.config['TRIE_ROOT'] == trie()
    return render_template(
        'index.html', 
        corpus_was_indexed=not trie_is_empty, 
        corpus_name=app.config['CORPUS_NAME']
    )

@app.before_request
def before_request():
    """Inicializa o sistema antes da primeira requisição"""
    if not app.config['INITIALIZED']:
        initialize_search_system()

@app.route('/save', methods=['GET'])
def handle_save():
    save_index_to_disk(app.config['TRIE_ROOT'], INDEX_FILE_PATH)
    return render_index_page()

@app.route('/upload')
def handle_upload():
    return render_template('upload.html')

@app.route('/upload-direct', methods=['POST'])
def upload_and_extract_direct():
    if 'index_file' not in request.files:
        return 'Nenhum arquivo selecionado', 400
    
    file = request.files['index_file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    
    if file:
        extract_folder_name = "corpus"
        extract_path = os.path.join('extractions', extract_folder_name)
        os.makedirs(extract_path, exist_ok=True)

        filepath = os.path.join(extract_path, secure_filename(file.filename))
        file.save(filepath)
        
        # Recarrega o índice após upload
        app.config['TRIE_ROOT'] = load_index_from_disk(INDEX_FILE_PATH)
        app.config['CORPUS_STATS'] = calculate_corpus_stats(app.config['TRIE_ROOT'])
        
        return render_index_page()

@app.route("/view", methods=['GET'])
def handle_view():
    filepath = request.args.get('file')
    with open(filepath, 'r') as file:
        contents = file.read()
    return render_template('page_view.html', doc_title=filepath, doc_content=contents)
    
@app.route("/", methods=['GET']) 
def handle_search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    # Se não há query, renderiza página inicial
    if not query:
        return render_index_page()
    
    # Processa a busca
    tokens = search_tokenizer(query)
    matching_docs = corpus_search(app.config['TRIE_ROOT'], tokens)
    
    query_keywords = [tvalue for ttype, tvalue in tokens if ttype == 'keyword']
    ranked_docs = rank_by_relevance(
        matching_docs, 
        query_keywords, 
        app.config['TRIE_ROOT'], 
        app.config['CORPUS_STATS']
    )

    # Paginação
    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    paginated_docs = ranked_docs[start_index:end_index]

    # Gera resultados com snippets
    final_results = []
    for doc_name in paginated_docs:
        best_term = find_best_term_for_snippet(
            doc_name, query_keywords, app.config['TRIE_ROOT'], app.config['CORPUS_STATS']
        )
        with open(doc_name) as file_for_snippet:
            snippet = generate_snippet(file_for_snippet.read(), best_term, query_keywords)
            final_results.append({'filename': doc_name, 'snippet': snippet})

    total_pages = (len(ranked_docs) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    return render_template(
        'results.html', 
        query=query, 
        results=final_results,
        current_page=page,
        total_pages=total_pages,
        total_results=len(ranked_docs)
    )

if __name__ == '__main__':
    app.run(debug=True)
