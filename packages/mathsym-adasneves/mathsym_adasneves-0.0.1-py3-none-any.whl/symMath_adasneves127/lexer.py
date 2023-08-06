from eq_token import token
from typing import List

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
                if len(equation_code) > 1 and (equation_code[1].isdigit() or equation_code[1] == "."):
                    equation_code = equation_code[1:]
                else:
                    break

                if equation_code == "":
                    char == ""
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
    
if __name__ == "__main__":
    x = tokenize("51.2^x")
    
    print([(y.type, y.value) for y in x])
    
    