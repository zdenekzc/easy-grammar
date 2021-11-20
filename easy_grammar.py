
# easy_grammar.py

from __future__ import print_function

from easy_lexer import Lexer

# --------------------------------------------------------------------------

class Rule (object) :
   def __init__ (self) :
       self.name = ""
       self.expr = None
       self.rule_mode = ""
       self.rule_type = ""
       self.super_type = ""
       self.store_name = ""
       self.store_type = ""

       self.add_used = False
       self.new_directive = None # local
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

class Expression (object) :
   def __init__ (self) :
       self.alternatives = [ ]

       self.continue_expr = False
       self.expr_link = None # selection alternative

       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Alternative (object) :
   def __init__ (self) :
       self.items = [ ]

       self.level = 0
       self.silent = False
       self.leading_required = False # local

       self.select_alt = False # top level alternative in <select> rule
       self.select_nonterm = None

       self.continue_ebnf = None
       self.continue_alt = False # alternative in ( ... ) expression in <select> rule
       self.alt_link = None # selection alternative

       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Ebnf (object) :
   def __init__ (self) :
       self.mark = ""
       self.expr = None
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Nonterminal (object) :
   def __init__ (self) :
       self.variable = ""
       self.rule_name = ""
       self.add = False
       self.modify = False

       self.select_item = False
       self.item_link = None # selection alternative

       self.continue_item = False

       # self.rule_ref = None
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

class Terminal (object) :
   def __init__ (self) :
       self.text = ""

       self.variable = ""
       self.multiterminal_name = ""

       # self.symbol_ref = None
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

# --------------------------------------------------------------------------

class Directive (object) :
   def __init__ (self) :
       pass

class Assign (Directive) :
   def __init__ (self) :
       self.variable = ""
       self.value = ""

class Execute (Directive) :
   def __init__ (self) :
       self.name = ""
       self.no_param = False

class New (Directive) :
   def __init__ (self) :
       self.new_type = ""
       self.new_super_type = ""
       self.store_name = ""
       self.store_type = ""
       # self.tag_name = ""
       # self.tag_value = ""

class Style (Directive) :
   def __init__ (self) :
       self.name = ""

# --------------------------------------------------------------------------

class Options (object) :
   def __init__ (self) :
       self.add = False
       self.modify = False
       self.need_nonterminal = False

# --------------------------------------------------------------------------

class Type (object) :
    def __init__ (self) :
        self.name = ""
        self.super_type = None
        self.fields = { }
        self.field_list = [ ]
        self.enums = { }
        self.enum_list = [ ]

class Field (object) :
    def __init__ (self) :
        self.name = ""
        self.field_type = ""
        self.struct_type = None

class Enum (object) :
    def __init__ (self) :
        self.name = ""
        self.values = [ ]

# --------------------------------------------------------------------------

class Grammar (Lexer) :

   def __init__ (self) :
       super (Grammar, self).__init__ ()
       self.rules = [ ]
       self.multiterminals = [ "identifier",
                               "number",
                               "real_number",
                               "character_literal",
                               "string_literal" ]

       self.type_list = [ ]
       self.type_dict = { }
       self.methods = [ ]
       self.methods_no_param = [ ]

       # self.multiterminal_dict = { }
       # self.keyword_dict = { }
       # self.separator_dict = { }
       #
       # self.symbol_cnt = 0
       # self.symbols = [ ]
       # self.symbol_dict = { }
       #
       # self.rule_dict = { }
       # self.nullableChanged = True
       # self.firstChanged = True
       # self.followChanged = True

   # -- types --

   def declareType (self, name, super_type_name = "") :
       if super_type_name != "" :
          super_type = self.declareType (super_type_name)

       if name in self.type_dict :
          type = self.type_dict [name]
       else :
          type = Type ()
          type.name = name
          self.type_dict [name] = type
          self.type_list.append (type)

       if super_type_name != "" :
          if type.super_type != None and type.super_type != super_type :
             self.error ("Super type for " + type.name + " already defined")
          type.super_type = super_type

          # if type (without super_type) was already in type_list, correct type_list
          if self.type_list.index (super_type) > self.type_list.index (type) :
             self.type_list.remove (type)
             self.type_list.append (type)

       return type

   def findField (self, type, field_name) :
       while type != None and field_name not in type.fields :
          type = type.super_type
       field = None
       if type != None :
          field = type.fields [field_name]
       return field

   def declareField (self, type_name, field_name, field_type) :
       type = self.declareType (type_name)
       field = self.findField (type, field_name)
       if field != None :
          if field_type != field.field_type :
             self.error ("Field " + type_name + "." + field_name + " already defined with different type")
       else :
          field = Field ()
          field.name = field_name
          field.field_type = field_type
          field.struct_type = type
          type.fields [field_name] = field
          type.field_list.append (field)
       return field

   def declareEnumType (self, type, enum_name) :
       if enum_name in type.enums :
          enum = type.enums [enum_name]
       else :
          enum = Enum ()
          enum.name = enum_name
          type.enums [enum_name] = enum
          type.enum_list.append (enum)
       return enum

   def declareEnumValue (self, type, enum_name, enum_value) :
       enum = self.declareEnumType (type, enum_name)
       if enum_value not in enum.values :
          enum.values = enum.values + [enum_value]

   def declareFieldVariable (self, type_name, field_name, field_type) :
       field = self.declareField (type_name, field_name, field_type)
       if field_type == "enum" :
          self.declareEnumType (field.struct_type, field_name)

   def declareFieldValue (self, type_name, field_name, field_value) :
       if field_value == "True" or field_value == "False" :
          self.declareField (type_name, field_name, "bool")
       else :
          field = self.declareField (type_name, field_name, "enum")
          self.declareEnumValue (field.struct_type, field_name, field_value)

   def declareMethod (self, method_name, no_param = False) :
       if no_param :
          if method_name not in self.methods_no_param :
             self.methods_no_param.append (method_name)
       else :
          if method_name not in self.methods :
             self.methods.append (method_name)

   # -- rule directive --

   def ruleDirective (self, rule) :
       if self.isSeparator ('<') :
          self.nextToken ()

          if not self.isSeparator ('>') :

             if self.isKeyword ("new") :
                rule.rule_mode = "new"
                self.nextToken ()
             elif self.isKeyword ("modify") :
                rule.rule_mode = "modify"
                self.nextToken ()
             elif self.isKeyword ("select") or self.isKeyword ("choose") or self.isKeyword ("return") :
                rule.rule_mode = "select"
                self.nextToken ()
             else :
                rule.rule_mode = "new"

             rule.rule_type = self.readIdentifier ("Type name expected")

             if self.isSeparator (':') :
                self.nextToken ()
                rule.super_type = self.readIdentifier ("Super-type expected")
          self.checkSeparator ('>')

   # -- item directive --

   def itemDirective (self, rule, alt, opt) :
          self.checkSeparator ('<')

          if self.isKeyword ("new") :
             self.nextToken ()
             # add New to this alternative
             item = New ()
             item.new_type = self.readIdentifier ("Type identifier expected")
             self.checkSeparator (':')
             item.new_super_type = self.readIdentifier ("Type identifier expected")
             alt.items.append (item)
             rule.new_directive = item
             alt.leading_required = False # !?

          elif self.isKeyword ("store") :
             self.nextToken ()
             name = self.readIdentifier ("Field identifier expected")
             self.checkSeparator (':')
             type = self.readIdentifier ("Type identifier expected")
             if rule.new_directive != None :
                rule.new_directive.store_name = name
                rule.new_directive.store_type = type
             else :
                rule.store_name = name
                rule.store_type = type

          elif self.isKeyword ("add") :
             self.nextToken ()
             opt.add = True
             opt.need_nonterminal = True

          elif self.isKeyword ("modify") :
             self.nextToken ()
             opt.modify = True
             opt.need_nonterminal = True

          elif self.isKeyword ("set") :
             self.nextToken ()
             variable = self.readIdentifier ("Variable identifier expected")
             self.checkSeparator ('=')
             value = self.readIdentifier ("Value expected")
             if value == "true" :
                value = "True"
             if value == "false" :
                value = "False"
             # add Assign to this alternative
             item = Assign ()
             item.variable = variable
             item.value = value
             alt.items.append (item)

          elif self.isKeyword ("execute") :
             self.nextToken ()
             name = self.readIdentifier ("Method identifier expected")
             # add Execute to this alternative
             item = Execute ()
             item.name = name
             alt.items.append (item)

          elif self.isKeyword ("execute_no_param") :
             self.nextToken ()
             name = self.readIdentifier ("Method identifier expected")
             # add Execute to this alternative
             item = Execute ()
             item.name = name
             item.no_param = True
             alt.items.append (item)

          elif self.isKeyword ("silent") :
             self.nextToken ()
             # set silent field in this alternative
             alt.silent = True

          elif ( self.isKeyword ("indent") or
                 self.isKeyword ("unindent") or
                 self.isKeyword ("no_space") or
                 self.isKeyword ("new_line") or
                 self.isKeyword ("empty_line") ) :
             name = self.tokenText
             self.nextToken ()
             # add Style to this alternative
             item = Style ()
             item.name = name

          else :
             self.error ("Unknown directive " + self.tokenText)

          self.checkSeparator ('>')

   # -- source code position --

   def setPosition (self, item) :
       item.src_file = self.fileInx
       item.src_line = self.tokenLineNum
       item.src_column = self.tokenColNum
       item.src_pos = self.tokenByteOfs

   def rememberPosition (self) :
       return (self.fileInx, self.tokenLineNum, self.tokenColNum, self.tokenByteOfs)

   def storePosition (self, item, value) :
       # item.src_file = value [0]
       item.src_line = value [1]
       item.src_column = value [2]
       item.src_pos = value [3]

   def updatePosition (self, item) :
       "set position for error reporting, used by easy_symbols"
       self.tokenLineNum = item.src_line
       self.tokenColNum = item.src_column
       self.tokenByteOfs = item.src_pos

   # -- struct directive --

   def structDirective (self) :
       struct = StructDecl ()
       struct.struct_name = self.readIdentifier ("Type identifier expected")
       if self.isSeparator (':') :
          self.nextToken ()
          struct.super_type = self.readIdentifier ("Super-type identifier expected")
       self.struct_decl.append (struct)
       if self.isSeparator (',') :
          self.nextToken ()
          struct.tag_name = self.readIdentifier ("Tag identifier expected")
          self.checkSeparator ('=')
          struct.tag_value = self.readIdentifier ("Tag value expected")
       if self.isSeparator ('{') :
          self.nextToken ()
          while not self.isSeparator ('}') :
             field = FieldDecl ()
             field.field_type = self.readIdentifier ("Type identifier expected")
             field.field_name = self.readIdentifier ("Field identifier expected")
             self.checkSeparator (';')
             struct.fields.append (field)
          self.checkSeparator ('}')
       return struct

   # -- rules --

   def parseRules (self) :
       while not self.isEndOfSource () :
             self.parseRule ()

   def parseRule (self) :
       rule = Rule ()

       rule.name = self.readIdentifier ("Rule identifier expected")
       self.setPosition (rule)

       self.ruleDirective (rule)
       self.checkSeparator (':')

       rule.expr = self.parseExpression (rule, 1)

       self.checkSeparator (';')
       self.rules.append (rule)

   # -- expression --

   def parseExpression (self, rule, level) :
       expr = Expression ()
       self.setPosition (expr)

       if level == 2 :
          if rule.rule_mode == "select" :
             expr.continue_expr = True
             expr.expr_link = rule.above_alt

       alt = self.parseAlternative (rule, level)
       expr.alternatives.append (alt)

       while self.isSeparator ('|') :
          self.nextToken ()

          alt = self.parseAlternative (rule, level)
          expr.alternatives.append (alt)

       return expr

   def parseAlternative (self, rule, level) :
       alt = Alternative ()
       alt.level = level
       self.setPosition (alt)

       if level == 1 :
          if rule.rule_mode == "select" :
             alt.select_alt = True
             rule.above_alt = alt
             alt.leading_required = True

       if level == 2 :
          if rule.rule_mode == "select" :
             alt.continue_alt = True
             alt.alt_link = rule.above_alt
             alt.leading_required = True

       opt = Options ()

       while not self.isSeparator ('|') and not self.isSeparator (')') and not self.isSeparator (';') :

          if self.token == self.identifier :
             item = self.parseNonterminal (rule, alt, opt)
             alt.items.append (item)

          elif self.token == self.character_literal or self.token == self.string_literal :
             if opt.need_nonterminal :
                self.error ("Nonterminal expected")
             item = self.parseTerminal ()
             alt.items.append (item)

          elif self.isSeparator ('(') :
             if opt.need_nonterminal :
                self.error ("Nonterminal expected")
             if alt.leading_required :
                self.error ("Missing nonterminal (in the beginning of sub-expression)")
             ebnf = self.parseEbnf (rule, level)
             if alt.select_alt :
                alt.continue_ebnf = ebnf
             alt.items.append (ebnf)

          elif self.isSeparator ('<') :
             self.itemDirective (rule, alt, opt)

          else :
             self.error ("Unknown grammar item")

       # after while lopp
       if opt.need_nonterminal :
          self.error ("Nonterminal expected")

       if alt.leading_required :
          self.error ("Missing nonterminal (for rule with select attribute)")

       return alt

   def parseEbnf (self, rule, level) :
       item = Ebnf ()
       self.setPosition (item)

       self.checkSeparator ('(')
       item.expr = self.parseExpression (rule, level+1)
       self.checkSeparator (')')

       if self.isSeparator ('?') or self.isSeparator ('+') or self.isSeparator ('*') :
          item.mark = self.tokenText
          self.nextToken ()

       return item

   def parseNonterminal (self, rule, alt, opt) :

       item = None
       pos = self.rememberPosition ()
       variable = ""
       rule_name = self.readIdentifier ()

       if self.isSeparator (':') :
          self.nextToken ()
          variable = rule_name
          rule_name = self.readIdentifier ("Rule identifier expected")

       if rule_name in self.multiterminals :
          item = Terminal ()
          self.storePosition (item, pos)
          item.variable = variable
          item.multiterminal_name = rule_name
          if opt.add or opt.modify :
             self.error ("<add> or <modify> not allowed before multiterminal")
          if alt.leading_required :
             self.error ("Missing nonterminal (for rule with select or choose attribute)")
       else :
          item = Nonterminal ()
          self.storePosition (item, pos)
          item.variable = variable
          item.rule_name = rule_name

          item.add = opt.add
          item.modify = opt.modify
          opt.need_nonterminal = False

          if alt.leading_required  :
             alt.leading_required = False
             if alt.select_alt :
                item.select_item = True
                item.item_link = alt
                alt.select_nonterm = item
             if alt.continue_alt :
                item.continue_item = True
             if item.variable != "" :
                self.error ("Variable identifier not allowed for first nonterminal (in rule with select or choose attribute)")

          if item.add or item.modify :
             if item.variable != "" :
                self.error ("Variable identifier not allowed after <add> or <modify> directive")

          if item.add :
             rule.add_used = True

       return item

   def parseTerminal (self) :
       item = Terminal ()
       self.setPosition (item)
       item.text = self.tokenText
       self.nextToken ()
       return item

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("./input/cecko2.g")
    grammar.parseRules ()
    for rule in grammar.rules :
       print (rule.name)

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
