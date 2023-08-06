from typing import List

class token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
        
        
class tree_node:
    def __init__(self, type, value, precedence):
        self.value = value
        self.type = type
        self.prec = precedence
        self.parent: None | tree_node = None
        self.left_child: None | tree_node  = None
        self.right_child: None | tree_node = None
        
    def print(self):
        if self.left_child is None or self.right_child is None:
            print(self.value, end="")
            return
        else:
            print("(", end="")
            self.left_child.print()
            print(self.value, end="")
            self.right_child.print()
            print(")", end="")
            
    def evaluate(self, x: int) -> int | float:
        if self.left_child is None and self.right_child is None:
            if self.type == "VARIABLE":
                return x
            return float(self.value)
        else:
            left_result = self.left_child.evaluate(x)
            right_result = self.right_child.evaluate(x)
            
            match self.type:
                case "PLUS":
                    return left_result + right_result
                case "MINUS":
                    return left_result - right_result
                case "MULTIPLICATION":
                    return left_result * right_result
                case "DIVISION":
                    return left_result / right_result
                case "EXPONENT":
                    return left_result ** right_result
                case other:  # noqa: F841
                    return 0
            

def tokenize(equation_code: str) -> List[token]:
    token_list: List[token] = []
    
    while equation_code != "":
        char = equation_code[0]
        match char:
            case "+":
                token_list.append(token("PLUS", "+"))
            case "-":
                token_list.append(token("MINUS", "-"))   
            case "(":
                token_list.append(token("LPAREN", "("))     
            case ")":
                token_list.append(token("RPAREN", ")"))
            case "*":
                token_list.append(token("MULTIPLICATION", "*"))
            case "/":
                token_list.append(token("DIVISION", "/"))
            case "^":
                token_list.append(token("EXPONENT", "^"))
            case "x":
                token_list.append(token("VARIABLE", "x"))
        if char.isdigit() or char == ".":
            numbStr = "" if char != "." else "0"
            while char.isdigit() or char == ".":
                numbStr += char
                if len(equation_code) > 1 and (equation_code[1].isdigit() or \
                                               equation_code[1] == "."):
                    equation_code = equation_code[1:]
                else:
                    break

                if equation_code == "":
                    char == "" # type: ignore
                else:
                    char = equation_code[0]
            try:
                float(numbStr)
            except ValueError:
                print("Error: Invalid Number!")
                exit()
            
            newToken = token("NUMBER", numbStr)
            token_list.append(newToken)
        equation_code = equation_code[1:]
    
    return token_list
    

def create_eq(eq: str) -> tree_node:
    
    token_seq = tokenize(eq)
    root = parse(token_seq)
    if root is None:
        raise TypeError("Root node not found.")
    return(root)


def get_prec(type: str) -> int:
    prec = 0
    if type == "PLUS" or type == "MINUS":
        prec = 1
    elif type == "MULTIPLICATION" or type == "DIVISION":
        prec = 2
    elif type == "EXPONENT":
        prec = 3
    return prec

def create_tree_list(token_list: List[token]):
    node_list: List[tree_node] = []
    global_prec = 0
    for token in token_list:
        if token.type == "LPAREN":
            global_prec += 4
        elif token.type == "RPAREN":
            global_prec -= 4
        else:
            new_node = tree_node(token.type, token.value, get_prec(token.type) + \
                global_prec)
            node_list.append(new_node)
    return node_list

def parse(token_list: List[token]):
    rootNode = None
    treeNodeList = create_tree_list(token_list)
    create_tree(treeNodeList)
    rootNode = findRoot(treeNodeList)
    return rootNode



def link_nodes(parent: tree_node, left: tree_node | None = None, \
    right: tree_node | None = None):
    
    parent.left_child = left or parent.left_child
    parent.right_child = right or parent.right_child
    
    if right is not None:
        right.parent = parent
    if left is not None:
        left.parent = parent
        
        
        
def create_neg_one():
    minus = tree_node("MINUS", "-", 10)
    mult = tree_node("MULTIPLICATION", "*", 10)
    
    link_nodes(minus, tree_node("NUMBER", "0", 0), tree_node("NUMBER", "1", 0))
    
    link_nodes(mult, minus)
    
    return mult

def create_neg():
    # Create a tree that represents -1 * n.
    minus = tree_node("MINUS", "-", 10)
    mult = tree_node("MULTIPLICATION", "*", 10)
    
    link_nodes(minus, tree_node("NUMBER", "0", 0), tree_node("NUMBER", "1", 0))
    
    link_nodes(mult, minus, tree_node("DUMMY", "n", 0))
    
    return mult
    
def create_doub_neg():
    # Create a tree that represents -1 * -1.
    neg_one = create_neg()
    neg_two = create_neg()
    link_nodes(neg_one, right = neg_two)
    
    
def create_tree(node_list: List[tree_node]):
    dummy_node = tree_node("DUMMY", "", 0)
    node_list.insert(0, dummy_node)
    node_list.append(dummy_node)
    for index, node in enumerate(node_list):
        
        if node.type == "NUMBER" and node_list[index + 1].type == "VARIABLE":
            node_list.insert(index + 1, tree_node("MULTIPLICATION", "*", node.prec + 2))
        
        
        if node.type == "NUMBER" or node.type == "VARIABLE":
            prev_op = node_list[index - 1]
            next_op = node_list[index + 1]
            
                
            
            if next_op.prec > prev_op.prec:
                next_op.left_child = node
                node.parent = next_op
                if prev_op.type != "DUMMY":
                    prev_op.right_child = next_op
                    next_op.parent = prev_op
            else:
                prev_op.right_child = node
                node.parent = prev_op
                
                if next_op.type != "DUMMY":
                    while prev_op.parent is not None:
                        if prev_op.parent.prec < next_op.prec:
                            break
                        prev_op = prev_op.parent
                    if prev_op.parent is not None:
                        prev_op.parent.right_child = next_op
                        next_op.parent = prev_op.parent
                    next_op.left_child = prev_op
                    prev_op.parent = next_op
                    
def findRoot(treeNodeList):
    rootNode = None
    for node in treeNodeList:
        if (node.parent is not None and node.parent.type == "DUMMY") or \
            (node.parent is None and node.type != "DUMMY"):
            rootNode = node
            break
    return rootNode
            
