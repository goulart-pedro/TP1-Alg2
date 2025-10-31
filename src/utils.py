import re
from typing import List, Dict
from .insert import trie_node
from .search import trie_search

def generate_snippet(
    document_content: str, 
    center_term: str, 
    all_terms: List[str], 
    context_chars: int = 80
) -> str:
    """
    Gera um snippet centralizado no 'center_term', destacando todos os 'all_terms'
    apenas como palavras inteiras (não substrings).
    """
    if not center_term:
        center_term = all_terms[0] if all_terms else ""
        if not center_term: return document_content[:context_chars*2] + "..."

  
    center_pattern = r'(^|\W)(' + re.escape(center_term) + r')(\W|$)'
    match = re.search(center_pattern, document_content, re.IGNORECASE)
    
    if not match:
        return document_content[:context_chars * 2] + "..."
    
    start_pos = match.start(2)
    end_pos = match.end(2)

    snippet_start = max(0, start_pos - context_chars)
    snippet_end = min(len(document_content), end_pos + context_chars)
    raw_snippet = document_content[snippet_start:snippet_end]
    
    terms_pattern = "|".join(re.escape(term) for term in all_terms if term)
    
    if terms_pattern:
        highlight_pattern = r'(^|\W)(' + terms_pattern + r')(\W|$)'
        highlighted = re.sub(highlight_pattern, r'\1<b>\2</b>\3', raw_snippet, flags=re.IGNORECASE)
    else:
        highlighted = raw_snippet
    
    prefix = "..." if snippet_start > 0 else ""
    suffix = "..." if snippet_end < len(document_content) else ""
    return f"{prefix}{highlighted}{suffix}"


def find_best_term_for_snippet(
    doc_id: str,
    query_terms: List[str],
    trie: trie_node,
    corpus_stats: Dict[str, Dict[str, float]]
) -> str:
    best_term = ""
    max_z_score = -float('inf')

    if not query_terms:
        return ""

    for term in query_terms:
        postings = trie_search(trie, term)
        
        if postings and doc_id in postings:
            observed_freq = postings[doc_id]
            stats = corpus_stats.get(term)

            if not stats: continue

            mean_freq, stdev_freq = stats['mean'], stats['stdev']

            if stdev_freq > 0:
                z_score = (observed_freq - mean_freq) / stdev_freq
            else:
                z_score = 1.0 if observed_freq > mean_freq else 0.0
            
            if z_score > max_z_score:
                max_z_score = z_score
                best_term = term

    return best_term if best_term else query_terms[0]