class Token():

  def __init__(self, type, value):
    self.value = value
    self.type = type

  def __str__(self):
    return f"Token({self.type},{self.value})"

  def __repr__(self) -> str:
    return self.__str__()

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
      elif self.current_char == "\n":
        tokens.append(Token("EOL",None))
      elif self.current_char == "=":
        tokens.append(Token("Set","="))
      else:
        #found a general character will either be a variable or a function
        #end will either be an open bracket or an operator 
        
        invalid_characters = {"(",")","EOF","EOL"," ",",","\n"}
        current_value = self.current_char
        if self.current_char in invalid_characters:
          self.current_char = self.get_next_char()
          continue
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
  
class Interpreter():
  def __init__(self,tokens,function_map,variable_map,show = False):
    self.tokens = tokens
    self.pos = 0
    self.current_token = tokens[0]
    self.function_map = function_map
    self.variable_map = variable_map
    self.show = show
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
  def run(self):
    #determines if a line is calculate or set
    #run until end of file
    while self.current_token.type != "EOF":
      current_pos = self.pos
      
      #run to the end of the line looking for set
     
      isSet = False
      while self.current_token.type != "EOL" and self.current_token.type != "EOF":
        
        if self.current_token.type == "Set":
          isSet = True
          
        self.current_token = self.get_next_token()
      if self.current_token.type != "EOF":
        self.current_token = self.get_next_token()
      if isSet: 
        
        self.pos = current_pos
        self.current_token = self.tokens[self.pos]
        
        self.set()
        if self.current_token.type != "EOF":
          self.current_token = self.get_next_token()
      else:
        
        self.pos = current_pos
        self.current_token = self.tokens[self.pos]
        self.pos = current_pos
        num = self.calculate(self.show)
        if self.current_token.type != "EOF":
          self.current_token = self.get_next_token()
        print(num)
  def set(self):

    set_type = None
    #False is finding set_type
    #True is finding expr
    state = self.current_token.type
    #function is stored as 
    #map[func_name] = {parameters:[parameters names],tokens:[Tokens]}
    #variable stored as
    #map[variable name] = variable value
    
    if state == "Function":
      #get parameters
  
      function_name = self.current_token.value
      comma_found = 0
      params = []
      
      while self.current_token.type != "Set":

        if self.current_token.type == "Variable":
          params.append(self.current_token.value)

        if self.current_token.type == "Separator":
          comma_found += 1
        self.current_token = self.get_next_token()
      if len(params)-1 != comma_found:
        self.err(f"error parsing parameters for function {function_name}")

      self.current_token = self.get_next_token()
      tokens = []
      
      while self.current_token.type != "EOL" and self.current_token.type != "EOF":
        tokens.append(self.current_token)
        self.current_token = self.get_next_token()
      self.function_map[function_name] = {"params":params[:],"tokens":tokens}
    elif state == "Variable":

      variable_name = self.current_token.value
      self.current_token = self.get_next_token()
      if self.current_token.type != "Set":
        self.err(f"expecting = after {variable_name} instead found {self.current_token.value}")

      self.current_token = self.get_next_token()
      tokens = []
      while  self.current_token.type != "EOL" and self.current_token.type != "EOF":
        tokens.append(self.current_token)
        self.current_token = self.get_next_token()
      
      tokens.append(Token("EOL",None))
      value = Interpreter(tokens,self.function_map,self.variable_map).calculate()
      self.variable_map[variable_name] = value

    else:
      self.err("expecting function or variable declaration")
    
      
  def calculate(self,show = False):

    total = 0
    nums = []
    ops = []
    prio_dic = {
        "+": 2,
        "-": 2,
        "*": 1,
        "/": 1,
    }
    if self.current_token.type != "INT" and self.current_token.type != "OpenBracket" and self.current_token.type != "Function" and self.current_token.type != "Variable":
      self.err(
          f"Unexpected token at {self.pos} found {self.current_token} expected INT"
      )
    #for if the -show flag is provided
    reset_pos = self.pos
    while self.current_token.type != "EOF" and self.current_token.type != "EOL":

      if self.current_token.type == "Function":
        function_name = self.current_token.value
        if self.peek().type != "OpenBracket":
          self.err(f"Unexpected token at {self.pos} expected (")
        parameters = []
        self.current_token = self.get_next_token()
        while self.current_token.type != "ClosedBracket":
          #skips the open bracket
          
          self.current_token = self.get_next_token()
          current_expr = []
          open_brackets_found = 1
          while (self.current_token.type != "Separator" or open_brackets_found > 1) and open_brackets_found != 0:
            if self.current_token.type == "OpenBracket":
              open_brackets_found += 1
            if self.current_token.type == "ClosedBracket":
              open_brackets_found -= 1
              if open_brackets_found == 0:
                break
            current_expr.append(self.current_token)
            self.current_token = self.get_next_token()
         
          #create new interp object to evaluate
          current_expr.append(Token("EOF",None))
          parameters.append(Interpreter(current_expr,self.function_map,self.variable_map).calculate())
          
        #now i need to map parameters to variables
        function_tokens = self.function_map[function_name]["tokens"]
        
        function_params= self.function_map[function_name]["params"]
        variable_map = {}
        
        for i in range(0,len(function_params)):
          variable_map[function_params[i]] = parameters[i]
        new_tokens = []
        for token in function_tokens:
          if token.type == "Variable":
            new_tokens.append(Token("INT", variable_map[token.value]))
          else:
            new_tokens.append(Token(token.type,token.value))
        new_tokens.append(Token("EOL",None))
        new_interp = Interpreter(new_tokens,self.function_map,self.variable_map)
        
        nums.append(new_interp.calculate())
      elif self.current_token.type == "INT":
        nums.append(self.current_token.value)   
      elif self.current_token.type == "OP":
        ops.append(self.current_token.value)
      elif self.current_token.type == "OpenBracket":
        
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
       
        temp_interpreter = Interpreter(new_tokens,self.function_map,self.variable_map)
        new_num = temp_interpreter.calculate()

        nums.append(new_num)
      elif self.current_token.type == "Variable":
        nums.append(self.variable_map[self.current_token.value])
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
    expr_string = ""
    
    if show == True:
      self.pos = reset_pos
      self.current_token = self.tokens[self.pos]
      while self.current_token.type != "EOF" and self.current_token.type != "EOL":
        
        expr_string += str(self.current_token.value)
        self.current_token = self.get_next_token()

      return f"{expr_string} = {nums[0]}"
    return nums[0]
