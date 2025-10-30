import zipfile
import re
import os
from typing import List, Dict

from .insert import trie, trie_insert, trie_node

def preprocess_text(text: str) -> List[str]:
    lower_text = text.lower()
    cleaned_text = re.sub(r'[^a-z0-9\s]', ' ', lower_text)
    words = cleaned_text.split()
    return words

def build_index_from_zip(zip_filepath: str) -> trie_node:
    root_node = trie()
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if filename.endswith('.txt') and not filename.startswith('__MACOSX'):
                    with zip_ref.open(filename, 'r') as file:
                        content = file.read().decode('utf-8', errors='ignore')
                        words = preprocess_text(content)
                        path_parts = filename.split('/')
                        if len(path_parts) >= 2:
                            category = path_parts[-2]
                            doc_number = path_parts[-1].replace('.txt', '')
                            doc_id = f"{category}_{doc_number}"
                        else:
                            doc_id = os.path.basename(filename)
                        
                        for word in words:
                            if word:
                                trie_insert(root_node, word, doc_id)
    except FileNotFoundError: return trie()
    return root_node

def _get_all_words(node: trie_node, prefix: str, all_words: dict):
    if node.postings: all_words[prefix] = node.postings
    for key, child_node in node.branches.items():
        _get_all_words(child_node, prefix + key, all_words)

def save_index_to_disk(trie: trie_node, filepath: str):
    print(f"Salvando índice em disco em '{filepath}'...")
    all_words_data = {}
    _get_all_words(trie, "", all_words_data)
    with open(filepath, 'w', encoding='utf-8') as f:
        for word, postings in all_words_data.items():
            postings_str = ",".join([f"{doc}:{freq}" for doc, freq in postings.items()])
            f.write(f"{word};{postings_str}\n")
    print("indice salvo com sucesso.")

def load_index_from_disk(filepath: str) -> trie_node:
    print(f"Carregando índice do disco de '{filepath}'...")
    root_node = trie()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word, postings_str = line.strip().split(';', 1)
            for entry in postings_str.split(','):
                doc_name, freq_str = entry.split(':', 1)
                for _ in range(int(freq_str)):
                    trie_insert(root_node, word, doc_name)
    print("indice carregado com sucesso.")
    return root_node

def load_documents_into_memory(zip_filepath: str) -> Dict[str, str]:
    print(f"Carregando conteúdo dos documentos de '{zip_filepath}' para a memória...")
    documents = {}
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if filename.endswith('.txt') and not filename.startswith('__MACOSX'):
                    with zip_ref.open(filename, 'r') as file:
                        content = file.read().decode('utf-8', errors='ignore')
                        path_parts = filename.split('/')
                        if len(path_parts) >= 2:
                            category = path_parts[-2]
                            doc_number = path_parts[-1].replace('.txt', '')
                            doc_id = f"{category}_{doc_number}"
                        else:
                            doc_id = os.path.basename(filename)
                        documents[doc_id] = content
    except FileNotFoundError: return {}
    print(f"✅ {len(documents)} documentos carregados na memória.")
    return documents