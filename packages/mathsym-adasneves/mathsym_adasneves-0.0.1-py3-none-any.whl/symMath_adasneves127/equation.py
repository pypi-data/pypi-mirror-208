from lexer import tokenize

class equation:
    def __init__(self, eq):
        self.eq = eq
        self.token_list = tokenize(eq)
        