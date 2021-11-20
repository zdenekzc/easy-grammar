
# easy_toproduct.py

from __future__ import print_function

from easy_grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive, Assign, Execute, New, Style
from easy_output import Output
from easy_toparser import ToParser

# --------------------------------------------------------------------------

class ToProduct (Output) :

   def __init__ (self) :
       super (ToProduct, self).__init__ ()

   def conditionFromAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Nonterminal) :
              if item.variable != "" :
                 return "param." + item.variable + " != None"
              elif item.add :
                 return "inx < cnt"
              elif item.select_item or item.continue_item :
                 rule_ref = item.rule_ref
                 return "isinstance (param, " + rule_ref.rule_type + ")"
           elif isinstance (item, Terminal) :
              if item.multiterminal_name != "" :
                 return "param." + item.variable + " != " + '"' + '"'
           elif isinstance (item, New) :
                 return "isinstance (param, " + item.new_type + ")"
           elif isinstance (item, Assign) :
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "param."
              return "param." + item.variable + " == " + prefix + item.value
       return "unknown"
       # grammar.error ("Cannot find condition")

   def conditionFromExpression (self, grammar, expr) :
       result = ""
       for alt in expr.alternatives :
           if result != "" :
              result = result + " or "
           result = result + self.conditionFromAlternative (grammar, alt)
       return result

   def conditionIsUnknown (self, cond) :
       return (cond == "unknown")

   def conditionIsLoop (self, grammar, expr) :
       result = False
       for alt in expr.alternatives :
           cond = self.conditionFromAlternative (grammar, alt)
           if cond == "inx < cnt" :
              result = True
       return result

# --------------------------------------------------------------------------

   def productFromRules (self, grammar) :
       self.last_rule = None
       for rule in grammar.rules :
           self.productFromRule (grammar, rule)

   def productFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.last_rule = rule
       grammar.charLineNum = rule.src_line # !?
       grammar.charColNum = rule.src_column
       self.putLn ("def send_" + rule.name + " (self, param) :")
       self.incIndent ()
       if rule.add_used :
          self.putLn ("inx = 0")
          self.putLn ("cnt = len (param.items)")
       self.productFromExpression (grammar, rule, rule.expr)
       self.decIndent ()
       self.putEol ()

   def productChooseItem (self, grammar, rule, alt, field, enable_recursion) :
       proc = alt.select_nonterm.rule_name
       if enable_recursion :
          mark = alt.continue_ebnf.mark
          if mark == "+" or mark == "*" :
             proc = rule.name
       self.putLn ("self.send_" + proc + " (" + field + ")")

   def productFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       inx = 0
       for alt in expr.alternatives :
           if cnt > 1 or expr.continue_expr :
              cond = self.conditionFromAlternative (grammar, alt)
              #if self.conditionIsUnknown (cond) :
                 #if inx < len (expr.alternatives) - 1 :
                    ## grammar.error ("Cannot find condition (rule: " + self.last_rule.name+ ")")
                    #pass
                 #else :
                    #self.putLn ("else :")
              #else :
              if inx == 0 :
                 self.putLn ("if " + cond + " :")
              else :
                 self.putLn ("elif " + cond + " :")
              self.incIndent ()
           self.productFromAlternative (grammar, rule, alt)
           if cnt > 1  or expr.continue_expr :
              self.decIndent ()
           inx = inx + 1
       if expr.continue_expr :
          self.putLn ("else :")
          self.incIndent ()
          self.productChooseItem (grammar, rule, expr.expr_link, "param", False)
          self.decIndent ()

   def productFromAlternative (self, grammar, rule, alt) :
       grammar.updatePosition (alt)
       any = False
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.productFromTerminal (grammar, item)
              any = True
           elif isinstance (item, Nonterminal) :
              if item.continue_item :
                 if item.rule_ref.store_name != "" :
                    self.productChooseItem (grammar, rule, alt.alt_link, "param." + item.rule_ref.store_name, True)
              choose = item.select_item and item.item_link.continue_ebnf != None
              if not choose :
                 self.productFromNonterminal (grammar, item)
                 any = True
           elif isinstance (item, Ebnf) :
              self.productFromEbnf (grammar, rule, item)
              any = True
           elif isinstance (item, Style) :
              self.productFromStyle (grammar, item)
              any = True
           elif isinstance (item, New) :
              self.productChooseItem (grammar, rule, alt.alt_link, "param." + item.store_name, True)
              any = True
           elif isinstance (item, Directive) :
              pass
           else :
              raise Exception ("Unknown alternative item")
       if not any :
          self.putLn ("pass")

   def productFromEbnf (self, grammar, rule, ebnf) :
       grammar.updatePosition (ebnf)
       block = False
       if not ebnf.expr.continue_expr :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          if ebnf.mark == '?' :
             self.putLn ("if " + cond + " :")
             block = True
          if ebnf.mark == '*' or ebnf.mark == '+' :
             loop = self.conditionIsLoop (grammar, ebnf.expr)
             if loop :
                self.putLn ("while " + cond + " :")
             else :
                self.putLn ("if " + cond + " :")
             block = True

       if block :
          self.incIndent ()

       self.productFromExpression (grammar, rule, ebnf.expr)

       if block :
          self.decIndent ()

   def productFromNonterminal (self, grammar, item, field = "") :
       grammar.updatePosition (item)
       proc = item.rule_name

       self.put ("self.send_" + proc)
       self.put (" (")
       if field != "" :
          self.put ("param." + field)
       elif item.variable :
          self.put ("param." + item.variable)
       elif item.add :
          self.put ("param.items [inx]")
       elif item.modify or item.select_item or item.continue_item :
          self.put ("param")
       self.putLn (")")

       if item.add :
          self.putLn ("inx = inx + 1")

   def productFromTerminal (self, grammar, item) :
       if item.multiterminal_name != "" :
          if item.variable != "" :
             quote1 = (item.multiterminal_name == "character_literal");
             quote2 = (item.multiterminal_name == "string_literal");

             if quote1 :
                self.put ("self.sendChr (")
             elif quote2 :
                self.put ("self.sendStr (")
             else :
                self.put ("self.send (")
             self.put ("param." + item.variable)
             self.putLn (")")
       else :
          self.putLn ("self.send (" + '"' + item.text + '"' + ")")

   def productFromStyle (self, grammar, item) :
       self.putLn ("self.style_" + item.name + " ()")

# --------------------------------------------------------------------------

   def productFromGrammar (self, grammar, parser_module = "") :

       self.putLn ()
       if parser_module != "" :
          self.putLn ("from " + parser_module + " import *")
       self.putLn ("from easy_output import Output")
       self.putLn ()

       self.putLn ("class Product (Output) :")
       self.putLn ("")
       self.incIndent ()

       self.productFromRules (grammar)

       self.decIndent ()

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    # grammar.openFile ("../pas.g")
    grammar.openFile ("../c2.g")
    grammar.parseRules ()

    product = ToParser ()
    product.parserFromGrammar (grammar)

    product = ToProduct ()
    product.productFromGrammar (grammar)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
