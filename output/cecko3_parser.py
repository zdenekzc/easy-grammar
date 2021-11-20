
from easy_lexer import Lexer

class Parser (Lexer) :
   def parse_while_stat (self) :
      result = CmmWhileStat ()
      self.storeLocation (result)
      self.check ("while")
      self.check ("(")
      result.cond = self.parse_expr ()
      self.check (")")
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_if_stat (self) :
      result = CmmIfStat ()
      self.storeLocation (result)
      self.check ("if")
      self.check ("(")
      result.cond = self.parse_expr ()
      self.check (")")
      result.then_stat = self.parse_inner_stat ()
      if self.tokenText == "else" :
         self.check ("else")
         result.else_stat = self.parse_inner_stat ()
      return result

   def parse_for_stat (self) :
      result = CmmForStat ()
      self.storeLocation (result)
      self.check ("for")
      self.check ("(")
      if self.set_0 [self.token] :
         result.from_expr = self.parse_expr ()
      self.check (";")
      if self.set_0 [self.token] :
         result.cond_expr = self.parse_expr ()
      self.check (";")
      if self.set_0 [self.token] :
         result.step_expr = self.parse_expr ()
      self.check (")")
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_return_stat (self) :
      result = CmmReturnStat ()
      self.storeLocation (result)
      self.check ("return")
      if self.set_0 [self.token] :
         result.return_expr = self.parse_expr ()
      self.check (";")
      return result

   def parse_compound_stat (self) :
      result = CmmCompoundStat ()
      self.storeLocation (result)
      self.check ("{")
      while self.set_1 [self.token] :
         result.items.append (self.parse_stat ())
      self.check ("}")
      return result

   def parse_simple_stat (self) :
      result = CmmSimpleStat ()
      self.storeLocation (result)
      result.inner_expr = self.parse_expr ()
      self.check (";")
      return result

   def parse_decl_stat (self) :
      result = CmmDeclStat ()
      self.storeLocation (result)
      self.check ("dcl")
      result.inner_decl = self.parse_simple_decl ()
      return result

   def parse_empty_stat (self) :
      result = CmmEmptyStat ()
      self.storeLocation (result)
      self.check (";")
      return result

   def parse_stat (self) :
      if self.tokenText == "dcl" :
         result = self.parse_decl_stat ()
      elif self.tokenText == "while" :
         result = self.parse_while_stat ()
      elif self.tokenText == "if" :
         result = self.parse_if_stat ()
      elif self.tokenText == "for" :
         result = self.parse_for_stat ()
      elif self.tokenText == "return" :
         result = self.parse_return_stat ()
      elif self.tokenText == "{" :
         result = self.parse_compound_stat ()
      elif self.set_0 [self.token] :
         result = self.parse_simple_stat ()
      elif self.tokenText == ";" :
         result = self.parse_empty_stat ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_inner_stat (self) :
      result = self.parse_stat ()
      return result

   def parse_variable_expr (self) :
      result = CmmVarExpr ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_variable_expr (result)
      return result

   def parse_int_value_expr (self) :
      result = CmmIntValue ()
      self.storeLocation (result)
      result.value = self.readNumber ()
      return result

   def parse_real_value_expr (self) :
      result = CmmRealValue ()
      self.storeLocation (result)
      result.value = self.readReal ()
      return result

   def parse_char_value_expr (self) :
      result = CmmCharValue ()
      self.storeLocation (result)
      result.value = self.readCharacter ()
      return result

   def parse_string_value_expr (self) :
      result = CmmStringValue ()
      self.storeLocation (result)
      result.value = self.readString ()
      return result

   def parse_subexpr_expr (self) :
      result = CmmSubexprExpr ()
      self.storeLocation (result)
      self.check ("(")
      result.inner_expr = self.parse_expr ()
      self.check (")")
      return result

   def parse_sequence_expr (self) :
      result = CmmSequenceExpr ()
      self.storeLocation (result)
      self.check ("[")
      result.param = self.parse_expr_list ()
      self.check ("]")
      return result

   def parse_this_expr (self) :
      result = CmmThisExpr ()
      self.storeLocation (result)
      self.check ("this")
      return result

   def parse_simple_expr (self) :
      if self.token == self.identifier :
         result = self.parse_variable_expr ()
      elif self.token == self.number :
         result = self.parse_int_value_expr ()
      elif self.token == self.real_number :
         result = self.parse_real_value_expr ()
      elif self.token == self.character_literal :
         result = self.parse_char_value_expr ()
      elif self.token == self.string_literal :
         result = self.parse_string_value_expr ()
      elif self.tokenText == "(" :
         result = self.parse_subexpr_expr ()
      elif self.tokenText == "[" :
         result = self.parse_sequence_expr ()
      elif self.tokenText == "this" :
         result = self.parse_this_expr ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_postfix_expr (self) :
      result = self.parse_simple_expr ()
      while self.tokenText == "[" or self.tokenText == "(" or self.tokenText == "{" or self.tokenText == "." or self.tokenText == "->" or self.tokenText == "++" or self.tokenText == "--" :
         if self.tokenText == "[" :
            result = self.parse_index_expr (result)
         elif self.tokenText == "(" :
            result = self.parse_call_expr (result)
         elif self.tokenText == "{" :
            result = self.parse_compound_expr (result)
         elif self.tokenText == "." :
            result = self.parse_field_expr (result)
         elif self.tokenText == "->" :
            result = self.parse_ptr_field_expr (result)
         elif self.tokenText == "++" :
            result = self.parse_post_inc_expr (result)
         elif self.tokenText == "--" :
            result = self.parse_post_dec_expr (result)
         else :
            self.error ("Unexpected token")
      return result

   def parse_index_expr (self, store) :
      result = CmmIndexExpr ()
      self.storeLocation (result)
      result.left = store
      self.check ("[")
      result.param = self.parse_expr_list ()
      self.check ("]")
      return result

   def parse_call_expr (self, store) :
      result = CmmCallExpr ()
      self.storeLocation (result)
      result.left = store
      self.check ("(")
      result.param_list = self.parse_expr_list ()
      self.check (")")
      return result

   def parse_compound_expr (self, store) :
      result = CmmCompoundExpr ()
      self.storeLocation (result)
      result.left = store
      result.body = self.parse_compound_stat ()
      return result

   def parse_field_expr (self, store) :
      result = CmmFieldExpr ()
      self.storeLocation (result)
      result.left = store
      self.check (".")
      result.name = self.readIdentifier ()
      self.on_field_expr (result)
      return result

   def parse_ptr_field_expr (self, store) :
      result = CmmPtrFieldExpr ()
      self.storeLocation (result)
      result.left = store
      self.check ("->")
      result.name = self.readIdentifier ()
      return result

   def parse_post_inc_expr (self, store) :
      result = CmmPostIncExpr ()
      self.storeLocation (result)
      result.left = store
      self.check ("++")
      return result

   def parse_post_dec_expr (self, store) :
      result = CmmPostDecExpr ()
      self.storeLocation (result)
      result.left = store
      self.check ("--")
      return result

   def parse_unary_expr (self) :
      if self.tokenText == "++" :
         result = self.parse_inc_expr ()
      elif self.tokenText == "--" :
         result = self.parse_dec_expr ()
      elif self.tokenText == "*" :
         result = self.parse_deref_expr ()
      elif self.tokenText == "&" :
         result = self.parse_addr_expr ()
      elif self.tokenText == "+" :
         result = self.parse_plus_expr ()
      elif self.tokenText == "-" :
         result = self.parse_minus_expr ()
      elif self.tokenText == "~" :
         result = self.parse_bit_not_expr ()
      elif self.tokenText == "!" :
         result = self.parse_log_not_expr ()
      elif self.tokenText == "new" :
         result = self.parse_allocation_expr ()
      elif self.tokenText == "delete" :
         result = self.parse_deallocation_expr ()
      elif self.set_2 [self.token] :
         result = self.parse_postfix_expr ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_inc_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("++")
      result.param = self.parse_unary_expr ()
      return result

   def parse_dec_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("--")
      result.param = self.parse_unary_expr ()
      return result

   def parse_deref_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("*")
      result.param = self.parse_unary_expr ()
      return result

   def parse_addr_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("&")
      result.param = self.parse_unary_expr ()
      return result

   def parse_plus_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("+")
      result.param = self.parse_unary_expr ()
      return result

   def parse_minus_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("-")
      result.param = self.parse_unary_expr ()
      return result

   def parse_bit_not_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("~")
      result.param = self.parse_unary_expr ()
      return result

   def parse_log_not_expr (self) :
      result = CmmUnaryExpr ()
      self.storeLocation (result)
      self.check ("!")
      result.param = self.parse_unary_expr ()
      return result

   def parse_allocation_expr (self) :
      result = CmmNewExpr ()
      self.storeLocation (result)
      self.check ("new")
      result.type = self.readIdentifier ()
      if self.tokenText == "(" :
         self.check ("(")
         result.init_list = self.parse_expr_list ()
         self.check (")")
      return result

   def parse_deallocation_expr (self) :
      result = CmmDeleteExpr ()
      self.storeLocation (result)
      self.check ("delete")
      result.param = self.parse_unary_expr ()
      return result

   def parse_multiplicative_expr (self) :
      result = self.parse_unary_expr ()
      while self.tokenText == "%" or self.tokenText == "*" or self.tokenText == "/" :
         store = result
         result = CmmMulExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "*" :
            self.check ("*")
            result.kind = result.mulExp
         elif self.tokenText == "/" :
            self.check ("/")
            result.kind = result.divExp
         elif self.tokenText == "%" :
            self.check ("%")
            result.kind = result.modExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_unary_expr ()
      return result

   def parse_additive_expr (self) :
      result = self.parse_multiplicative_expr ()
      while self.tokenText == "+" or self.tokenText == "-" :
         store = result
         result = CmmAddExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "+" :
            self.check ("+")
            result.kind = result.addExp
         elif self.tokenText == "-" :
            self.check ("-")
            result.kind = result.subExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_multiplicative_expr ()
      return result

   def parse_shift_expr (self) :
      result = self.parse_additive_expr ()
      while self.tokenText == "<<" or self.tokenText == ">>" :
         store = result
         result = CmmShiftExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "<<" :
            self.check ("<<")
            result.kind = result.shlExp
         elif self.tokenText == ">>" :
            self.check (">>")
            result.kind = result.shrExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_additive_expr ()
      return result

   def parse_relational_expr (self) :
      result = self.parse_shift_expr ()
      while self.set_3 [self.token] :
         store = result
         result = CmmRelExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "<" :
            self.check ("<")
            result.kind = result.ltExp
         elif self.tokenText == ">" :
            self.check (">")
            result.kind = result.gtExp
         elif self.tokenText == "<=" :
            self.check ("<=")
            result.kind = result.leExp
         elif self.tokenText == ">=" :
            self.check (">=")
            result.kind = result.geExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_shift_expr ()
      return result

   def parse_equality_expr (self) :
      result = self.parse_relational_expr ()
      while self.tokenText == "!=" or self.tokenText == "==" :
         store = result
         result = CmmEqExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "==" :
            self.check ("==")
            result.kind = result.eqExp
         elif self.tokenText == "!=" :
            self.check ("!=")
            result.kind = result.neExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_relational_expr ()
      return result

   def parse_and_expr (self) :
      result = self.parse_equality_expr ()
      while self.tokenText == "&" :
         store = result
         result = CmmAndExpr ()
         self.storeLocation (result)
         result.left = store
         self.check ("&")
         result.kind = result.bitAndExp
         result.right = self.parse_equality_expr ()
      return result

   def parse_exclusive_or_expr (self) :
      result = self.parse_and_expr ()
      while self.tokenText == "^" :
         store = result
         result = CmmXorExpr ()
         self.storeLocation (result)
         result.left = store
         self.check ("^")
         result.kind = result.bitXorExp
         result.right = self.parse_and_expr ()
      return result

   def parse_inclusive_or_expr (self) :
      result = self.parse_exclusive_or_expr ()
      while self.tokenText == "|" :
         store = result
         result = CmmOrExpr ()
         self.storeLocation (result)
         result.left = store
         self.check ("|")
         result.kind = result.bitOrExp
         result.right = self.parse_exclusive_or_expr ()
      return result

   def parse_logical_and_expr (self) :
      result = self.parse_inclusive_or_expr ()
      while self.tokenText == "&&" :
         store = result
         result = CmmAndAndExpr ()
         self.storeLocation (result)
         result.left = store
         self.check ("&&")
         result.kind = result.logAndExp
         result.right = self.parse_inclusive_or_expr ()
      return result

   def parse_logical_or_expr (self) :
      result = self.parse_logical_and_expr ()
      while self.tokenText == "||" :
         store = result
         result = CmmOrOrExpr ()
         self.storeLocation (result)
         result.left = store
         self.check ("||")
         result.kind = result.logOrExp
         result.right = self.parse_logical_and_expr ()
      return result

   def parse_assignment_expr (self) :
      result = self.parse_logical_or_expr ()
      if self.tokenText == "+=" or self.tokenText == "-=" or self.tokenText == "=" :
         store = result
         result = CmmAssignExpr ()
         self.storeLocation (result)
         result.left = store
         if self.tokenText == "=" :
            self.check ("=")
            result.kind = result.assignExp
         elif self.tokenText == "+=" :
            self.check ("+=")
            result.kind = result.assignAddExp
         elif self.tokenText == "-=" :
            self.check ("-=")
            result.kind = result.assignSubExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_assignment_expr ()
      return result

   def parse_expr (self) :
      result = self.parse_assignment_expr ()
      return result

   def parse_expr_list (self) :
      result = CmmExprList ()
      self.storeLocation (result)
      if self.set_0 [self.token] :
         result.items.append (self.parse_expr ())
         while self.tokenText == "," :
            self.check (",")
            result.items.append (self.parse_expr ())
      return result

   def parse_namespace_decl (self) :
      result = CmmNamespace ()
      self.storeLocation (result)
      self.check ("namespace")
      result.name = self.readIdentifier ()
      self.open_namespace (result)
      self.check ("{")
      while self.set_4 [self.token] :
         result.items.append (self.parse_decl ())
      self.check ("}")
      self.close_namespace (result)
      return result

   def parse_class_decl (self) :
      result = CmmClass ()
      self.storeLocation (result)
      self.begin_class (result)
      self.check ("class")
      result.name = self.readIdentifier ()
      self.open_class (result)
      self.check ("{")
      while self.token == self.identifier :
         result.items.append (self.parse_simple_decl ())
      self.check ("}")
      self.close_class (result)
      self.end_class (result)
      return result

   def parse_enum_decl (self) :
      result = CmmEnum ()
      self.storeLocation (result)
      self.check ("enum")
      result.name = self.readIdentifier ()
      self.open_enum (result)
      self.check ("{")
      result.items.append (self.parse_enum_item ())
      while self.tokenText == "," :
         self.check (",")
         result.items.append (self.parse_enum_item ())
      self.check ("}")
      self.close_enum (result)
      return result

   def parse_enum_item (self) :
      result = CmmEnumItem ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_enum_item (result)
      return result

   def parse_template_decl (self) :
      result = CmmTemplate ()
      self.storeLocation (result)
      self.begin_template (result)
      self.check ("template")
      self.check ("<")
      if self.token == self.identifier :
         result.items.append (self.parse_template_param ())
         while self.tokenText == "," :
            self.check (",")
            result.items.append (self.parse_template_param ())
         result.parameters = True
      self.check (">")
      result.inner_decl = self.parse_decl ()
      self.end_template (result)
      return result

   def parse_template_param (self) :
      result = CmmTemplateParam ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      return result

   def parse_simple_decl (self) :
      result = CmmSimpleDecl ()
      self.storeLocation (result)
      result.type = self.readIdentifier ()
      if self.tokenText == "*" :
         self.check ("*")
         result.pointer = True
      result.name = self.readIdentifier ()
      self.on_simple_decl (result)
      if self.tokenText == ";" or self.tokenText == "=" :
         if self.tokenText == "=" :
            self.check ("=")
            result.init_value = self.parse_expr ()
         self.check (";")
         result.variable = True
      elif self.tokenText == "{" :
         result.init_stat = self.parse_compound_stat ()
      elif self.tokenText == "(" :
         self.open_parameters (result)
         result.param_list = self.parse_parameter_list ()
         self.close_parameters (result)
         self.open_function (result)
         result.body = self.parse_compound_stat ()
         self.close_function (result)
      else :
         self.error ("Unexpected token")
      return result

   def parse_parameter_list (self) :
      result = CmmParamList ()
      self.storeLocation (result)
      self.check ("(")
      if self.token == self.identifier :
         result.items.append (self.parse_parameter_decl ())
         while self.tokenText == "," :
            self.check (",")
            result.items.append (self.parse_parameter_decl ())
      self.check (")")
      return result

   def parse_parameter_decl (self) :
      result = CmmParamDecl ()
      self.storeLocation (result)
      result.type = self.readIdentifier ()
      result.name = self.readIdentifier ()
      self.on_param_decl (result)
      return result

   def parse_empty_decl (self) :
      result = CmmEmptyDecl ()
      self.storeLocation (result)
      self.check (";")
      return result

   def parse_decl (self) :
      if self.tokenText == "namespace" :
         result = self.parse_namespace_decl ()
      elif self.tokenText == "class" :
         result = self.parse_class_decl ()
      elif self.tokenText == "enum" :
         result = self.parse_enum_decl ()
      elif self.tokenText == "template" :
         result = self.parse_template_decl ()
      elif self.token == self.identifier :
         result = self.parse_simple_decl ()
      elif self.tokenText == ";" :
         result = self.parse_empty_decl ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_program (self) :
      result = CmmDeclList ()
      self.storeLocation (result)
      self.on_start_program (result)
      while self.set_4 [self.token] :
         result.items.append (self.parse_decl ())
      return result

   def lookupKeyword (self) :
      s = self.tokenText
      n = len (s)
      if n == 2 :
         if s[0:2] == "if" :
            self.token = self.keyword_if
      elif n == 3 :
         if s[0] == 'd' :
            if s[1:3] == "cl" :
               self.token = self.keyword_dcl
         elif s[0] == 'f' :
            if s[1:3] == "or" :
               self.token = self.keyword_for
         elif s[0] == 'n' :
            if s[1:3] == "ew" :
               self.token = self.keyword_new
      elif n == 4 :
         if s[0] == 'e' :
            if s[1] == 'l' :
               if s[2:4] == "se" :
                  self.token = self.keyword_else
            elif s[1] == 'n' :
               if s[2:4] == "um" :
                  self.token = self.keyword_enum
         elif s[0] == 't' :
            if s[1:4] == "his" :
               self.token = self.keyword_this
      elif n == 5 :
         if s[0] == 'c' :
            if s[1:5] == "lass" :
               self.token = self.keyword_class
         elif s[0] == 'w' :
            if s[1:5] == "hile" :
               self.token = self.keyword_while
      elif n == 6 :
         if s[0] == 'd' :
            if s[1:6] == "elete" :
               self.token = self.keyword_delete
         elif s[0] == 'r' :
            if s[1:6] == "eturn" :
               self.token = self.keyword_return
      elif n == 8 :
         if s[0:8] == "template" :
            self.token = self.keyword_template
      elif n == 9 :
         if s[0:9] == "namespace" :
            self.token = self.keyword_namespace

   def processSeparator (self) :
      if self.tokenText == '!' :
         self.token = 21
         if self.ch == '=' :
            self.token = 22
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '%' :
         self.token = 23
      if self.tokenText == '&' :
         self.token = 24
         if self.ch == '&' :
            self.token = 25
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '(' :
         self.token = 26
      if self.tokenText == ')' :
         self.token = 27
      if self.tokenText == '*' :
         self.token = 28
      if self.tokenText == '+' :
         self.token = 29
         if self.ch == '+' :
            self.token = 30
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 31
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ',' :
         self.token = 32
      if self.tokenText == '-' :
         self.token = 33
         if self.ch == '-' :
            self.token = 34
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 35
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '>' :
            self.token = 36
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '.' :
         self.token = 37
      if self.tokenText == '/' :
         self.token = 38
      if self.tokenText == ';' :
         self.token = 39
      if self.tokenText == '<' :
         self.token = 40
         if self.ch == '<' :
            self.token = 41
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 42
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '=' :
         self.token = 43
         if self.ch == '=' :
            self.token = 44
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '>' :
         self.token = 45
         if self.ch == '=' :
            self.token = 46
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '>' :
            self.token = 47
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '[' :
         self.token = 48
      if self.tokenText == ']' :
         self.token = 49
      if self.tokenText == '^' :
         self.token = 50
      if self.tokenText == '{' :
         self.token = 51
      if self.tokenText == '|' :
         self.token = 52
         if self.ch == '|' :
            self.token = 53
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '}' :
         self.token = 54
      if self.tokenText == '~' :
         self.token = 55
      if self.token == self.separator :
         self.error ("Unknown separator")

   def tokenToString (self, value) :
      if value == 0: return "<end of source text>"
      if value == 1: return "<identifier>"
      if value == 2: return "<number>"
      if value == 3: return "<real_number>"
      if value == 4: return "<character_literal>"
      if value == 5: return "<string_literal>"
      if value == 6: return "<unknown separator>"
      if value == 7: return "<end of line>"
      if value == 8: return "class"
      if value == 9: return "dcl"
      if value == 10: return "delete"
      if value == 11: return "else"
      if value == 12: return "enum"
      if value == 13: return "for"
      if value == 14: return "if"
      if value == 15: return "namespace"
      if value == 16: return "new"
      if value == 17: return "return"
      if value == 18: return "template"
      if value == 19: return "this"
      if value == 20: return "while"
      if value == 21: return "!"
      if value == 22: return "!="
      if value == 23: return "%"
      if value == 24: return "&"
      if value == 25: return "&&"
      if value == 26: return "("
      if value == 27: return ")"
      if value == 28: return "*"
      if value == 29: return "+"
      if value == 30: return "++"
      if value == 31: return "+="
      if value == 32: return ","
      if value == 33: return "-"
      if value == 34: return "--"
      if value == 35: return "-="
      if value == 36: return "->"
      if value == 37: return "."
      if value == 38: return "/"
      if value == 39: return ";"
      if value == 40: return "<"
      if value == 41: return "<<"
      if value == 42: return "<="
      if value == 43: return "="
      if value == 44: return "=="
      if value == 45: return ">"
      if value == 46: return ">="
      if value == 47: return ">>"
      if value == 48: return "["
      if value == 49: return "]"
      if value == 50: return "^"
      if value == 51: return "{"
      if value == 52: return "|"
      if value == 53: return "||"
      if value == 54: return "}"
      if value == 55: return "~"
      return "<unknown symbol>"

   def storeLocation (self, item) :
      item.src_file = self.fileInx
      item.src_line = self.tokenLineNum
      item.src_column = self.tokenColNum
      item.src_pos = self.tokenByteOfs
      item.src_end = self.charByteOfs

   def alloc (self, items) :
      result = [False] * 56
      for item in items :
         result [item] = True
      return result

   def __init__ (self) :
      super (Parser, self).__init__ ()

      # eos = 0
      # identifier = 1
      # number = 2
      # real_number = 3
      # character_literal = 4
      # string_literal = 5
      # separator = 6
      # end_of_line = 7
      self.keyword_class = 8
      self.keyword_dcl = 9
      self.keyword_delete = 10
      self.keyword_else = 11
      self.keyword_enum = 12
      self.keyword_for = 13
      self.keyword_if = 14
      self.keyword_namespace = 15
      self.keyword_new = 16
      self.keyword_return = 17
      self.keyword_template = 18
      self.keyword_this = 19
      self.keyword_while = 20
      # ! 21
      # != 22
      # % 23
      # & 24
      # && 25
      # ( 26
      # ) 27
      # * 28
      # + 29
      # ++ 30
      # += 31
      # , 32
      # - 33
      # -- 34
      # -= 35
      # -> 36
      # . 37
      # / 38
      # ; 39
      # < 40
      # << 41
      # <= 42
      # = 43
      # == 44
      # > 45
      # >= 46
      # >> 47
      # [ 48
      # ] 49
      # ^ 50
      # { 51
      # | 52
      # || 53
      # } 54
      # ~ 55

      self.set_0 = self.alloc ([self.identifier, self.number, self.real_number, self.character_literal, self.string_literal, self.keyword_delete, self.keyword_new, self.keyword_this, 21, 24, 26, 28, 29, 30, 33, 34, 48, 55]) #  identifier  number  real_number  character_literal  string_literal  delete  new  this  !  &  (  *  +  ++  -  --  [  ~
      self.set_1 = self.alloc ([self.identifier, self.number, self.real_number, self.character_literal, self.string_literal, self.keyword_dcl, self.keyword_delete, self.keyword_for, self.keyword_if, self.keyword_new, self.keyword_return, self.keyword_this, self.keyword_while, 21, 24, 26, 28, 29, 30, 33, 34, 39, 48, 51, 55]) #  identifier  number  real_number  character_literal  string_literal  dcl  delete  for  if  new  return  this  while  !  &  (  *  +  ++  -  --  ;  [  {  ~
      self.set_2 = self.alloc ([self.identifier, self.number, self.real_number, self.character_literal, self.string_literal, self.keyword_this, 26, 48]) #  identifier  number  real_number  character_literal  string_literal  this  (  [
      self.set_3 = self.alloc ([40, 42, 45, 46]) #  <  <=  >  >=
      self.set_4 = self.alloc ([self.identifier, self.keyword_class, self.keyword_enum, self.keyword_namespace, self.keyword_template, 39]) #  identifier  class  enum  namespace  template  ;

   def on_variable_expr (self, item) :
      pass

   def on_field_expr (self, item) :
      pass

   def open_namespace (self, item) :
      pass

   def close_namespace (self, item) :
      pass

   def begin_class (self, item) :
      pass

   def open_class (self, item) :
      pass

   def close_class (self, item) :
      pass

   def end_class (self, item) :
      pass

   def open_enum (self, item) :
      pass

   def close_enum (self, item) :
      pass

   def on_enum_item (self, item) :
      pass

   def begin_template (self, item) :
      pass

   def end_template (self, item) :
      pass

   def on_simple_decl (self, item) :
      pass

   def open_parameters (self, item) :
      pass

   def close_parameters (self, item) :
      pass

   def open_function (self, item) :
      pass

   def close_function (self, item) :
      pass

   def on_param_decl (self, item) :
      pass

   def on_start_program (self, item) :
      pass

class CmmStat (object) :
   def __init__ (self) :
      pass

class CmmWhileStat (CmmStat) :
   def __init__ (self) :
      super (CmmWhileStat, self).__init__ ()
      self.cond = None
      self.body_stat = None

class CmmIfStat (CmmStat) :
   def __init__ (self) :
      super (CmmIfStat, self).__init__ ()
      self.cond = None
      self.then_stat = None
      self.else_stat = None

class CmmForStat (CmmStat) :
   def __init__ (self) :
      super (CmmForStat, self).__init__ ()
      self.from_expr = None
      self.cond_expr = None
      self.step_expr = None
      self.body_stat = None

class CmmReturnStat (CmmStat) :
   def __init__ (self) :
      super (CmmReturnStat, self).__init__ ()
      self.return_expr = None

class CmmCompoundStat (CmmStat) :
   def __init__ (self) :
      super (CmmCompoundStat, self).__init__ ()
      self.items = [ ]

class CmmSimpleStat (CmmStat) :
   def __init__ (self) :
      super (CmmSimpleStat, self).__init__ ()
      self.inner_expr = None

class CmmDeclStat (CmmStat) :
   def __init__ (self) :
      super (CmmDeclStat, self).__init__ ()
      self.inner_decl = None

class CmmEmptyStat (CmmStat) :
   def __init__ (self) :
      super (CmmEmptyStat, self).__init__ ()

class CmmExpr (object) :
   def __init__ (self) :
      pass

class CmmVarExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmVarExpr, self).__init__ ()
      self.name = ""

class CmmIntValue (CmmExpr) :
   def __init__ (self) :
      super (CmmIntValue, self).__init__ ()
      self.value = ""

class CmmRealValue (CmmExpr) :
   def __init__ (self) :
      super (CmmRealValue, self).__init__ ()
      self.value = ""

class CmmCharValue (CmmExpr) :
   def __init__ (self) :
      super (CmmCharValue, self).__init__ ()
      self.value = ""

class CmmStringValue (CmmExpr) :
   def __init__ (self) :
      super (CmmStringValue, self).__init__ ()
      self.value = ""

class CmmSubexprExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmSubexprExpr, self).__init__ ()
      self.inner_expr = None

class CmmSequenceExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmSequenceExpr, self).__init__ ()
      self.param = None

class CmmThisExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmThisExpr, self).__init__ ()

class CmmPostfixExpr (object) :
   def __init__ (self) :
      pass

class CmmIndexExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmIndexExpr, self).__init__ ()
      self.left = None
      self.param = None

class CmmCallExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmCallExpr, self).__init__ ()
      self.left = None
      self.param_list = None

class CmmCompoundExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmCompoundExpr, self).__init__ ()
      self.left = None
      self.body = None

class CmmFieldExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmFieldExpr, self).__init__ ()
      self.left = None
      self.name = ""

class CmmPtrFieldExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmPtrFieldExpr, self).__init__ ()
      self.left = None
      self.name = ""

class CmmPostIncExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmPostIncExpr, self).__init__ ()
      self.left = None

class CmmPostDecExpr (CmmPostfixExpr) :
   def __init__ (self) :
      super (CmmPostDecExpr, self).__init__ ()
      self.left = None

class CmmUnaryExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmUnaryExpr, self).__init__ ()
      self.param = None

class CmmNewExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmNewExpr, self).__init__ ()
      self.type = ""
      self.init_list = None

class CmmDeleteExpr (CmmExpr) :
   def __init__ (self) :
      super (CmmDeleteExpr, self).__init__ ()
      self.param = None

class CmmBinaryExpr (object) :
   def __init__ (self) :
      pass

class CmmMulExpr (CmmBinaryExpr) :
   mulExp = 0
   divExp = 1
   modExp = 2

   def __init__ (self) :
      super (CmmMulExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmAddExpr (CmmBinaryExpr) :
   addExp = 0
   subExp = 1

   def __init__ (self) :
      super (CmmAddExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmShiftExpr (CmmBinaryExpr) :
   shlExp = 0
   shrExp = 1

   def __init__ (self) :
      super (CmmShiftExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmRelExpr (CmmBinaryExpr) :
   ltExp = 0
   gtExp = 1
   leExp = 2
   geExp = 3

   def __init__ (self) :
      super (CmmRelExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmEqExpr (CmmBinaryExpr) :
   eqExp = 0
   neExp = 1

   def __init__ (self) :
      super (CmmEqExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmAndExpr (CmmBinaryExpr) :
   bitAndExp = 0

   def __init__ (self) :
      super (CmmAndExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmXorExpr (CmmBinaryExpr) :
   bitXorExp = 0

   def __init__ (self) :
      super (CmmXorExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmOrExpr (CmmBinaryExpr) :
   bitOrExp = 0

   def __init__ (self) :
      super (CmmOrExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmAndAndExpr (CmmBinaryExpr) :
   logAndExp = 0

   def __init__ (self) :
      super (CmmAndAndExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmOrOrExpr (CmmBinaryExpr) :
   logOrExp = 0

   def __init__ (self) :
      super (CmmOrOrExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmAssignExpr (CmmBinaryExpr) :
   assignExp = 0
   assignAddExp = 1
   assignSubExp = 2

   def __init__ (self) :
      super (CmmAssignExpr, self).__init__ ()
      self.left = None
      self.kind = None
      self.right = None

class CmmExprList (object) :
   def __init__ (self) :
      self.items = [ ]

class CmmDecl (object) :
   def __init__ (self) :
      pass

class CmmNamespace (CmmDecl) :
   def __init__ (self) :
      super (CmmNamespace, self).__init__ ()
      self.name = ""
      self.items = [ ]

class CmmClass (CmmDecl) :
   def __init__ (self) :
      super (CmmClass, self).__init__ ()
      self.name = ""
      self.items = [ ]

class CmmEnum (CmmDecl) :
   def __init__ (self) :
      super (CmmEnum, self).__init__ ()
      self.name = ""
      self.items = [ ]

class CmmEnumItem (CmmDecl) :
   def __init__ (self) :
      super (CmmEnumItem, self).__init__ ()
      self.name = ""

class CmmTemplate (CmmDecl) :
   def __init__ (self) :
      super (CmmTemplate, self).__init__ ()
      self.items = [ ]
      self.parameters = False
      self.inner_decl = None

class CmmTemplateParam (object) :
   def __init__ (self) :
      self.name = ""

class CmmSimpleDecl (CmmDecl) :
   def __init__ (self) :
      super (CmmSimpleDecl, self).__init__ ()
      self.type = ""
      self.pointer = False
      self.name = ""
      self.init_value = None
      self.variable = False
      self.init_stat = None
      self.param_list = None
      self.body = None

class CmmParamList (object) :
   def __init__ (self) :
      self.items = [ ]

class CmmParamDecl (CmmDecl) :
   def __init__ (self) :
      super (CmmParamDecl, self).__init__ ()
      self.type = ""
      self.name = ""

class CmmEmptyDecl (CmmDecl) :
   def __init__ (self) :
      super (CmmEmptyDecl, self).__init__ ()

class CmmDeclList (object) :
   def __init__ (self) :
      self.items = [ ]

