from insert import trie_node, compute_common_prefix
# "pera AND banana"
# -> trie_search(pera).index
#    .intersection(trie_search(banana).index)

def trie_search(t: trie_node, word: str) -> set[str]:
    if not word:
        return t.index
    
    for key, node in t.branches.items():
        common_prefix = compute_common_prefix(word, key)
        
        if common_prefix:
            print((key, node.index))
            word = word[len(common_prefix):]
            return trie_search(node, word)

    # a palavra existe mas não há prefixo comum
    return set()



if __name__ == '__main__':
    t = trie_node(
        index=set(),
        branches={
            'peter': trie_node({'t1'}, {}),
            'd': trie_node(set(), {
                'ampf': trie_node({'t2'}, {}),
                'onau': trie_node({'t3'}, {
                    'dampfschiff': trie_node({'t3'}, {
                        'ahrt': trie_node({'t3'}, {})
                    })
                })
            })
        }
    )
    
    assert(trie_search(t, 'açlkdjfaç') == set())
    assert(trie_search(t, 'donau') == {'t3'})
    assert(trie_search(t, 'dampf') == {'t2'})
    assert(trie_search(t, 'donaudampfschiffahrt') == {'t3'})
    print("✅ Todos os testes passaram")

