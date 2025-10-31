import re

def generate_snippet(document_content: str, term: str, context_chars: int = 80) -> str:
    if not term or not document_content:
        return ""
    match = re.search(re.escape(term), document_content, re.IGNORECASE)
    if not match:
        return document_content[:context_chars * 2] + "..."

    start_pos, end_pos = match.start(), match.end()
    snippet_start = max(0, start_pos - context_chars)
    snippet_end = min(len(document_content), end_pos + context_chars)
    raw_snippet = document_content[snippet_start:snippet_end]
    
    highlighted = re.sub(f'({re.escape(term)})', r'<span class="highlight">\1</span>', raw_snippet, flags=re.IGNORECASE)
    
    prefix = "..." if snippet_start > 0 else ""
    suffix = "..." if snippet_end < len(document_content) else ""
    return f"{prefix}{highlighted}{suffix}"
