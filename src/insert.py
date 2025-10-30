from dataclasses import dataclass, field

@dataclass
class trie_node:
    postings: dict[str, int] = field(default_factory=dict)
    branches: dict[str, 'trie_node'] = field(default_factory=dict)

def trie() -> trie_node:
    return trie_node()

def compute_common_prefix(w1: str, w2: str) -> str:
    common_prefix = ""
    for i in range(min(len(w1), len(w2))):
        if w1[i] != w2[i]:
            break
        common_prefix += w1[i]
    return common_prefix

def trie_insert(root: trie_node, word: str, filename: str):
    if not word:
        root.postings[filename] = root.postings.get(filename, 0) + 1
        return

    for key, child_node in list(root.branches.items()):
        if word.startswith(key):
            rest_of_word = word[len(key):]
            trie_insert(child_node, rest_of_word, filename)
            return

    for key, child_node in list(root.branches.items()):
        common_prefix = compute_common_prefix(word, key)
        if common_prefix:
            rest_of_key = key[len(common_prefix):]
            rest_of_word = word[len(common_prefix):]
            root.branches.pop(key)
            intermediate_node = trie_node()
            intermediate_node.branches[rest_of_key] = child_node
            root.branches[common_prefix] = intermediate_node
            trie_insert(intermediate_node, rest_of_word, filename)
            return
            
    new_node = trie_node()
    root.branches[word] = new_node
    trie_insert(new_node, "", filename)