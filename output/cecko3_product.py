
from cecko3_parser import *
from easy_output import Output

class Product (Output) :

   def send_while_stat (self, param) :
      self.send ("while")
      self.send ("(")
      self.send_expr (param.cond)
      self.send (")")
      self.send_inner_stat (param.body_stat)

   def send_if_stat (self, param) :
      self.send ("if")
      self.send ("(")
      self.send_expr (param.cond)
      self.send (")")
      self.send_inner_stat (param.then_stat)
      if param.else_stat != None :
         self.send ("else")
         self.send_inner_stat (param.else_stat)

   def send_for_stat (self, param) :
      self.send ("for")
      self.send ("(")
      if param.from_expr != None :
         self.send_expr (param.from_expr)
      self.send (";")
      if param.cond_expr != None :
         self.send_expr (param.cond_expr)
      self.send (";")
      if param.step_expr != None :
         self.send_expr (param.step_expr)
      self.send (")")
      self.send_inner_stat (param.body_stat)

   def send_return_stat (self, param) :
      self.send ("return")
      if param.return_expr != None :
         self.send_expr (param.return_expr)
      self.send (";")

   def send_compound_stat (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("{")
      while inx < cnt :
         self.send_stat (param.items [inx])
         inx = inx + 1
      self.send ("}")

   def send_simple_stat (self, param) :
      self.send_expr (param.inner_expr)
      self.send (";")

   def send_decl_stat (self, param) :
      self.send ("dcl")
      self.send_simple_decl (param.inner_decl)

   def send_empty_stat (self, param) :
      self.send (";")

   def send_stat (self, param) :
      if isinstance (param, CmmDeclStat) :
         self.send_decl_stat (param)
      elif isinstance (param, CmmWhileStat) :
         self.send_while_stat (param)
      elif isinstance (param, CmmIfStat) :
         self.send_if_stat (param)
      elif isinstance (param, CmmForStat) :
         self.send_for_stat (param)
      elif isinstance (param, CmmReturnStat) :
         self.send_return_stat (param)
      elif isinstance (param, CmmCompoundStat) :
         self.send_compound_stat (param)
      elif isinstance (param, CmmSimpleStat) :
         self.send_simple_stat (param)
      elif isinstance (param, CmmEmptyStat) :
         self.send_empty_stat (param)

   def send_inner_stat (self, param) :
      self.send_stat (param)

   def send_variable_expr (self, param) :
      self.send (param.name)

   def send_int_value_expr (self, param) :
      self.send (param.value)

   def send_real_value_expr (self, param) :
      self.send (param.value)

   def send_char_value_expr (self, param) :
      self.sendChr (param.value)

   def send_string_value_expr (self, param) :
      self.sendStr (param.value)

   def send_subexpr_expr (self, param) :
      self.send ("(")
      self.send_expr (param.inner_expr)
      self.send (")")

   def send_sequence_expr (self, param) :
      self.send ("[")
      self.send_expr_list (param.param)
      self.send ("]")

   def send_this_expr (self, param) :
      self.send ("this")

   def send_simple_expr (self, param) :
      if isinstance (param, CmmVarExpr) :
         self.send_variable_expr (param)
      elif isinstance (param, CmmIntValue) :
         self.send_int_value_expr (param)
      elif isinstance (param, CmmRealValue) :
         self.send_real_value_expr (param)
      elif isinstance (param, CmmCharValue) :
         self.send_char_value_expr (param)
      elif isinstance (param, CmmStringValue) :
         self.send_string_value_expr (param)
      elif isinstance (param, CmmSubexprExpr) :
         self.send_subexpr_expr (param)
      elif isinstance (param, CmmSequenceExpr) :
         self.send_sequence_expr (param)
      elif isinstance (param, CmmThisExpr) :
         self.send_this_expr (param)

   def send_postfix_expr (self, param) :
      if isinstance (param, CmmIndexExpr) :
         self.send_postfix_expr (param.left)
         self.send_index_expr (param)
      elif isinstance (param, CmmCallExpr) :
         self.send_postfix_expr (param.left)
         self.send_call_expr (param)
      elif isinstance (param, CmmCompoundExpr) :
         self.send_postfix_expr (param.left)
         self.send_compound_expr (param)
      elif isinstance (param, CmmFieldExpr) :
         self.send_postfix_expr (param.left)
         self.send_field_expr (param)
      elif isinstance (param, CmmPtrFieldExpr) :
         self.send_postfix_expr (param.left)
         self.send_ptr_field_expr (param)
      elif isinstance (param, CmmPostIncExpr) :
         self.send_postfix_expr (param.left)
         self.send_post_inc_expr (param)
      elif isinstance (param, CmmPostDecExpr) :
         self.send_postfix_expr (param.left)
         self.send_post_dec_expr (param)
      else :
         self.send_simple_expr (param)

   def send_index_expr (self, param) :
      self.send ("[")
      self.send_expr_list (param.param)
      self.send ("]")

   def send_call_expr (self, param) :
      self.send ("(")
      self.send_expr_list (param.param_list)
      self.send (")")

   def send_compound_expr (self, param) :
      self.send_compound_stat (param.body)

   def send_field_expr (self, param) :
      self.send (".")
      self.send (param.name)

   def send_ptr_field_expr (self, param) :
      self.send ("->")
      self.send (param.name)

   def send_post_inc_expr (self, param) :
      self.send ("++")

   def send_post_dec_expr (self, param) :
      self.send ("--")

   def send_unary_expr (self, param) :
      if isinstance (param, CmmUnaryExpr) :
         self.send_inc_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_dec_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_deref_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_addr_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_plus_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_minus_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_bit_not_expr (param)
      elif isinstance (param, CmmUnaryExpr) :
         self.send_log_not_expr (param)
      elif isinstance (param, CmmNewExpr) :
         self.send_allocation_expr (param)
      elif isinstance (param, CmmDeleteExpr) :
         self.send_deallocation_expr (param)
      elif isinstance (param, CmmExpr) :
         self.send_postfix_expr (param)

   def send_inc_expr (self, param) :
      self.send ("++")
      self.send_unary_expr (param.param)

   def send_dec_expr (self, param) :
      self.send ("--")
      self.send_unary_expr (param.param)

   def send_deref_expr (self, param) :
      self.send ("*")
      self.send_unary_expr (param.param)

   def send_addr_expr (self, param) :
      self.send ("&")
      self.send_unary_expr (param.param)

   def send_plus_expr (self, param) :
      self.send ("+")
      self.send_unary_expr (param.param)

   def send_minus_expr (self, param) :
      self.send ("-")
      self.send_unary_expr (param.param)

   def send_bit_not_expr (self, param) :
      self.send ("~")
      self.send_unary_expr (param.param)

   def send_log_not_expr (self, param) :
      self.send ("!")
      self.send_unary_expr (param.param)

   def send_allocation_expr (self, param) :
      self.send ("new")
      self.send (param.type)
      if param.init_list != None :
         self.send ("(")
         self.send_expr_list (param.init_list)
         self.send (")")

   def send_deallocation_expr (self, param) :
      self.send ("delete")
      self.send_unary_expr (param.param)

   def send_multiplicative_expr (self, param) :
      if isinstance (param, CmmMulExpr) :
         self.send_multiplicative_expr (param.left)
         if param.kind == param.mulExp :
            self.send ("*")
         elif param.kind == param.divExp :
            self.send ("/")
         elif param.kind == param.modExp :
            self.send ("%")
         self.send_unary_expr (param.right)
      else :
         self.send_unary_expr (param)

   def send_additive_expr (self, param) :
      if isinstance (param, CmmAddExpr) :
         self.send_additive_expr (param.left)
         if param.kind == param.addExp :
            self.send ("+")
         elif param.kind == param.subExp :
            self.send ("-")
         self.send_multiplicative_expr (param.right)
      else :
         self.send_multiplicative_expr (param)

   def send_shift_expr (self, param) :
      if isinstance (param, CmmShiftExpr) :
         self.send_shift_expr (param.left)
         if param.kind == param.shlExp :
            self.send ("<<")
         elif param.kind == param.shrExp :
            self.send (">>")
         self.send_additive_expr (param.right)
      else :
         self.send_additive_expr (param)

   def send_relational_expr (self, param) :
      if isinstance (param, CmmRelExpr) :
         self.send_relational_expr (param.left)
         if param.kind == param.ltExp :
            self.send ("<")
         elif param.kind == param.gtExp :
            self.send (">")
         elif param.kind == param.leExp :
            self.send ("<=")
         elif param.kind == param.geExp :
            self.send (">=")
         self.send_shift_expr (param.right)
      else :
         self.send_shift_expr (param)

   def send_equality_expr (self, param) :
      if isinstance (param, CmmEqExpr) :
         self.send_equality_expr (param.left)
         if param.kind == param.eqExp :
            self.send ("==")
         elif param.kind == param.neExp :
            self.send ("!=")
         self.send_relational_expr (param.right)
      else :
         self.send_relational_expr (param)

   def send_and_expr (self, param) :
      if isinstance (param, CmmAndExpr) :
         self.send_and_expr (param.left)
         self.send ("&")
         self.send_equality_expr (param.right)
      else :
         self.send_equality_expr (param)

   def send_exclusive_or_expr (self, param) :
      if isinstance (param, CmmXorExpr) :
         self.send_exclusive_or_expr (param.left)
         self.send ("^")
         self.send_and_expr (param.right)
      else :
         self.send_and_expr (param)

   def send_inclusive_or_expr (self, param) :
      if isinstance (param, CmmOrExpr) :
         self.send_inclusive_or_expr (param.left)
         self.send ("|")
         self.send_exclusive_or_expr (param.right)
      else :
         self.send_exclusive_or_expr (param)

   def send_logical_and_expr (self, param) :
      if isinstance (param, CmmAndAndExpr) :
         self.send_logical_and_expr (param.left)
         self.send ("&&")
         self.send_inclusive_or_expr (param.right)
      else :
         self.send_inclusive_or_expr (param)

   def send_logical_or_expr (self, param) :
      if isinstance (param, CmmOrOrExpr) :
         self.send_logical_or_expr (param.left)
         self.send ("||")
         self.send_logical_and_expr (param.right)
      else :
         self.send_logical_and_expr (param)

   def send_assignment_expr (self, param) :
      if isinstance (param, CmmAssignExpr) :
         self.send_logical_or_expr (param.left)
         if param.kind == param.assignExp :
            self.send ("=")
         elif param.kind == param.assignAddExp :
            self.send ("+=")
         elif param.kind == param.assignSubExp :
            self.send ("-=")
         self.send_assignment_expr (param.right)
      else :
         self.send_logical_or_expr (param)

   def send_expr (self, param) :
      self.send_assignment_expr (param)

   def send_expr_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send_expr (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_expr (param.items [inx])
            inx = inx + 1

   def send_namespace_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("namespace")
      self.send (param.name)
      self.send ("{")
      while inx < cnt :
         self.send_decl (param.items [inx])
         inx = inx + 1
      self.send ("}")

   def send_class_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("class")
      self.send (param.name)
      self.send ("{")
      while inx < cnt :
         self.send_simple_decl (param.items [inx])
         inx = inx + 1
      self.send ("}")

   def send_enum_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("enum")
      self.send (param.name)
      self.send ("{")
      self.send_enum_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_enum_item (param.items [inx])
         inx = inx + 1
      self.send ("}")

   def send_enum_item (self, param) :
      self.send (param.name)

   def send_template_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("template")
      self.send ("<")
      if inx < cnt :
         self.send_template_param (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_template_param (param.items [inx])
            inx = inx + 1
      self.send (">")
      self.send_decl (param.inner_decl)

   def send_template_param (self, param) :
      self.send (param.name)

   def send_simple_decl (self, param) :
      self.send (param.type)
      if param.pointer == True :
         self.send ("*")
      self.send (param.name)
      if param.variable == True :
         if param.init_value != None :
            self.send ("=")
            self.send_expr (param.init_value)
         self.send (";")
      elif param.init_stat != None :
         self.send_compound_stat (param.init_stat)
      elif param.param_list != None :
         self.send_parameter_list (param.param_list)
         self.send_compound_stat (param.body)

   def send_parameter_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("(")
      if inx < cnt :
         self.send_parameter_decl (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_parameter_decl (param.items [inx])
            inx = inx + 1
      self.send (")")

   def send_parameter_decl (self, param) :
      self.send (param.type)
      self.send (param.name)

   def send_empty_decl (self, param) :
      self.send (";")

   def send_decl (self, param) :
      if isinstance (param, CmmNamespace) :
         self.send_namespace_decl (param)
      elif isinstance (param, CmmClass) :
         self.send_class_decl (param)
      elif isinstance (param, CmmEnum) :
         self.send_enum_decl (param)
      elif isinstance (param, CmmTemplate) :
         self.send_template_decl (param)
      elif isinstance (param, CmmSimpleDecl) :
         self.send_simple_decl (param)
      elif isinstance (param, CmmEmptyDecl) :
         self.send_empty_decl (param)

   def send_program (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_decl (param.items [inx])
         inx = inx + 1

