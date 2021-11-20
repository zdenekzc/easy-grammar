
# easy_cparser.py

from __future__ import print_function

from easy_grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Assign, Execute, New, Style
from easy_symbols import Symbol, initSymbols
from easy_lexer import quoteString
from easy_output import Output

from easy_toparser import ToParser

# --------------------------------------------------------------------------

class CParser (ToParser) :

   use_strings = False # use symbol text (in parsing)
   use_numbers = True # use integers (during set allocation)

   def prindKeywordItem (self, dictionary, inx, name) :
       self.incIndent ()
       if len (dictionary) == 0 :
          self.putLn ("token = " + "keyword_" + name )
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
             self.putLn ("if (s[" + str (inx) + "] == " + "'" + substr + "'" + ")")
          else :
             self.putLn ("if (s[" + str (start_inx) + ":" + str (inx+1) + "] == " + '"' + substr + '"' + ")")
          self.prindKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if first_item :
                  cmd = "if"
                  first_item = False
               else :
                  cmd = "else if"
               self.putLn (cmd + " (s[" + str (inx) + "] == "  "'" + c + "'" + ")")
               self.prindKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.putLn ("void " + self.class_name + "::lookupKeyword ()")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("string s = tokenText;")
       self.putLn ("int n = len (s);")

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
             self.putLn (cmd + " (n == " + str (size) + ")")
             self.putLn ("{")
             self.incIndent ()
             self.printKeywordDictionary (tree, 0, "")
             self.decIndent ()
             self.putLn ("}")
          size = size + 1

       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # -----------------------------------------------------------------------

   def printDictionary (self, dictionary) :
       for c in sorted (dictionary.keys ()) :
           self.putLn ("'" + c + "'" + " :")
           self.incIndent ()
           if len (dictionary[c]) == 0 :
              self.putLn ("//")
           else :
              printDictionary (dictionary[c])
           self.decIndent ()

   def selectBranch (self, grammar, dictionary, level, prefix) :
       for c in sorted (dictionary.keys ()) :
           if level == 1 :
              self.putLn ("if (tokenText == " + "'" + c + "'" + ")")
           else :
              self.putLn ("if (ch == " + "'" + c + "'" + ")")
           self.putLn ("{")
           self.incIndent ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.putLn ("token = " + str ( grammar.separator_dict[name].inx)) # !?
           if level > 1 :
              self.putLn ("tokenText = tokenText + ch;")
              self.putLn ("nextChar ();")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.decIndent ()
           self.putLn ("}")

   def selectSeparators (self, grammar) :
       self.putLn ("void " + self.class_name + "::processSeparator ()")
       self.putLn ("{")
       self.incIndent ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.putLn ("if (token == separator)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("error (" + '"' + "Unknown separator" + '"' + ");")
       self.decIndent ()
       self.putLn ("}")

       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # -----------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       if rule_name in func_dict :
          method_name = func_dict [rule_name]
          self.declareMethod (grammar, method_name, no_param)
          if no_param :
             self.putLn (method_name + " ();")
          else :
             self.putLn (method_name + " (result);")

   def declareField (self, grammar, cls, name, type) :
       pass

   def declareType (self, grammar, rule_type, super_type) :
       pass

   def declareFieldValue (self, grammar, cls, variable, value) :
       pass

   def declareFieldVariable (self, grammar, cls, name, type) :
       pass

   def declareTagField (self, grammar, cls, tag_name, tag_value) :
       pass

   def declareMethod (self, grammar, func_name, no_param = False) :
       pass

   def declareTypes (self, grammar) :
       for type in grammar.type_list :
           self.declareClass (grammar, type)

   def declareClass (self, grammar, type) :
       self.put ("class " + type.name)
       if type.super_type != None :
          self.put (" : public " + type.super_type.name)
       self.putEol ()
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("public:")
       self.incIndent ()

       for enum_name in type.enums :
           enum = type.enums [enum_name]
           self.putLn ("enum Enum_" + enum.name)
           self.putLn ("{")
           self.incIndent ()
           any = False
           for value in enum.values :
               if any :
                  self.putLn (",")
               any = True
               self.put (value)
           if any :
              self.putLn ()
           self.decIndent ()
           self.putLn ("};")
           self.style_empty_line ()

       "field declaration"
       for field in type.field_list :
          if field.field_type == "bool" :
             self.put ("bool")
          elif field.field_type == "str" :
             self.put ("string")
          elif field.field_type == "list" :
             self.put ("list")
          elif field.field_type == "enum" :
             self.put ("Enum_" + field.name)
          else :
             self.put (field.field_type + " *")
          self.putLn (" " + field.name + ";")
       self.style_empty_line ()

       "constructor"
       self.decIndent ()
       self.putLn ("public:")
       self.incIndent ()
       self.putLn (type.name + " ()")

       self.incIndent ()
       any = False
       if type.super_type != None :
          self.put (type.super_type.name + " ()")
          any = True
       for field in type.field_list :
           if any :
              self.putLn (",")
           any = True
           self.put (field.name + " (")
           if field.field_type == "bool" :
              self.put ("false")
           elif field.field_type == "str" :
              self.put ('"' + '"')
           elif field.field_type == "list" :
              self.put ("[ ]")
           else :
             self.put ("NULL")
           self.put (")")
       if any :
          self.putEol ()
       self.decIndent ()

       "constructor body"
       self.putLn ("{")
       self.incIndent ()
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

       "end of class"
       self.style_no_empty_line ()
       self.decIndent ()
       self.decIndent ()
       self.putLn ("};")
       self.putLn ()

   # -----------------------------------------------------------------------

   def declareTerminals (self, grammar) :
       for symbol in grammar.symbols :
           if symbol.keyword :
              self.putLn ("const int " + symbol.ident + " = " + str (symbol.inx) + ";")
           elif symbol.separator :
              if symbol.ident != "" :
                 self.putLn ("const int " + symbol.ident + " = " + str (symbol.inx) + "; // " + symbol.text)
              else :
                 self.putLn ("// " + symbol.text + " = " + str (symbol.inx))
           else :
              self.putLn ("// " + symbol.ident + " = " + str (symbol.inx))

   def convertTerminals (self, grammar) :
       self.putLn ("string " + self.class_name + "::tokenToString (Token value)")
       self.putLn ("{")
       self.incIndent ()

       for symbol in grammar.symbols :
           self.putLn ("if (value == " + str (symbol.inx) + ") " + "return " + '"' + symbol.alias + '"' + ";")

       self.putLn ("return " + '"' + "<unknown symbol>" + '"' + ";")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareStoreLocation (self, grammar) :
       self.putLn ("void " + self.class_name + "::storeLocation (item)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("item.src_file = tokenFileInx") # !?
       self.putLn ("item.src_line = tokenLineNum")
       self.putLn ("item.src_column = tokenColNum")
       self.putLn ("item.src_pos = tokenByteOfs")
       self.putLn ("item.src_end = charByteOfs")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   def declareAlloc (self, grammar) :
       self.putLn ("bool * " + self.class_name + "::alloc (items) :")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("result = new bool [" + str (grammar.symbol_cnt) + "];")
       self.putLn ("foreach (item : items)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("result [item] = true;")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ("return result;")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           self.put ("set_" + str (num) + " = alloc (" )

           if self.use_numbers :
              self.put (str (data))
           else:
              self.put ("[")
              any = False
              for inx in data :
                 if any :
                    self.put (", ")
                 any = True
                 symbol = grammar.symbols [inx]
                 if symbol.ident != "" :
                    self.put (symbol.ident)
                 else :
                    self.put (str (inx))
              self.put ("]")

           self.put ( ") //" )

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
                    code = code + " || "
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
                    code = code + "token == " + symbol.ident
                 elif symbol.text != "" :
                    code = code + "tokenText == " + '"' + symbol.text + '"'
                 else :
                    code = code + "token == " + str (symbol.inx)
       else :
          num = self.registerCollection (grammar, collection)
          code = "set_" + str (num) + " [token]";

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

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.parserFromRule (grammar, rule)

   def headerFromRule (self, grammar, rule, prefix = "", suffix = "") :
       rule.actual_type = rule.rule_type
       if rule.rule_mode != "" :
          if rule.rule_type != "" :
             self.declareType (grammar, rule.rule_type, rule.super_type)

       params = ""
       if rule.rule_mode == "modify" :
          params = "result"
       if rule.store_name != "" :
          if params != "" :
             params = params + ", "
          params = params + "store"

       self.putLn (rule.rule_type + " * " + prefix + "parse_" + rule.name + " (" + params + ")" + suffix)

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.headerFromRule (grammar, rule, self.class_name + "::", "")

       self.putLn ("{")
       self.incIndent ()

       if rule.rule_mode == "new" :
          self.putLn (rule.rule_type + " * result = new " + rule.rule_type + ";")

          self.putLn ("storeLocation (result);")

       if rule.store_name != "" :
          self.declareField (grammar, rule.actual_type, rule.store_name, rule.store_type)
          self.putLn ("result->" + rule.store_name + " = store;")

       self.parserFromExpression (grammar, rule, rule.expr)

       self.putLn ("return result;")
       self.decIndent ()
       self.putLn ("}")
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
                 self.put ("else if")
              start = False
              self.putLn (" (" + cond + ")")
              self.putLn ("{")
              self.incIndent ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.decIndent ()
              self.putLn ("}")
       if cnt > 1 :
          self.putLn ("else")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("error (" +  '"' + "Unexpected token" + '"' + ");")
          self.decIndent ()
          self.putLn ("}")

   def parserFromAlternative (self, grammar, rule, alt) :
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.parserFromTerminal (grammar, rule, item)
           elif isinstance (item, Nonterminal) :
              self.parserFromNonterminal (grammar, rule, item)
           elif isinstance (item, Ebnf) :
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              self.declareFieldValue (grammar, rule.actual_type, item.variable, item.value)
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "result->"
              self.putLn ("result->" + item.variable + " = " + prefix + item.value)
           elif isinstance (item, Execute) :
              self.declareMethod (grammar, item.name)
              if item.no_param :
                 self.putLn (item.name + " ();")
              else :
                 self.putLn (item.name + " (result);")
           elif isinstance (item, New) :
              self.declareType (grammar, item.new_type, item.new_super_type)
              self.putLn (rule.rule_type + " * store = result;")
              self.putLn ("result = new " + item.new_type + ";")
              self.putLn ("storeLocation (result);")
              self.putLn ("result->"  + item.store_name + " = store;")
              rule.actual_type = item.new_type
              if item.store_name != "" :
                 self.declareField (grammar, rule.actual_type, item.store_name, item.store_type)
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       # after for
       if alt.continue_alt :
          rule.actual_type = rule.rule_type

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          self.putLn (" (" + cond + ")")
          self.putLn ("{")
          self.incIndent ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("}")

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.variable != "" :
           self.declareField (grammar, rule.actual_type, item.variable, item.rule_ref.rule_type)
       if item.add :
           self.declareField (grammar, rule.actual_type, "items", "list")

       if item.add :
          self.put ("result->items.append (")
       if item.select_item or item.continue_item :
          self.put ("result = ")
       if item.variable != ""  :
          self.put ("result->" + item.variable + " = ")

       self.put ("parse_" + item.rule_name)

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
       self.putLn (";")

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.declareField (grammar, rule.actual_type, item.variable, "str")
             self.put ("result->" + item.variable + " = ")

          func = symbol.ident
          if func.endswith ("_number") :
             func = func [ : -7 ]
          if func.endswith ("_literal") :
             func = func [ : -8 ]
          func = "read" + func.capitalize()

          self.putLn (func + " ();")
       else :
          if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
             self.putLn ("checkToken (" + symbol.ident + ");")
          elif symbol.text != "":
             self.putLn ("check (" + '"' + symbol.text + '"' + ");")
          else :
             self.putLn ("check (" + str (symbol.inx) + ");")

# --------------------------------------------------------------------------

   def parserFromGrammar (self, grammar, class_name = "Parser") :
       grammar.parseRules ()
       self.class_name = class_name

       initSymbols (grammar)
       self.initCollections (grammar)

       self.putLn ()
       self.putLn ("#include " + quoteString ("lexer.h"))
       self.putLn ()

       for type in grammar.type_list :
           self.putLn ("class " + type.name + ";")
       self.putLn ()

       self.putLn ("class " + class_name + " : public Lexer")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("public:")
       self.incIndent ()

       self.putLn (class_name + " ();") # constructor
       self.style_empty_line ()

       for rule in grammar.rules :
          self.headerFromRule (grammar, rule, "", ";")
       self.style_empty_line ()

       self.putLn ("void lookupKeyword ();")
       self.putLn ("void processSeparator ();")
       self.putLn ("string tokenToString (Token value);")
       self.putLn ("void storeLocation (item);")
       self.style_empty_line ()

       for method_name in grammar.methods :
          self.putLn ("virtual void " +  method_name + " (item) { }")

       for method_name in grammar.methods_no_param :
          self.putLn ("virtual void " +  method_name + " () { }")

       self.style_no_empty_line ()
       self.decIndent () # end of class
       self.decIndent ()
       self.putLn ("};")
       self.putLn ()

       # constructor
       self.putLn (class_name + "::" + class_name + " () :")
       self.incIndent ()
       self.putLn ("Lexer ()")
       self.decIndent ()
       self.putLn ("{")
       self.incIndent ()
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

       self.parserFromRules (grammar)

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)
       self.declareStoreLocation (grammar)
       self.declareAlloc (grammar)

       self.declareTypes (grammar)

       self.declareTerminals (grammar)
       self.declareCollections (grammar)


# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("input/pas.g")

    product = CParser ()
    product.parserFromGrammar (grammar)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
