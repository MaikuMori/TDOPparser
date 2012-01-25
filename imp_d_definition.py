# -*- coding: utf-8 -*-
"""
    Programmēšanas valodu sintakse un semantika
    
    Miks Kalnins, mk09228.
"""
from my_parser import SymbolTable, RegexTokenizer

symbol_table = SymbolTable()

#Just playing around with what's possible with regex based tokenizer,
#the implementation doesn't neccessary depend on tokenizer being able to
#assign types to tokens.

tokenizer = RegexTokenizer(r"""
(skip|if|then|else|fi|while|do|od|:=|\;)|   # CONSTANT
(>=|<=|!=|<|>|\!|\=|and|or|\*\*)|           # BOOLEAN OPERATOR   
(\*|\+|\-|\/|\)|\()|                        # OPERATOR            
(true|false)|                               # BOOLEAN
([0-9]+)|                                   # NUMBER                    
([a-zA-Z]+)|                                # LITERAL
(\s|\n|\t)                                  # WHITESPACE
""")

#Token type lookup table.
class TokenType:
    CONSTANT = 1
    BOPERATOR = 2
    OPERATOR = 3
    BOOLEAN = 4
    NUMBER = 5
    LITERAL = 6
    WHITESPACE = 7

#Given token and token type choses matching simbol.
def tokenize(program):
    for id, value in tokenizer.get_tokens(program):
        if id == TokenType.WHITESPACE:
            continue
        elif id == TokenType.LITERAL:
            symbol = symbol_table.get("(literal)")
            s = symbol()
            s.value = value
        elif id == TokenType.NUMBER:
            symbol = symbol_table.get("(number)")
            s = symbol()
            s.value = int(value)
        else:
            symbol = symbol_table.get(value)
            if symbol:
                s = symbol()
            s.value = value
        yield s
    symbol = symbol_table.get("(end)")
    yield symbol()

#The real parse function.
def expression(rbp=0):
    global token
    t = token
    token = next(next_token)
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next(next_token)
        left = t.led(left)
    return left

#Entry point.
def parse(program):
    global token, next_token
    next_token = tokenize(program)
    token = next(next_token)
    return expression()

#Check if current token matches given string and if yes,
#advance to next token.
def advance(id=None):
    global token
    if id and token.id != id:
       raise SyntaxError("Expected %r" % id)
    token = next(next_token)

#Helper functions to help defining infix operators.
def infix(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp)
        return self
    symbol_table.add(id, bp).led = led
    
def infix_r(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp - 1)
        return self
    symbol_table.add(id, bp).led = led

#Helper function to help defining prefix operators.    
def prefix(id, bp):
    def nud(self):
        self.first = expression(bp)
        self.second = None
        return self
    symbol_table.add(id).nud = nud
    

#Defining most symbols and their binding power.
prefix("!", 30)
infix("<", 35); infix("<=", 35)
infix(">", 35); infix(">=", 35)
infix("!=", 35); infix("=", 35)
infix("and", 35); infix("or", 35)

infix("+", 40); infix("-", 40)
infix("*", 50); infix("/", 50)
prefix("+", 100); prefix("-", 100)
infix_r("**", 120)
infix(":=", 30)
infix(";", 10)


#Skip and literals don't bond with other tokens. Same with special end token.
def nud(self):
    return self
symbol_table.add("skip").nud = nud
symbol_table.add("(literal)").nud = nud
symbol_table.add("(number)").nud = nud
symbol_table.add("(end)")

#Special handling for if statements.
def nud(self):
    self.first = expression(20)
    advance("then")
    self.second = expression(20)
    #Seems like for now we always have else.
    # if token.id == "else":
        # advance("else")
        # self.third = expression(20)
    advance("else")
    self.third = expression(20)
    advance("fi")
    return self
    
symbol_table.add("if", 20).nud = nud
symbol_table.add("then")
symbol_table.add("else")
symbol_table.add("fi")

#Special handling for while loops.
def nud(self):
    self.first = expression(20)
    advance("do")
    self.second = expression(20)
    advance("od")
    return self

symbol_table.add("while", 20).nud = nud
symbol_table.add("do")
symbol_table.add("od")

#Binary true and false.
symbol_table.add("true")
symbol_table.add("false")

#Brackets
def nud(self):
    expr = expression()
    advance(")")
    return expr
    
symbol_table.add("(").nud = nud
symbol_table.add(")")

#Add translation for each node.
symbol_table.get("+").translation = "{second} {first} ADD"
symbol_table.get("-").translation = "{second} {first} SUB"
symbol_table.get("*").translation = "{second} {first} MULT"
symbol_table.get("/").translation = "{second} {first} DIV"
symbol_table.get("true").translation = "TRUE"
symbol_table.get("false").translation = "FALSE"
symbol_table.get("=").translation = "{second} {first} EQ"
symbol_table.get("<=").translation = "{second} {first} LE {second} {first} EQ OR"
symbol_table.get(">=").translation = "{second} {first} LE NEG {second} {first} EQ OR"
symbol_table.get("!=").translation = "{second} {first} EQ NEG"
symbol_table.get("<").translation = "{second} {first} LE"
symbol_table.get(">").translation = "{second} {first} LE NEG"
symbol_table.get("!").translation = "{first} NEG"
symbol_table.get("and").translation = "{second} {first} AND"
symbol_table.get("or").translation = "{second} {first} OR"

symbol_table.get("skip").translation = "NOOP"
symbol_table.get(":=").translation = "{second} STORE({first_value})"
symbol_table.get(";").translation = "{first} {second}"
symbol_table.get("if").translation = "{first} BRANCH({second}, {third})"
symbol_table.get("while").translation = "LOOP({first}, {second})"

symbol_table.get("(literal)").translation = "FETCH({value})"
symbol_table.get("(number)").translation = "PUSH{value}"

print(parse("""
while !(x=y) do
    if x <= y then
        y:=y-x
    else
        x:=x-y
    fi
od
""").get_translation())