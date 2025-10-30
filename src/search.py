from src.insert import trie_node, compute_common_prefix


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

    # a palavra existe mas não há prefixo comum
    return set()


def corpus_search(t: trie_node, tokens: list[tuple[str, str]]):
    operator_stack = []
    set_stack: list[set[str]] = []

    def process(operator_stack, set_stack):
        s1 = set_stack.pop()
        s2 = set_stack.pop()

        if operator_stack.pop() == 'OR':
            set_stack.append(s1.union(s2))
        else:
            set_stack.append(s1.intersection(s2))


    for ttype, tvalue in tokens:
        if ttype == 'keyword':
            set_stack.append(trie_search(t, tvalue))

        if ttype == 'paren':
            if tvalue == '(':
                operator_stack.append(tvalue)
            else:
                while operator_stack[-1] != '(':
                    process(operator_stack, set_stack)
                operator_stack.pop()
                    
                    
        if ttype == 'operator':
            while (operator_stack and
                   operator_stack[-1] == 'AND' and
                   tvalue == 'OR'):
                process(operator_stack, set_stack)

                
            operator_stack.append(tvalue)

    # roda quando toda a entrada foi consumida
    while operator_stack:
        process(operator_stack, set_stack)
    return set_stack.pop()



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

    # Testes da busca no corpus

    p = search_tokenizer("dampf AND donau")
    assert(corpus_search(t, p) == set())

    p = search_tokenizer("dampf OR donau")
    assert(corpus_search(t, p) == {'t2', 't3'})


    p = search_tokenizer("dampf OR donau OR peter")
    assert(corpus_search(t, p) == {'t1', 't2', 't3'})

    # teste de precedência a direita
    p = search_tokenizer("dampf OR donau AND peter")
    assert(corpus_search(t, p) == {'t2'})

    # teste de precedência a esquerda
    p = search_tokenizer("donaudampfschiff AND donau OR peter")
    assert(corpus_search(t, p) == {'t3', 't1'})

    p = search_tokenizer("donaudampfschiff AND (donau OR peter)")
    assert(corpus_search(t, p) == {'t3'})

        # Teste 1: Parênteses aninhados complexos
    p = search_tokenizer("((dampf OR peter) AND (donau OR donaudampfschiffahrt))")
    assert(corpus_search(t, p) == set())
    
    # Teste 2: Múltiplos níveis de parênteses com diferentes operadores
    p = search_tokenizer("(dampf AND (donau OR peter)) OR donaudampfschiffahrt")
    assert(corpus_search(t, p) == {'t3'})  # dampf AND (donau OR peter) = vazio, OR donaudampfschiffahrt = t3
    
    # Teste 3: Parênteses mudando completamente a precedência
    p = search_tokenizer("dampf OR (donau AND peter)")
    assert(corpus_search(t, p) == {'t2'})  # donau AND peter = vazio, OR dampf = t2

    
    print("✅ Todos os testes passaram")

