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
                tokens.append(('keyword', word.lower()))
                
        # Caracteres não reconhecidos (podem ser tratados como parte de palavras)
        else:
            # Coletar sequência de caracteres não-espaço como palavra
            start = i
            while i < n and not search_str[i].isspace() and search_str[i] not in '()':
                i += 1
            word = search_str[start:i]
            tokens.append(('keyword', word))
    
    return tokens


def trie_search(t: trie_node, word: str) -> dict[str, int]:
    if not word:
        return set(t.postings.keys())
    
    for key, node in t.branches.items():
        if word.startswith(key):
            rest_of_word = word[len(key):]
            return trie_search(node, rest_of_word)

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
            postings_set = trie_search(t, tvalue)
            set_stack.append(postings_set.keys())

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
    # Para testar, precisamos importar as funções para construir a Trie
    from src.insert import trie, trie_insert

    # --- PASSO 1: Construir a Trie de Teste usando as funções reais ---
    print("Construindo Trie para testes...")
    t = trie()
    trie_insert(t, 'peter', 't1')
    trie_insert(t, 'dampf', 't2')
    trie_insert(t, 'donau', 't3')
    # Inserimos a mesma palavra de novo para testar a frequência
    trie_insert(t, 'donau', 't3') 
    trie_insert(t, 'donaudampfschiff', 't3')
    trie_insert(t, 'donaudampfschiffahrt', 't3')
    print("Trie de teste construída.")

    # --- PASSO 2: Testes da busca na trie (trie_search) CORRIGIDOS ---
    print("Testando trie_search...")
    assert(trie_search(t, 'açlkdjfaç') == {}) # Espera um dict vazio
    assert(trie_search(t, 'dampf') == {'t2': 1}) # Espera um dict com frequência
    assert(trie_search(t, 'donaudampfschiffahrt') == {'t3': 1})
    # A palavra 'donau' foi inserida 2 vezes para o arquivo 't3'
    assert(trie_search(t, 'donau') == {'t3': 2}) 

    # --- PASSO 3: Testes do tokenizer (NÃO MUDAM) ---
    print("Testando search_tokenizer...")
    assert search_tokenizer("chocolate AND leite") == [
        ('keyword', 'chocolate'), ('operator', 'AND'), ('keyword', 'leite')
    ]
    assert search_tokenizer("(chocolate OR baunilha) AND leite") == [
        ('paren', '('), ('keyword', 'chocolate'), ('operator', 'OR'), ('keyword', 'baunilha'),
        ('paren', ')'), ('operator', 'AND'), ('keyword', 'leite')
    ]
    # ... (os outros testes do tokenizer estão corretos e não precisam de mudança)

    # --- PASSO 4: Testes da busca no corpus (corpus_search) NÃO MUDAM ---
    print("Testando corpus_search...")
    p = search_tokenizer("dampf AND donau")
    assert(corpus_search(t, p) == set())

    p = search_tokenizer("dampf OR donau")
    assert(corpus_search(t, p) == {'t2', 't3'})

    p = search_tokenizer("dampf OR donau OR peter")
    assert(corpus_search(t, p) == {'t1', 't2', 't3'})

    p = search_tokenizer("donaudampfschiff AND (donau OR peter)")
    assert(corpus_search(t, p) == {'t3'})
    
    # Teste de precedência
    p = search_tokenizer("peter OR donau AND dampf") # AND tem precedência
    # (donau AND dampf) = {}, peter OR {} = {'t1'}
    assert(corpus_search(t, p) == {'t1'})

    print("✅ Todos os testes passaram com sucesso!")
