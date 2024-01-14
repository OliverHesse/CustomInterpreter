from lexer import Token,lexer


if __name__ == "__main__":
    myLexer = lexer("2+2")
    print(myLexer.tokenize())
    print("here")
