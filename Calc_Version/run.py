import os
import time
from lexer import Token,Lexer,Interpreter
import sys

if __name__ == "__main__":
  read_file = sys.argv[1]
  
  show = False
  if len(sys.argv) > 2 and sys.argv[2] == "-show":
    show = True
  #main is run by using Start()
  #every line after this will be treated as a calculation
  #in future use = op to detect if they are trying to define variables and functions or to run them
  with open(read_file,"r") as file:
    data = file.read()
    lexer = Lexer(data).tokenize()
    #for i in range(0,len(lexer)):
      #print(f"({i}) {lexer[i]}")
    Interpreter(lexer,{},{},show).run()