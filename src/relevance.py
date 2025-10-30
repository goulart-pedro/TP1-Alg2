import statistics
from typing import Dict, List, Set, Tuple
from .insert import trie_node
from .search import trie_search

def _traverse_trie(node: trie_node, prefix: str, word_stats: Dict[str, List[int]]):
    """percorre a trie e coleta frequencias de todas as palavras"""
    if node.postings:
        word_stats[prefix] = list(node.postings.values())

    for key, child_node in node.branches.items():
        _traverse_trie(child_node, prefix + key, word_stats)

def calculate_corpus_stats(trie: trie_node) -> Dict[str, Dict[str, float]]:
    
    word_frequencies = {}
    _traverse_trie(trie, "", word_frequencies)

    corpus_stats = {}
    for word, frequencies in word_frequencies.items():
        if len(frequencies) > 1:
            mean = statistics.mean(frequencies)
            stdev = statistics.stdev(frequencies)
        else:
            mean = frequencies[0] if frequencies else 0
            stdev = 0.0 # desvio padrão é 0 se só tem um valor
        
        corpus_stats[word] = {'mean': mean, 'stdev': stdev}
    
    return corpus_stats

def rank_by_relevance(
    doc_set: Set[str],
    query_terms: List[str],
    trie: trie_node,
    corpus_stats: Dict[str, Dict[str, float]]
) -> List[str]:
    if not doc_set:
        return []

    ranked_results: List[Tuple[str, float]] = []

    for doc_id in doc_set:
        z_scores = []
        for term in query_terms:
            postings = trie_search(trie, term)
            
            if postings and doc_id in postings:
                observed_freq = postings[doc_id]
                stats = corpus_stats.get(term)
                if not stats: continue

                mean_freq = stats['mean']
                stdev_freq = stats['stdev']

                if stdev_freq > 0:
                    z_score = (observed_freq - mean_freq) / stdev_freq
                else:
                    z_score = 1.0 if observed_freq > mean_freq else 0.0
                
                z_scores.append(z_score)

        if z_scores:
            avg_z_score = sum(z_scores) / len(z_scores)
            ranked_results.append((doc_id, avg_z_score))
        else:
            #relevancia zero
            ranked_results.append((doc_id, 0.0))

    ranked_results.sort(key=lambda item: item[1], reverse=True)
    
    return [doc for doc, score in ranked_results]