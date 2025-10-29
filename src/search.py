from insert import trie_node, compute_common_prefixrt import tur
# "pera AND banana"
# -> trie_search(pera).index
#    .intersection(trie_search(banana).index)


def search_tokenizer(search_str: str):
    tokens = []
    i = 0
    n = len(search_str)
    
    while i < n:
        char = search_str[i]
        
        # Ignorar espaços em branco
        if char.isspace():
            i += 1
            continue
            
        # Parêntese esquerdo
        elif char == '(':
            tokens.append(('paren', '('))
            i += 1
            
        # Parêntese direito
        elif char == ')':
            tokens.append(('paren', ')'))
            i += 1
            
        # Operadores AND/OR
        elif char.isalpha():
            # Coletar a palavra completa
            start = i
            while i < n and search_str[i].isalpha():
                i += 1
            word = search_str[start:i]
            
            if word.upper() in ('AND', 'OR'):
                tokens.append(('operator', word.upper()))
            else:
                tokens.append(('keyword', word))
                
        # Caracteres não reconhecidos (podem ser tratados como parte de palavras)
        else:
            # Coletar sequência de caracteres não-espaço como palavra
            start = i
            while i < n and not search_str[i].isspace() and search_str[i] not in '()':
                i += 1
            word = search_str[start:i]
            tokens.append(('keyword', word))
    
    return tokens



def trie_search(t: trie_node, word: str) -> set[str]:
    if not word:
        return t.index
    
    for key, node in t.branches.items():
        common_prefix = compute_common_prefix(word, key)
        
        if common_prefix:
            word = word[len(common_prefix):]
            return trie_search(node, word)

    # a palavra existe mas não há prefixo comumroots
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

    # Testes da busca na trie
    assert(trie_search(t, 'açlkdjfaç') == set())
    assert(trie_search(t, 'donau') == {'t3'})
    assert(trie_search(t, 'dampf') == {'t2'})
    assert(trie_search(t, 'donaudampfschiffahrt') == {'t3'})

    # Testes do tokenizer
    assert search_tokenizer("chocolate AND leite") == [
        ('keyword', 'chocolate'),
        ('operator', 'AND'),
        ('keyword', 'leite')
    ]

    assert search_tokenizer("(chocolate OR baunilha) AND leite") == [
        ('paren', '('),
        ('keyword', 'chocolate'),
        ('operator', 'OR'),
        ('keyword', 'baunilha'),
        ('paren', ')'),
        ('operator', 'AND'),
        ('keyword', 'leite')
    ]

    # Testes adicionais
    assert search_tokenizer("chocolate OR (baunilha AND leite)") == [
        ('keyword', 'chocolate'),
        ('operator', 'OR'),
        ('paren', '('),
        ('keyword', 'baunilha'),
        ('operator', 'AND'),
        ('keyword', 'leite'),
        ('paren', ')')
    ]

    assert search_tokenizer("((a OR b) AND c)") == [
        ('paren', '('),
        ('paren', '('),
        ('keyword', 'a'),
        ('operator', 'OR'),
        ('keyword', 'b'),
        ('paren', ')'),
        ('operator', 'AND'),
        ('keyword', 'c'),
        ('paren', ')')
    ]

    assert search_tokenizer("chocolate AND leite OR baunilha") == [
        ('keyword', 'chocolate'),
        ('operator', 'AND'),
        ('keyword', 'leite'),
        ('operator', 'OR'),
        ('keyword', 'baunilha')
    ]

    assert search_tokenizer("chocolate") == [
        ('keyword', 'chocolate')
    ]

    assert search_tokenizer("(chocolate)") == [
        ('paren', '('),
        ('keyword', 'chocolate'),
        ('paren', ')')
    ]

    print("✅ Todos os testes passaram")

