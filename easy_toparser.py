
# easy_toparser.py

from __future__ import print_function

import time

from easy_grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Assign, Execute, New, Style
from easy_symbols import Symbol, initSymbols
from easy_lexer import quoteString
from easy_output import Output

# --------------------------------------------------------------------------

class ToParser (Output) :

   def addToDictionary (self, tree, name) :
       ref = tree
       for c in name :
           if c not in ref :
               ref[c] = { }
           ref = ref[c]

   def prindKeywordItem (self, dictionary, inx, name) :
       self.incIndent ()
       if len (dictionary) == 0 :
          self.putLn ("self.token = " + "self.keyword_" + name )
       else :
          self.printKeywordDictionary (dictionary, inx+1, name)
       self.decIndent ()

   def printKeywordDictionary (self, dictionary, inx, name) :
       if len (dictionary) == 1 :
          start_inx = inx
          substr = ""
          while len (dictionary) == 1:
             for c in sorted (dictionary.keys ()) : # only one
                 substr = substr + c
                 dictionary = dictionary [c]
                 inx = inx + 1
                 name = name + c
          inx = inx - 1
          if start_inx == inx :
             self.putLn ("if s[" + str (inx) + "] == " + "'" + substr + "'" + " :")
          else :
             self.putLn ("if s[" + str (start_inx) + ":" + str (inx+1) + "] == " + '"' + substr + '"' + " :")
          self.prindKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if first_item :
                  cmd = "if"
                  first_item = False
               else :
                  cmd = "elif"
               self.putLn (cmd + " s[" + str (inx) + "] == "  "'" + c + "'" + " :")
               self.prindKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.putLn ("def lookupKeyword (self) :")
       self.incIndent ()
       self.putLn ("s = self.tokenText")
       self.putLn ("n = len (s)")

       lim = 0
       for name in grammar.keyword_dict :
           n = len (name)
           if n > lim :
              lim = n

       size = 1
       first_item = True
       while size <= lim :
          tree = { }
          for name in grammar.keyword_dict :
              if len (name) == size :
                 self.addToDictionary (tree, name)
          if len (tree) != 0 :
             if first_item :
                cmd = "if"
                first_item = False
             else :
                cmd = "elif"
             self.putLn (cmd + " n == " + str (size) + " :")
             self.incIndent ()
             self.printKeywordDictionary (tree, 0, "")
             self.decIndent ()
          size = size + 1

       self.decIndent ()
       self.putLn ()

# --------------------------------------------------------------------------

   def printDictionary (self, dictionary) :
       for c in sorted (dictionary.keys ()) :
           self.putLn ("'" + c + "'" + " :")
           self.incIndent ()
           if len (dictionary[c]) == 0 :
              self.putLn ("#")
           else :
              printDictionary (dictionary[c])
           self.decIndent ()

   def selectBranch (self, grammar, dictionary, level, prefix) :
       for c in sorted (dictionary.keys ()) :
           if level == 1 :
              self.putLn ("if self.tokenText == " + "'" + c + "'" + " :")
           else :
              self.putLn ("if self.ch == " + "'" + c + "'" + " :")
           self.incIndent ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.putLn ("self.token = " + str ( grammar.separator_dict[name].inx)) # !?
           if level > 1 :
              self.putLn ("self.tokenText = self.tokenText + self.ch")
              self.putLn ("self.nextChar ()")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.decIndent ()

   def selectSeparators (self, grammar) :
       self.putLn ("def processSeparator (self) :")
       self.incIndent ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.putLn ("if self.token == self.separator :")
       self.incIndent ()
       self.putLn ("self.error (" + '"' + "Unknown separator" + '"' + ")")
       self.decIndent ()

       self.decIndent ()
       self.putLn ()

   # -----------------------------------------------------------------------

   def declareTypes (self, grammar) :
       for type in grammar.type_list :
          self.put ("class " + type.name + " (")
          if type.super_type != None :
             self.put (type.super_type.name)
          else :
             self.put ("object")
          self.putLn (") :")
          self.incIndent ()

          any = False
          for enum_name in type.enums :
              enum = type.enums [enum_name]
              inx = 0
              for value in enum.values :
                  any = True
                  self.putLn (value + " = " + str (inx))
                  inx = inx + 1
          if any :
             self.putLn ()

          self.putLn ("def __init__ (self) :")
          self.incIndent ()
          any = False

          if type.super_type != None :
             self.putLn ("super (" + type.name + ", self).__init__ ()")
             # self.putLn (type.super_type.name + ".__init__ (self)")
             any = True

          for field in type.field_list :
             any = True
             self.put ("self." + field.name + " = ")
             if field.field_type == "bool" :
                self.put ("False")
             elif field.field_type == "str" :
                self.put ('"' + '"')
             elif field.field_type == "list" :
                self.put ("[ ]")
             elif field.field_type in type.enums :
                self.put ("[ ]")
             else :
                self.put ("None")
             self.putEol ()

          if not any :
             self.putLn ("pass")
          self.decIndent ()

          self.decIndent ()
          self.putLn ()
          # self.putLn ("# end of " + type.name)

   # -----------------------------------------------------------------------

   def declareTerminals (self, grammar) :
       for symbol in grammar.symbols :
           if symbol.keyword :
              self.putLn ("self." + symbol.ident + " = " + str (symbol.inx))
           elif symbol.separator :
              if symbol.ident != "" :
                 self.putLn ("self." + symbol.ident + " = " + str (symbol.inx) + " # " + symbol.text)
              else :
                 self.putLn ("# " + symbol.text + " " + str (symbol.inx))
           else :
              self.putLn ("# " + symbol.ident + " = " + str (symbol.inx))

   def convertTerminals (self, grammar) :
       self.putLn ("def tokenToString (self, value) :")
       self.incIndent ()

       for symbol in grammar.symbols :
           self.putLn ("if value == " + str (symbol.inx) + ": " + "return " + '"' + symbol.alias + '"')

       self.putLn ("return " + '"' + "<unknown symbol>" + '"')
       self.decIndent ()
       self.putLn ()

   # --------------------------------------------------------------------------

   def initCollections (self, grammar) :
       grammar.collections = [ ]

   def registerCollection (self, grammar, collection) :
       "collection is set of (at least four) symbols"
       data = [ ]
       for inx in range (len (collection)) :
           if collection [inx] :
              data = data + [inx]
       if data not in grammar.collections :
          grammar.collections = grammar.collections + [data]
       return grammar.collections.index (data)

   def declareStoreLocation (self, grammar) :
       self.putLn ("def storeLocation (self, item) :")
       self.incIndent ()
       self.putLn ("item.src_file = self.fileInx")
       self.putLn ("item.src_line = self.tokenLineNum")
       self.putLn ("item.src_column = self.tokenColNum")
       self.putLn ("item.src_pos = self.tokenByteOfs")
       self.putLn ("item.src_end = self.charByteOfs")
       self.decIndent ()
       self.putLn ()

   def declareAlloc (self, grammar) :
       self.putLn ("def alloc (self, items) :")
       self.incIndent ()
       self.putLn ("result = [False] * " + str (grammar.symbol_cnt))
       self.putLn ("for item in items :")
       self.incIndent ()
       self.putLn ("result [item] = True")
       self.decIndent ()
       self.putLn ("return result")
       self.decIndent ()
       self.putLn ()

   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           self.put ("self.set_" + str (num) + " = self.alloc (" )

           self.put ("[")
           any = False
           for inx in data :
              if any :
                 self.put (", ")
              any = True
              symbol = grammar.symbols [inx]
              if symbol.ident != "" :
                 self.put ("self." + symbol.ident)
              else :
                 self.put (str (inx))
           self.put ("]")

           self.put ( ") #" )

           for inx in data :
               self.put (" ")
               symbol = grammar.symbols [inx]
               if symbol.text != "" :
                  self.put (" " +symbol.text)
               else :
                  self.put (" " +symbol.ident)

           self.putEol ()
           num = num + 1

   def condition (self, grammar, collection) :
       cnt = 0
       for inx in range (len (collection)) :
           if collection [inx] :
              cnt = cnt + 1

       complex = False
       if cnt == 0 :
          # grammar.error ("Empty set")
          # return "nothing"
          code = "True" # !?
       elif cnt <= 3 :
          if cnt > 1 :
             complex = True
          code = ""
          start = True
          for inx in range (len (collection)) :
              if collection [inx] :
                 if not start :
                    code = code + " or "
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.text != "" :
                    code = code + "self.tokenText == " + '"' + symbol.text + '"'
                 else :
                    code = code + "self.token == self." + symbol.ident
       else :
          num = self.registerCollection (grammar, collection)
          code = "self.set_" + str (num) + " [self.token]";

       return code

   def conditionFromAlternative (self, grammar, alt) :
       code = self.condition (grammar, alt.first)
       return code

   def conditionFromExpression (self, grammar, expr) :
       code = ""
       for alt in expr.alternatives :
           if code != "" :
              code = code + " or "
           code = code + self.conditionFromAlternative (grammar, alt)
       return code

   def conditionFromRule (self, grammar, name) :
       if name not in grammar.rule_dict :
          grammar.error ("Unknown rule: " + name)
       rule = grammar.rule_dict [name]
       return self.condition (grammar, rule.first)

   # -----------------------------------------------------------------------

   def simpleExpression (self, expr) :
       simple = len (expr.alternatives) != 0
       for alt in expr.alternatives :
           if not self.simpleAlternative (alt) :
              simple = False
       return simple

   def simpleAlternative (self, alt) :
       simple = False
       if len (alt.items) == 1 :
          item = alt.items [0]
          if isinstance (item, Terminal) :
             simple = True
       return simple

   # def simpleEbnf (self, ebnf) :
   #     return self.simpleExpression (ebnf.expr)

   # -----------------------------------------------------------------------

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.parserFromRule (grammar, rule)

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       rule.actual_type = rule.rule_type
       if rule.rule_type != "" :
          grammar.declareType (rule.rule_type, rule.super_type)

       params = ""
       if rule.rule_mode == "modify" :
          params = "result"
       if rule.store_name != "" :
          if params != "" :
             params = params + ", "
          params = params + "store"
       if params != "" :
          params = ", " + params # comma after self

       self.putLn ("def parse_" + rule.name + " (self" + params + ") :")

       self.incIndent ()

       if rule.rule_mode == "new" :
          self.putLn ("result = " + rule.rule_type + " ()")
          self.putLn ("self.storeLocation (result)")

       if rule.store_name != "" :
          grammar.declareField (rule.actual_type, rule.store_name, rule.store_type)
          self.putLn ("result." + rule.store_name + " = store")

       self.parserFromExpression (grammar, rule, rule.expr)

       self.putLn ("return result")
       self.decIndent ()
       self.putEol ()

   def parserFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt)
              if start :
                 self.put ("if")
              else :
                 self.put ("elif")
              start = False
              self.putLn (" " + cond + " :")
              self.incIndent ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.decIndent ()
       if cnt > 1 :
          self.putLn ("else :")
          self.incIndent ()
          self.putLn ("self.error (" +  '"' + "Unexpected token" + '"' + ")")
          self.decIndent ()

   def parserFromAlternative (self, grammar, rule, alt) :
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.parserFromTerminal (grammar, rule, item)
           elif isinstance (item, Nonterminal) :
              self.parserFromNonterminal (grammar, rule, item)
           elif isinstance (item, Ebnf) :
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              grammar.declareFieldValue (rule.actual_type, item.variable, item.value)
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "result."
              self.putLn ("result." + item.variable + " = " + prefix + item.value)
           elif isinstance (item, Execute) :
              grammar.declareMethod (item.name)
              if item.no_param :
                 self.putLn ("self." + item.name + " ()")
              else :
                 self.putLn ("self." + item.name + " (result)")
           elif isinstance (item, New) :
              grammar.declareType (item.new_type, item.new_super_type)
              self.putLn ("store = result")
              self.putLn ("result = " + item.new_type + " ()")
              self.putLn ("self.storeLocation (result)")
              self.putLn ("result."  + item.store_name + " = store")
              rule.actual_type = item.new_type
              if item.store_name != "" :
                 grammar.declareField (rule.actual_type, item.store_name, item.store_type)
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       # after for
       if alt.continue_alt :
          rule.actual_type = rule.rule_type

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if ")
       elif ebnf.mark == '*' :
          self.put ("while ")
       elif ebnf.mark == '+' :
          self.put ("while ")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          self.put (cond)
          self.putLn (" :")
          self.incIndent ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.decIndent ()

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.variable != "" :
           grammar.declareField (rule.actual_type, item.variable, item.rule_ref.rule_type)
       if item.add :
           grammar.declareField (rule.actual_type, "items", "list")

       if item.add :
          self.put ("result.items.append (")
       if item.select_item or item.continue_item :
          self.put ("result = ")
       if item.variable != ""  :
          self.put ("result." + item.variable + " = ")

       self.put ("self.parse_" + item.rule_name)

       params = ""
       if item.modify or item.rule_ref.rule_mode == "modify" :
          params = "result"
       if item.rule_ref.store_name != "" :
          params = "result"

       self.put (" (")
       if params != "" :
          self.put (params)
       self.put (")")

       if item.add :
          self.put (")") # close append parameters
       self.putEol ()

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             grammar.declareField (rule.actual_type, item.variable, "str")
             self.put ("result." + item.variable + " = ")

          func = symbol.ident
          if func.endswith ("_number") :
             func = func [ : -7 ]
          if func.endswith ("_literal") :
             func = func [ : -8 ]
          func = "read" + func.capitalize()

          self.putLn ("self." + func + " ()")
       else :
          if symbol.text != "":
             self.putLn ("self.check (" + '"' + symbol.text + '"' + ")")
          else :
             self.putLn ("self.check (" + str (symbol.inx) + ")")

   # -----------------------------------------------------------------------

   def note (self, txt) :
       # txt == "" ... init timer
       if 0 :
          start = self.start
          stop = time.clock ()
          if start == 0 :
             start = stop # first time measurement
          if txt != "" :
             print (txt + ", time %0.4f s" % (stop - start))
          self.start = stop

   # -----------------------------------------------------------------------

   def parserFromGrammar (self, grammar, class_name = "Parser") :
       self.note ("")
       grammar.parseRules ()
       self.note ("grammar parsed")

       initSymbols (grammar)
       self.initCollections (grammar)
       self.note ("symbols initialized")

       self.putLn ()
       self.putLn ("from easy_lexer import Lexer")
       self.putLn ()

       self.putLn ("class " + class_name + " (Lexer) :")
       self.incIndent ()

       self.parserFromRules (grammar)
       self.note ("parser methods generated")

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)
       self.declareStoreLocation (grammar)
       self.declareAlloc (grammar)

       self.putLn ("def __init__ (self) :")
       self.incIndent ()
       self.putLn ("super (" + class_name + ", self).__init__ ()")
       self.putLn ()
       self.declareTerminals (grammar)
       self.putLn ()
       self.declareCollections (grammar)
       self.decIndent ()
       self.putLn ()

       for method_name in grammar.methods :
          self.putLn ("def " +  method_name + " (self, item) :")
          self.incIndent ()
          self.putLn ("pass")
          self.decIndent ()
          self.putLn ()

       self.decIndent () # end of class

       self.declareTypes (grammar)

       self.note ("finished")

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("./input/cecko2.g")

    product = ToParser ()
    product.parserFromGrammar (grammar)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
