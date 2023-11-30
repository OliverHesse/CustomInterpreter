class Token():

  def __init__(self, type, value):
    self.value = value
    self.type = type

  def __str__(self):
    return f"Token({self.type},{self.value})"

  def __repr__(self) -> str:
    return self.__str__()


class lexer():

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

  def tokenize(self):
    op_dic = {"+": "PLUS", "-": "MINUS", "/": "DIV", "*": "MULTI"}
    tokens = []

    while self.current_char != "EOF":
      if self.current_char.isdigit():
        #i have encounterd a number, start creating a new num
        current_num = int(self.current_char)

        while self.peek().isdigit():

          self.current_char = self.get_next_char()

          current_num = current_num * 10 + int(self.current_char)

        tokens.append(Token("INT", current_num))
      if self.current_char in op_dic:
        #we have an operator
        tokens.append(Token("OP", self.current_char))
      if self.current_char == "(":
        tokens.append(Token("OpenBracket", self.current_char))
      if self.current_char == ")":
        tokens.append(Token("CloseBracket", self.current_char))

      self.current_char = self.get_next_char()

    tokens.append(Token("EOF", None))
    return tokens


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
            
          if self.current_token.type != "CloseBracket" and number_of_open != 0:
            new_tokens.append(self.current_token)
          
          if self.current_token.type == "CloseBracket":
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


if __name__ == "__main__":

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
