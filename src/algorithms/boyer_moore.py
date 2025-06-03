def build_bad_char_table(pattern):
    """Build bad character table for Boyer-Moore algorithm"""
    bad_char = {}
    m = len(pattern)
    
    # Fill the bad character table
    for i in range(m):
        bad_char[pattern[i]] = i
        
    return bad_char

def boyer_moore_search(text, pattern):
    """
    Boyer-Moore string searching algorithm
    Returns list of starting positions where pattern is found in text
    """
    if not pattern or not text:
        return []
    
    text = text.lower()
    pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)
    
    # Build bad character table
    bad_char = build_bad_char_table(pattern)
    
    matches = []
    s = 0  # shift of the pattern with respect to text
    
    while s <= n - m:
        j = m - 1
        
        # Keep reducing index j of pattern while characters match at this shift
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
            
        # If the pattern is present at current shift
        if j < 0:
            matches.append(s)
            
            # Shift the pattern so that the next character in text aligns with the last occurrence of it in pattern
            s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
        else:
            # Shift the pattern so that the bad character in text aligns with the last occurrence of it in pattern
            s += max(1, j - bad_char.get(text[s + j], -1))
            
    return matches

def boyer_moore_search_with_context(text, pattern, context_length=50):
    """
    Boyer-Moore search that returns matches with surrounding context
    """
    matches = boyer_moore_search(text, pattern)
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
