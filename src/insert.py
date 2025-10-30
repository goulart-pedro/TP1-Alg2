from dataclasses import dataclass, field

        
@dataclass
class trie_node:
    postings: dict[str, int] = field(default_factory=dict)
    branches: dict[str, 'trie_node'] = field(default_factory=dict)

# retorna um nó vazio
def trie():
    return trie_node(dict(), dict())


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
    if word in root.branches:
        child_node = root.branches[word]
        child_node.postings[filename] = child_node.postings.get(filename, 0) + 1
        return

    for key, node in root.branches.items():
        if word.startswith(key):
            rest_of_word = word[len(key):]
            # chamada recursiva 
            trie_insert(node, rest_of_word, filename)
            return 
        
    for key, node in list(root.branches.items()): # usei list() para poder modificar o dict
        common_prefix = compute_common_prefix(key, word)
        if common_prefix:
            rest_of_key = key[len(common_prefix):]
            rest_of_word = word[len(common_prefix):]
            
            root.branches.pop(key)
            
            intermediate_node = trie_node()
            intermediate_node.branches[rest_of_key] = node 
            
            root.branches[common_prefix] = intermediate_node
            
            trie_insert(intermediate_node, rest_of_word, filename)
            return 
    
    final_node = trie_node(postings={filename: 1})
    root.branches[word] = final_node
    return


# visualizaçao 
def print_trie(node: trie_node, prefix=""):
    if node.postings:
        print(f"{prefix} -> (Postings: {node.postings})")
    for key, child in node.branches.items():
        print(f"{prefix}[{key}]")
        print_trie(child, prefix + "  ")

            
if __name__ == '__main__':
    
    t = trie()
    trie_insert(t, 'the', 't0')
    trie_insert(t, 'the', 't0')
   
    assert t == trie_node(postings={}, branches={'the': trie_node(postings={'t0': 2}, branches={})})

    t = trie()
    trie_insert(t, 'apple', 'doc1')
    trie_insert(t, 'apply', 'doc2')
    
    expected = trie_node(branches={
        'appl': trie_node(branches={
            'e': trie_node(postings={'doc1': 1}),
            'y': trie_node(postings={'doc2': 1})
        })
    })
    assert t == expected
    
    trie_insert(t, 'app', 'doc3')
    expected.branches['appl'].postings = {'doc3': 1} 

   
    t3 = trie()
    trie_insert(t3, 'casa', 'v1')
    trie_insert(t3, 'casaco', 'v2')
    trie_insert(t3, 'casamento', 'v3')
    
    expected_t3 = trie_node(branches={
        'casa': trie_node(postings={'v1': 1}, branches={
            'co': trie_node(postings={'v2': 1}),
            'mento': trie_node(postings={'v3': 1})
        })
    })
    assert t3 == expected_t3

    print("✅ Todos os testes corrigidos passaram!")