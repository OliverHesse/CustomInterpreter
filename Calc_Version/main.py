PLUS, MINUS, MULT, DIV, INT, EOF = "PLUS", "MINUS", "MULT", "DIV", "INT", "EOF"

operators = {"*":"*","/":"/","+":"+","-":"-"}
class Token():

  def __init__(self, type, value):
    self.type = type
    self.value = value


class Interpreter():

  def __init__(self, text):
    self.text = text.replace(" ","")
    self.pos = 0
    self.current_token = None

  def peek(self):
    text = self.text
    if self.pos+1 > len(text) - 1:
      #stand in for EOF
      return "EOF"
    
    current_char = text[self.pos+1]

    if current_char.isdigit():
      token = current_char
      self.pos += 1
      return token
    if current_char == "+":
      self.pos += 1
      return "OP"
    elif current_char == "-":
      self.pos += 1
      return "OP"
    elif current_char == "*":
      self.pos += 1
      return "OP"
    elif current_char == "/":
      self.pos += 1
      return "OP"
  def err(self, message):
    raise Exception(message)

  def get_next_token(self):
    text = self.text
    if self.pos > len(text) - 1:
      return Token(EOF, None)
    current_char = text[self.pos]

    if current_char.isdigit():
      token = Token(INT, int(current_char))
      self.pos += 1
      return token
    if current_char == "+":
      self.pos += 1
      return Token(PLUS, current_char)
    elif current_char == "-":
      self.pos += 1
      return Token(MINUS, current_char)
    elif current_char == "*":
      self.pos += 1
      return Token(MULT, current_char)
    elif current_char == "/":
      self.pos += 1
      return Token(DIV, current_char)
    self.err(f"Invalid syntax at char {self.pos}, found {current_char}")
  def eat(self,token_type):
    #checks the type of retrieved token
    #if they match we increment the current node
    if self.current_token.type == token_type:
      self.current_token = self.get_next_token()
    else:
      self.err("unexpected token")

  def expr(self):
    #retrieves the first character
    self.current_token = self.get_next_token()
    nums = []
    ops = []
    while self.current_token.type != "EOF":
        c_type = self.current_token.type
        
        if c_type == INT:
            current_num = self.current_token.value
            self.eat(INT)
            while self.current_token.type == INT:
                
                current_num = current_num*10 + self.current_token.value
                self.eat(INT)
                
            nums.append(current_num)

            
        
        elif c_type == PLUS or c_type == MINUS or c_type == MULT or c_type == DIV:
            ops.append(self.current_token.value)
            self.current_token = self.get_next_token()
        else:
            self.err(f"Encounterd an unkown character at {self.pos}")
    #i know have a list of nums and ops
    op_order = ["*","/","+","-"]
    prio_dic = {
        "+" : 2,
        "-" : 2,
        "*" : 1,
        "/" : 1,
    }
    for i in range(1,3):
        count = 0
        if len(ops) == 0:
           break
        while count < len(ops):

            if count >= len(ops):
              break
            if prio_dic[ops[count]] == i:
                if ops[count] == "*":
                    nums[count] = nums[count]*nums[count+1]
                elif ops[count] == "+":
                    nums[count] = nums[count]+nums[count+1]
                elif ops[count] == "-":
                    nums[count] = nums[count]-nums[count+1]
                elif ops[count] == "/":
                    nums[count] = nums[count]/nums[count+1]
                ops.pop(count)
                nums.pop(count+1)
                
                count -= 1
                
            count+=1
    
    return nums[0]
if __name__ == "__main__":
  while True:
    try:
      text = input("calc> ")
    except EOFError:
      break
    interpreter = Interpreter(text)
    result = interpreter.expr()
    print(result)