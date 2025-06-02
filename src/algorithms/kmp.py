def build_lps_array(pattern):
    """Build Longest Proper Prefix which is also Suffix array for KMP algorithm"""
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of the previous longest prefix suffix
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    """
    Knuth-Morris-Pratt string searching algorithm
    Returns list of starting positions where pattern is found in text
    """
    if not pattern or not text:
        return []
    
    text = text.lower()
    pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)
    
    # Build LPS array
    lps = build_lps_array(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
            
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
                
    return matches

def kmp_search_with_context(text, pattern, context_length=50):
    """
    KMP search that returns matches with surrounding context
    """
    matches = kmp_search(text, pattern)
    results = []
    
    for match_pos in matches:
        start = max(0, match_pos - context_length)
        end = min(len(text), match_pos + len(pattern) + context_length)
        context = text[start:end]
        
        results.append({
            'position': match_pos,
            'context': context,
            'match': pattern
        })
    
    return results
