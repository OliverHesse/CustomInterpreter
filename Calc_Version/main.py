import os
import time
from lexer import Token,lexer

class Lexer():
  def __init__(self, text):
    self.text = text
    self.pos = 0
    self.current_char = text[0]
    
  def get_next_char(self):
    if self.pos + 1 >= len(self.text):
      return "EOF"
    else:
      self.pos += 1
      return self.text[self.pos]
    
  def peek(self):
    if self.pos + 1 > len(self.text) - 1:
      return "EOF"
    else:
      return self.text[self.pos + 1]
    
  def peekBehind(self):
    if self.pos -1 < 0:
      return None
    else:
      return self.text[self.pos - 1]
    
  def tokenize(self):
    op_dic = {"+": "PLUS", "-": "MINUS", "/": "DIV", "*": "MULTI"}
    tokens = []
    while self.current_char != "EOF":
      #first check if its a digit or -digit
      if self.current_char.isdigit() or (self.current_char == "-" and (self.peekBehind() in op_dic or self.peekBehind() is None)):
        num = self.current_char
        while self.peek().isdigit():
          self.current_char = self.get_next_char()
          num += self.current_char
       
        tokens.append(Token("INT",int(num)))
      elif self.current_char in op_dic:
        #this is an operator
        tokens.append(Token("OP", self.current_char))
      elif self.current_char == "(" or self.current_char == ")":
        bracket_map = {"(":"OpenBracket",")":"ClosedBracket"}
        tokens.append(Token(bracket_map[self.current_char], self.current_char))
      elif self.current_char == ",":
        tokens.append(Token("Separator",","))
      else:
        #found a general character will either be a variable or a function
        #end will either be an open bracket or an operator 
        current_value = self.current_char
        invalid_characters = {"(",")","EOF"}
        while self.peek() not in invalid_characters and self.peek() not in op_dic :
          self.current_char = self.get_next_char()
          current_value += self.current_char
        if self.peek() == "(":
          tokens.append(Token("Function",current_value))
        else:
          tokens.append(Token("Variable",current_value))

      self.current_char = self.get_next_char()
    tokens.append(Token("EOF", None))
    return tokens
class CalculatorInterpreter():
  def __init__(self,tokens,function_map):
    self.tokens = tokens
    self.pos = 0
    self.current_token = tokens[0]
    self.function_map = function_map
  def err(self, msg):
    raise Exception(msg)

  def get_next_token(self):

    if self.pos + 1 >= len(self.tokens):
      self.err("Index out of bounds")
    else:
      self.pos += 1
      return self.tokens[self.pos]

  def peek(self):
    if self.pos + 1 >= len(self.tokens):
      self.err("Index out of bounds")
    else:
      return self.tokens[self.pos + 1]
  def calculate(self):
    total = 0
    nums = []
    ops = []
    prio_dic = {
        "+": 2,
        "-": 2,
        "*": 1,
        "/": 1,
    }
    if self.current_token.type != "INT" and self.current_token.type != "OpenBracket" and self.current_token.type != "Function":
      self.err(
          f"Unexpected token at {self.pos} found {self.current_token} expected INT"
      )
    while self.current_token.type != "EOF":
      if self.current_token.type == "Function":
        function_name = self.current_token.value
        if self.peek().type != "OpenBracket":
          self.err(f"Unexpected token at {self.pos} expected (")
        parameters = []
        while self.current_token.type != "ClosedBracket":
          
          self.current_token = self.get_next_token()
          #does not allow for function parameters yet
          if self.current_token.type == "INT":
            parameters.append(self.current_token.value)
        #now i need to map parameters to variables
        function_tokens = self.function_map[function_name]["tokens"]
        
        function_params= self.function_map[function_name]["variables"]
        variable_map = {}
        
        for i in range(0,len(function_params)):
          variable_map[function_params[i]] = parameters[i]
        new_tokens = []
        for token in function_tokens:
          if token.type == "Variable":
            new_tokens.append(Token("INT", variable_map[token.value]))
          else:
            new_tokens.append(Token(token.type,token.value))
        new_interp = CalculatorInterpreter(new_tokens,self.function_map)
        
        nums.append(new_interp.calculate())
      elif self.current_token.type == "INT":
        nums.append(self.current_token.value)   
      elif self.current_token.type == "OP":
        ops.append(self.current_token.value)
      elif self.current_token.type == "OpenBracket":
        
        new_tokens = []
        number_of_open = 1
        
        while number_of_open != 0:

          self.current_token = self.get_next_token()
          
          if self.current_token.type == "OpenBracket":
            number_of_open += 1
            
          if self.current_token.type != "ClosedBracket" and number_of_open != 0:
            new_tokens.append(self.current_token)
          
          if self.current_token.type == "ClosedBracket":
            number_of_open -= 1
           
            if number_of_open != 0:
              new_tokens.append(self.current_token)
           
        new_tokens.append(Token("EOF", None))
       
        temp_interpreter = Interpreter(new_tokens)
        new_num = temp_interpreter.expr()

        nums.append(new_num)
      
      self.current_token = self.get_next_token()
    #calc everything
    for i in range(1, 3):
      count = 0
      
      if len(ops) == 0:
        break
        
      while count < len(ops):

        if count >= len(ops):
          break
          
        if prio_dic[ops[count]] == i:
          if ops[count] == "*":
            nums[count] = nums[count] * nums[count + 1]
          elif ops[count] == "+":
            nums[count] = nums[count] + nums[count + 1]
          elif ops[count] == "-":
            nums[count] = nums[count] - nums[count + 1]
          elif ops[count] == "/":
            nums[count] = nums[count] / nums[count + 1]
            
          ops.pop(count)
          nums.pop(count + 1)

          count -= 1

        count += 1

    return nums[0]


      
class Interpreter():

  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0
    self.current_token = tokens[0]

  def err(self, msg):
    raise Exception(msg)

  def get_next_token(self):

    if self.pos + 1 >= len(self.tokens):
      self.err("Index out of bounds")
    else:
      self.pos += 1
      return self.tokens[self.pos]

  def peek(self):
    if self.pos + 1 >= len(self.tokens):
      self.err("Index out of bounds")
    else:
      return self.tokens[self.pos + 1]

  def expr(self):
    
    nums = []
    ops = []
    prio_dic = {
        "+": 2,
        "-": 2,
        "*": 1,
        "/": 1,
    }
    if self.current_token.type != "INT" and self.current_token.type != "OpenBracket":
      self.err(
          f"Unexpected token at {self.pos} found {self.current_token} expected INT"
      )
    while self.current_token.type != "EOF":
      if self.current_token.type == "INT":
        nums.append(self.current_token.value)
        
      if self.current_token.type == "OP":
        ops.append(self.current_token.value)
  
      if self.current_token.type == "OpenBracket":
        new_tokens = []
        number_of_open = 1
        
        while number_of_open != 0:

          self.current_token = self.get_next_token()

          if self.current_token.type == "OpenBracket":
            number_of_open += 1
            
          if self.current_token.type != "ClosedBracket" and number_of_open != 0:
            new_tokens.append(self.current_token)
          
          if self.current_token.type == "ClosedBracket":
            number_of_open -= 1
           
            if number_of_open != 0:
              new_tokens.append(self.current_token)
              
        new_tokens.append(Token("EOF", None))
       
        temp_interpreter = Interpreter(new_tokens)
        new_num = temp_interpreter.expr()

        nums.append(new_num)
      self.current_token = self.get_next_token()

    for i in range(1, 3):
      count = 0
      
      if len(ops) == 0:
        break
        
      while count < len(ops):

        if count >= len(ops):
          break
          
        if prio_dic[ops[count]] == i:
          if ops[count] == "*":
            nums[count] = nums[count] * nums[count + 1]
          elif ops[count] == "+":
            nums[count] = nums[count] + nums[count + 1]
          elif ops[count] == "-":
            nums[count] = nums[count] - nums[count + 1]
          elif ops[count] == "/":
            nums[count] = nums[count] / nums[count + 1]
            
          ops.pop(count)
          nums.pop(count + 1)

          count -= 1

        count += 1

    return nums[0]


def mainLoop():
  global functions_map
  functions_map = {}
  while True:
    delay = 0
    text = input("(1)calculate (2)input function (3) view functions")
    if text == "1":
      delay = calculate()
    elif text == "2":
      delay = inputFunction()
    elif text == "3":
      delay = viewFunctions()
    else:
      print("please select a valid option")
      delay = 2
    
    time.sleep(delay)
    os.system('cls' if os.name == 'nt' else 'clear')
    delay = 0

def viewFunctions():
  for key,val in functions_map.items():
    
    expression = ""
    for token in val["tokens"]:
      expression += str(token.value)
    print(f"{key}({val['variables']}) = {expression}")
  input("enter to exit>")
  return 0
def calculate():
  while True:
    try:
      text = input("calc> ")
    except EOFError:
      return 0
    if text == "":
      return 0
    new_lexer = Lexer(text)
    new_interp = CalculatorInterpreter(new_lexer.tokenize(),functions_map)
    print(new_interp.calculate())

def inputFunction():
  function_name = input("func name> ")
  if function_name.find("(") != -1 or function_name.find(")") != -1 or function_name.find(" ") != -1 or function_name in functions_map or function_name.isdecimal():
    
    print("error invalid function name or already present")
    return 2
  variables = []
  done = False
  while done == False:
    new_variable = input("please enter the name of your variable")
    if new_variable.isdigit() and new_variable.find("(") != -1 and new_variable.find(")") != -1 and new_variable.find(" ") != -1 :
      print("error invalid variable name")
      return 2
    variables.append(new_variable)
    action = input("new variable? (y/n)")
    if action == "n":
      done = True

  contents = input(f"{function_name}({variables}) = " )
  #tokenize the contents
  #change tokenize to detect functions and variables 
  new_func = Lexer(contents).tokenize()
  functions_map[function_name] = {"variables":variables,"tokens":new_func}
  return 0    
if __name__ == "__main__":
  test_input = "2-3+-2/4+x-sin(4)"
  test_lexer = Lexer(test_input)
  print(test_lexer.tokenize())
  mainLoop()
  
  while True:
    try:
      text = input("calc> ")
    except EOFError:
      break
    new_lexer = lexer(text)
    tokens = new_lexer.tokenize()

    #print(tokens)
    interp = Interpreter(tokens)
    print(interp.expr())
