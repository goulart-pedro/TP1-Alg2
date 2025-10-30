import os
from flask import Flask, render_template, request
from src.indexing import build_index_from_zip
import zipfile
from src.snippet import generate_snippet
from src.relevance import calculate_corpus_stats, rank_by_relevance
from src.search import corpus_search, search_tokenizer
from src.insert import trie
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['TRIE_ROOT'] = trie()

@app.route('/upload-direct', methods=['POST'])
def upload_and_extract_direct():
    if 'zip_file' not in request.files:
        return 'Nenhum arquivo selecionado', 400
    
    file = request.files['zip_file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    
    if file:
        # Criar pasta de extração com nome corpus
        # considerar um nome único caso seja interessante ter vários
        extract_folder_name = "corpus"
        extract_path = os.path.join('extractions/corpus', extract_folder_name)
        os.makedirs(extract_path, exist_ok=True)

        filepath = extract_path + '/' + secure_filename(file.filename)
        file.save(filepath)
        app.config['TRIE_ROOT'] = build_index_from_zip(filepath)

        CORPUS_STATS = calculate_corpus_stats(app.config['TRIE_ROOT'])
        return render_template('index.html', corpus_was_indexed=True)

        
print(app.config['TRIE_ROOT'])
RESULTS_PER_PAGE = 10              



# este bloco roda UMA VEZ quando o servidor é iniciado
print("--- INICIANDO SERVIDOR DE BUSCA ---")

# # persistencia do índice
# if os.path.exists(INDEX_FILE_PATH):
#     print(f"Passo 1/3: Carregando índice de '{INDEX_FILE_PATH}'...")
#     TRIE_ROOT = load_index_from_disk(INDEX_FILE_PATH)
# else:
#     print(f"Passo 1/3: Construindo índice de '{CORPUS_ZIP_FILE}'...")
#     TRIE_ROOT = build_index_from_zip(CORPUS_ZIP_FILE)
#     save_index_to_disk(TRIE_ROOT, INDEX_FILE_PATH)

# print("Passo 2/3: Calculando estatísticas do corpus para z-score...")
CORPUS_STATS = {}


# print("Passo 3/3: Carregando conteúdo dos documentos para snippets...")
# ALL_DOCUMENTS = load_documents_into_memory(CORPUS_ZIP_FILE)

# print("--- SERVIDOR PRONTO ---")


@app.route("/", methods=['GET']) 
def handle_search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)

    if not query:
        return render_template('index.html')
    
    # tokeniza a query e executa a busca booleana    
    tokens = search_tokenizer(query)
    matching_docs = corpus_search(app.config['TRIE_ROOT'], tokens)
    
    # extrai as palavras chave e ordena os documentos por relevancia
    query_keywords = [tvalue for ttype, tvalue in tokens if ttype == 'keyword']
    ranked_docs = rank_by_relevance(matching_docs, query_keywords, app.config['TRIE_ROOT'], CORPUS_STATS)

    # paginaçao
    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    paginated_docs = ranked_docs[start_index:end_index]

    # snippets
    final_results = []
    primary_term = query_keywords[0] if query_keywords else "" # destaque
    for doc_name in paginated_docs:
        full_content = ALL_DOCUMENTS.get(doc_name, "")
        snippet = generate_snippet(full_content, primary_term)
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
