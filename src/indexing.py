import zipfile
import re
import os
from typing import List
from .insert import trie, trie_insert, trie_node

def preprocess_text(text: str) -> List[str]:
    lower_text = text.lower()
    # mantem apenas letras, numeros e espaços
    cleaned_text = re.sub(r'[^a-z0-9\s]', ' ', lower_text)
    words = cleaned_text.split()
    return words

def build_index_from_zip(zip_filepath: str) -> trie_node:
    root_node = trie()
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            file_list = zip_ref.namelist()
    
            for filename in file_list:
                if filename.endswith('.txt') and not filename.startswith('__MACOSX'):
                    with zip_ref.open(filename, 'r') as file:
                        content = file.read().decode('utf-8', errors='ignore')
                        words = preprocess_text(content)
                        base_filename = os.path.basename(filename)
                        
                        for word in words:
                            if word: # string vazia
                                trie_insert(root_node, word, base_filename)
                            
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{zip_filepath}' não foi encontrado.")
        return trie()

    return root_node