import lexer, parse, tree_node

def create_eq(eq: str) -> tree_node.tree_node:
    
    token_seq = lexer.tokenize(eq)
    root = parse.parse(token_seq)
    if root is None:
        raise TypeError("Root node not found.")
    return(root)