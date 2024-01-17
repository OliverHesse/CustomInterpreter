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
      if (self.current_char == "-" and self.peek().isdigit()) and (tokens[-1].type == "OP" or len(tokens) == 0):
        #accounts for cases like 2+-3
        self.current_char = self.get_next_char()
        current_num = int(self.current_char)

        while self.peek().isdigit():

          self.current_char = self.get_next_char()

          current_num = current_num * 10 + int(self.current_char)
        tokens.append(Token("INT", -current_num))
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
        tokens.append(Token("ClosedBracket", self.current_char))

      self.current_char = self.get_next_char()

    tokens.append(Token("EOF", None))
    return tokens

