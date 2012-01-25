# -*- coding: utf-8 -*-
"""
    Programmēšanas valodu sintakse un semantika
    
    Miks Kalnins, mk09228.
"""
import re

#Base class for all symbols.
class SymbolBase:
    #Token name.
    id = None
    #Used by literals.
    value = None
    #Holds subexpressions.
    first = second = third = None
    #Translation string.
    translation = ""
    
    #Null denotation method, called when token is at the beggining of language
    #construct.
    def nud(self):
        raise SyntaxError("Syntax error (%r)." % self.id)
    
    #Left denotation method, called when token is inside language construct.
    def led(self, left):
        raise SyntaxError("Unknown operator (%r)." % self.id)
    #Recursively prints translation to AM language.
    def get_translation(self):        
        keys = ["first", "second", "third", "value", "first_value"]
        vals = [self.first, self.second, self.third]
        vals = [n.get_translation() if n else None for n in vals]
        vals.append(self.value)
        #Special case for ':=', probably not the best way to handle it,
        #but I don't think it's cheating since I do know the value of it.
        vals.append(self.first.value if self.first else None)
        
        result = {}
        for k, v in zip(keys, vals):
            result[k] = v

        return self.translation.format(**result)
    
    #Recursively prints prefix notation of underlaying symbol tree.
    def __repr__(self):
        if self.id == "(number)" or self.id == "(literal)":
            return "(%s %s)" % (self.id[1:-1], self.value)
        out = [self.id, self.first, self.second, self.third]
        out = map(str, filter(None, out))
        return "(" + " ".join(out) + ")"

#Class which holds all symbol types in the language.
class SymbolTable:
    #Contains all the symbol types.
    table = {}
    
    #Add (or update) a symbol to symbol table.
    def add(self, id, bp = 0):
        if id in self.table:
            s = self.table[id]
            self.update(id, bp)
        else:
            class s(SymbolBase):
                pass
            
            #Just for debug.
            s.__name__ = "<Symbol id=" + id + ">"
            
            s.id = id
            s.lbp = bp
            
            self.table[id] = s
        
        return s
    
    #Update binding power of a symbol type.    
    def update(self, id, bp):
        try:
            s = self.table[id]
        except KeyError:
            raise SyntaxError("No such symbol (%r)" % id)
        else:
            s.lbp = max(bp, s.lbp)
            
        return s
    
    #Get a specific symbol type by id.
    def get(self, id):
        try:
            s = self.table[id]
        except KeyError:
            raise SyntaxError("No such symbol (%r)" % id)
        else:
            return s
            
#Tokenizes string based on input regex.
class RegexTokenizer:
    def __init__(self, regex):
        self.regex = re.compile(regex, re.VERBOSE)
    
    #Returns generator which in returns token index and value.
    def get_tokens(self, text):
        matches = self.regex.finditer(text)
        for m in matches:
            yield m.lastindex, m.group(m.lastindex)
            