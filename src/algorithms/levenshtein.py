def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Menghitung Levenshtein distance antara dua string.
    Merupakan metrik untuk mengukur perbedaan antara dua urutan.
    """
    s1 = s1.lower()
    s2 = s2.lower()
    
    m, n = len(s1), len(s2)
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )
            
    return dp[m][n]

def find_most_similar(keyword: str, text: str, threshold: int = 2) -> list[str]:
    words = text.lower().split()
    similar_words = []
    
    for word in words:
        # Menghapus tanda baca umum dari kata
        cleaned_word = ''.join(filter(str.isalnum, word))
        if levenshtein_distance(keyword, cleaned_word) <= threshold:
            similar_words.append(cleaned_word)
            
    return list(set(similar_words))