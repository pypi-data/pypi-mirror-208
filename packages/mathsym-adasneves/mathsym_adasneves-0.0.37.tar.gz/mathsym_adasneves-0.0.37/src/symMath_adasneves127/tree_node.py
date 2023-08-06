from eq_token import token
from typing import Dict
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
        if self.left_child == None and self.right_child == None:
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
                case other:
                    return 0
            