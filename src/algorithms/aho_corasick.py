from collections import deque

def build_trie(patterns):
    root = {'children': {}, 'fail': None, 'output': []}
    for pattern in patterns:
        node = root
        pattern_lower = pattern.lower()
        for char in pattern_lower:
            if char not in node['children']:
                node['children'][char] = {'children': {}, 'fail': None, 'output': []}
            node = node['children'][char]
        node['output'].append(pattern_lower)
    return root

def build_failure_links(root):
    queue = deque()
    for child in root['children'].values():
        child['fail'] = root
        queue.append(child)
    
    while queue:
        current_node = queue.popleft()
        for char, child in current_node['children'].items():
            fail_node = current_node['fail']
            while fail_node is not None and char not in fail_node['children']:
                fail_node = fail_node['fail']
            child['fail'] = fail_node['children'][char] if fail_node and char in fail_node['children'] else root
            child['output'] += child['fail']['output']
            queue.append(child)

def aho_corasick_search(text, patterns):
    root = build_trie(patterns)
    build_failure_links(root)

    results = []
    node = root
    text = text.lower()
    for index, char in enumerate(text):
        while node is not None and char not in node['children']:
            node = node['fail']
        if node is None:
            node = root
            continue
        node = node['children'][char]
        for match in node['output']:
            results.append({
                'pattern': match,
                'position': index - len(match) + 1
            })
    return results

if __name__ == "__main__":
    text = "This example shows how Aho-Corasick works for multi-pattern search."
    patterns = ["example", "aho", "corasick", "pattern", "search"]

    matches = aho_corasick_search(text, patterns)

    print("Matches found:")
    for match in matches:
        print(f"Pattern '{match['pattern']}' found at position {match['position']}")
