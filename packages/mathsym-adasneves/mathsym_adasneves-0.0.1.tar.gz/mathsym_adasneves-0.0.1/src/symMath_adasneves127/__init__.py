

def create_eq(eq: str):
    import lexer, parse
    token_seq = lexer.tokenize(eq)
    root = parse.parse(token_seq)
    if root is None:
        raise TypeError("Root node not found.")
    return(root)