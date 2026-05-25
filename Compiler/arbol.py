#%%
"""
================================================================ 
                       L I B R A R I E S
================================================================
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from llvmlite import ir

#%%
"""
================================================================ 
            A B S T R A C T   S Y N T A X   T R E E
================================================================
"""
# Abstract Base Class:
# Una clase abstracta es una clase que funciona como plantilla. 
# No está pensada para usarse directamente, sino para obligar a 
# sus clases hijas a implementar ciertos métodos.

"""
Ejemplo:

10 + 5 * 3

        +
       / \
     10   *
         / \
        5   3


BinaryOp(
    "+",
    Literal(10, "INT"),
    BinaryOp("*", Literal(5, "INT"), Literal(3, "INT"))
)


define i64 @"main"()
{
entry:
  %".2" = mul i64 5, 3
  %".3" = add i64 10, %".2"
  ret i64 %".3"
}
"""

# ASTNode es la plantilla base para todos los nodos del árbol.
# Como accept() es abstracto, cualquier clase que herede de ASTNode
# debe implementar su propia versión de accept().
class ASTNode(ABC):
    @abstractmethod
    # Todo nodo del AST debe implementar accept().
    # accept() permite que un Visitor visite el nodo.
    def accept(self, visitor: Visitor) -> None:
        pass

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                        R o o t
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class Program(ASTNode):
    def __init__(self, return_type: str, name: str, decls: Any, stmts: ASTNode) -> None:
        self.return_type = return_type
        self.name = name
        self.decls = decls
        self.stmts = stmts

    def accept(self, visitor: Visitor):
        visitor.visit_program(self)

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
               D e c l a r a t i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class Declaration(ASTNode):
    def __init__(self, var_type: str, name: str, initializer: ASTNode = None) -> None:
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor):
        visitor.visit_declaration(self)

    def __str__(self):
        return f"[DECL, {self.var_type}, {self.name}, {self.initializer}]"

class Declarations(ASTNode):
    def __init__(self, declarations: list[Declaration]) -> None:
        self.declarations = declarations

    def accept(self, visitor: Visitor):
        visitor.visit_declarations(self)

    def __str__(self):
        return f"[DECLS, {self.declarations}]"

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
        S t a t e m e n t    C o n t a i n e r
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class Statements(ASTNode):
    def __init__(self, statements: list[Assignment]) -> None:
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_statements(self)

    def __str__(self):
        return f"[STMTS, {self.statements}]"

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  S t a t e m e n t s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class Assignment(ASTNode):
    def __init__(self, variable: Any, expression: ASTNode) -> None:
        self.variable = variable
        self.expression = expression

    def accept(self, visitor: Visitor):
        visitor.visit_assignment(self)

    def __str__(self):
        return f"[ASSIGN, {self.variable}, {self.expression}]"

class Print(ASTNode):
    def __init__(self, args: list[ASTNode]) -> None:
        self.args = args

    def accept(self, visitor: Visitor):
        visitor.visit_print(self)

    def __str__(self):
        return f"[PRINT, {self.args}]"

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_stmts: Statements, else_stmts: Statements = None) -> None:
        self.condition = condition
        self.then_stmts = then_stmts
        self.else_stmts = else_stmts

    def accept(self, visitor: Visitor):
        visitor.visit_if_statement(self)

    def __str__(self):
        return f"[IF, {self.condition}, {self.then_stmts}, {self.else_stmts}]"

class SwitchCase(ASTNode):
    def __init__(self, value: int, statements: Statements) -> None:
        self.value = value
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_switch_case(self)

    def __str__(self):
        return f"[CASE, {self.value}, {self.statements}]"


class SwitchStatement(ASTNode):
    def __init__(self, expression: ASTNode, cases: list[SwitchCase], default_stmts: Statements = None) -> None:
        self.expression = expression
        self.cases = cases
        self.default_stmts = default_stmts

    def accept(self, visitor: Visitor):
        visitor.visit_switch_statement(self)

    def __str__(self):
        return f"[SWITCH, {self.expression}, {self.cases}, {self.default_stmts}]"


class Break(ASTNode):
    def accept(self, visitor: Visitor):
        visitor.visit_break(self)

    def __str__(self):
        return "[BREAK]"

class Return(ASTNode):
    def __init__(self, expression: ASTNode) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor):
        visitor.visit_return(self)

    def __str__(self):
        return f"[RETURN, {self.expression}]"

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                 E x p r e s s i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class BinaryOp(ASTNode):
    def __init__(self, op: str, lhs: ASTNode, rhs: ASTNode) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def accept(self, visitor: Visitor):
        visitor.visit_binary_op(self)

    def __str__(self):
        return f"[{self.op}, {self.lhs}, {self.rhs}]"

class CompareOp(ASTNode):
    def __init__(self, op: str, lhs: ASTNode, rhs: ASTNode) -> None:
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor: Visitor):
        visitor.visit_compare_op(self)

    def __str__(self):
        return f"[CMP, {self.op}, {self.lhs}, {self.rhs}]"

class UnaryOp(ASTNode):
    def __init__(self, op: str, expression: ASTNode) -> None:
        self.op = op
        self.expression = expression

    def accept(self, visitor: Visitor):
        visitor.visit_unary_op(self)

    def __str__(self):
        return f"[{self.op}, {self.expression}]"

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                   O p e r a n d s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
class Literal(ASTNode):
    def __init__(self, value: Any, type: str) -> None:
        self.value = value
        self.type = type

    def accept(self, visitor: Visitor):
        visitor.visit_literal(self)

    def __str__(self):
        return f"[LIT, {self.value}]"

class Variable(ASTNode):
    def __init__(self, name: Any, type: str) -> None:
        self.name = name
        self.type = type

    def accept(self, visitor: Visitor):
        visitor.visit_variable(self)

#%%
"""
================================================================ 
       V I S I T O R S   &   I M P L E M E N T A T I O N S
================================================================
"""
# Esta clase define qué métodos debe tener cualquier visitor.
# Es decir, si una clase quiere recorrer el AST, debe saber visitar
# todos sus elementos.
class Visitor(ABC):
    @abstractmethod
    def visit_program(self, node: Program) -> None:
        pass

    @abstractmethod
    def visit_literal(self, node: Literal) -> None:
        pass

    @abstractmethod
    def visit_declarations(self, node: Declarations) -> None:
        pass

    @abstractmethod
    def visit_declaration(self, node: Declaration) -> None:
        pass

    @abstractmethod
    def visit_statements(self, node: Statements) -> None:
        pass
    
    @abstractmethod
    def visit_variable(self, node: Variable) -> None:
        pass

    @abstractmethod
    def visit_binary_op(self, node: BinaryOp) -> None:
        pass

    @abstractmethod
    def visit_compare_op(self, node: CompareOp) -> None:
        pass

    @abstractmethod
    def visit_unary_op(self, node: UnaryOp) -> None:
        pass

    @abstractmethod
    def visit_assignment(self, node: Assignment) -> None:
        pass

    @abstractmethod
    def visit_print(self, node: Print) -> None:
        pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> None:
        pass

    @abstractmethod
    def visit_switch_statement(self, node: SwitchStatement) -> None:
        pass

    @abstractmethod
    def visit_switch_case(self, node: SwitchCase) -> None:
        pass

    @abstractmethod
    def visit_break(self, node: Break) -> None:
        pass

    @abstractmethod
    def visit_return(self, node: Return) -> None:
        pass

class IRGenerator(Visitor):
    def __init__(self, builder, intType, doubleType, stringType, boolType, module, return_type):
        # Pila temporal donde el IRGenerator guarda resultados mientras evalúa expresiones.
        # La pila guarda tuplas
        self.stack = []

        # Es la tabla de símbolos.
        # Sirve para recordar dónde vive cada variable.
        """
        self.symbol_table = {
            "x": (ptr_x, "int"),
            "y": (ptr_y, "double")
        }
        """
        # ptr_x y ptr_y son direcciones de memoria generadas con alloca.
        self.symbol_table = {}

        # Objeto que escribe instrucciones LLVM.
        self.builder = builder

        # Tipos de datos para el LLVM
        self.intType = intType
        self.doubleType = doubleType
        self.stringType = stringType
        self.boolType = ir.IntType(1)

        # Guardar el valor que aparece en un return
        self.return_type = return_type

        self.module = module
        self.string_count = 0

        # Guarda los bloques de SWITCH CASES que aún no han sido saltados
        self.break_blocks = []

        printf_type = ir.FunctionType(
            self.intType,
            [self.stringType],
            var_arg=True
        )

        self.printf = ir.Function(
            self.module,
            printf_type,
            name="printf"
        )
    
    def create_global_string(self, text: str):
        text = text + "\0"

        string_type = ir.ArrayType(ir.IntType(8), len(text))

        string_value = ir.Constant(
            string_type,
            bytearray(text.encode("utf8"))
        )

        name = f".str{self.string_count}"
        self.string_count = self.string_count + 1

        global_string = ir.GlobalVariable(
            self.module,
            string_type,
            name=name
        )

        global_string.linkage = "internal"
        global_string.global_constant = True
        global_string.initializer = string_value

        return self.builder.bitcast(global_string, self.stringType)

    def visit_literal(self, node: Literal) -> None:
        if node.type == "INT":
            value = ir.Constant(self.intType, node.value)
            self.stack.append((value, "int"))

        elif node.type == "DOUBLE":
            value = ir.Constant(self.doubleType, node.value)
            self.stack.append((value, "double"))
        
        elif node.type == "STRING":
            value = self.create_global_string(node.value)
            self.stack.append((value, "string"))

        elif node.type == "BOOL":
            value = ir.Constant(self.boolType, node.value)
            self.stack.append((value, "bool"))

    def visit_program(self, node: Program) -> None:
        node.decls.accept(self)
        node.stmts.accept(self)

    def visit_declarations(self, node: Declarations) -> None:
        for declaration in node.declarations:
            declaration.accept(self)

    def visit_declaration(self, node: Declaration) -> None:
        if node.var_type == "int":
            llvm_type = self.intType
            var_type = "int"
        elif node.var_type == "double":
            llvm_type = self.doubleType
            var_type = "double"
        elif node.var_type == "string":
            llvm_type = self.stringType
            var_type = "string"
        elif node.var_type == "bool":
            llvm_type = self.boolType
            var_type = "bool"
        else:
            raise ValueError(f"Tipo desconocido: {node.var_type}")

        #Reserva espacio en memoria para la variable.
        ptr = self.builder.alloca(llvm_type, name=node.name)
        #Guarda la dirección de la variable en symbol_table.
        self.symbol_table[node.name] = (ptr, var_type)

        """
        int x = 23 + 2;

        1. Reserva memoria para x. (Hecho anteriormente)
        2. Evalúa 23 + 2.
        3. El resultado de 23 + 2 queda en stack como (%".2", "int").
        4. Saca ese resultado.
        5. Lo guarda en x.
        """
        # Si tiene una asignación "="
        if node.initializer is not None:
            # Inicializador, acepta al IRGenerator para que te visite y genere tu valor LLVM.
            node.initializer.accept(self)

            #Extrae los últimos elementos de la pila
            value, value_type = self.stack.pop()

            if var_type == "double" and value_type == "int":
                value = self.builder.sitofp(value, self.doubleType)
                value_type = "double"

            elif var_type != value_type:
                raise TypeError(f"No se puede asignar '{value_type}' a '{var_type}'")

            self.builder.store(value, ptr)
        
        else:
            if var_type == "int":
                default_value = ir.Constant(self.intType, 0)
                self.builder.store(default_value, ptr)
            elif var_type == "double":
                default_value = ir.Constant(self.doubleType, 0.0)
                self.builder.store(default_value, ptr)
            elif var_type == "string":
                default_value = ir.Constant(self.stringType, None)
                self.builder.store(default_value, ptr)
            elif var_type == "bool":
                default_value = ir.Constant(self.boolType, 0)
                self.builder.store(default_value, ptr)
            else:
                raise ValueError(f"Tipo desconocido: {var_type}")

            self.builder.store(default_value, ptr)
    
    def visit_variable(self, node: Variable) -> None:
        #Recupera la dirección de memoria de la variable a guardar.
        ptr, var_type = self.symbol_table[node.name]
        #Carga el valor de la variable a través de la memoria.
        value = self.builder.load(ptr, name=node.name)
        #Guarda los cambios en la pila
        self.stack.append((value, var_type))

    def visit_statements(self, node: Statements) -> None:
        for statement in node.statements:
            if self.builder.block.is_terminated:
                break

            statement.accept(self)

    def visit_assignment(self, node: Assignment) -> None:
        node.expression.accept(self)

        value, value_type = self.stack.pop()
        #Recupera la dirección de memoria de la variable a guardar.
        ptr, var_type = self.symbol_table[node.variable]

        if var_type == "double" and value_type == "int":
            # Signed integer to floating point
            value = self.builder.sitofp(value, self.doubleType)
            value_type = "double"

        elif var_type == "int" and value_type == "double":
            raise TypeError("No se puede asignar 'DOUBLE' a 'INT' sin conversión explícita")

        elif var_type != value_type:
            raise TypeError(f"No se puede asignar '{value_type}' a '{var_type}'")

        #Guarda la nueva asignación de la variable
        self.builder.store(value, ptr)

        #Guarda los cambios en la pila
        self.stack.append((value, var_type))

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)

        rhs, rhs_type = self.stack.pop()
        lhs, lhs_type = self.stack.pop()

        invalid_types = {"string", "bool"}

        if lhs_type in invalid_types or rhs_type in invalid_types:
            raise TypeError(f"No se puede usar el operador {node.op} con {lhs_type} y {rhs_type}")

        if lhs_type == "double" or rhs_type == "double":
            if lhs_type == "int":
                # Signed integer to floating point
                lhs = self.builder.sitofp(lhs, self.doubleType)

            if rhs_type == "int":
                # Signed integer to floating point
                rhs = self.builder.sitofp(rhs, self.doubleType)

            if node.op == "+":
                result = self.builder.fadd(lhs, rhs)
            elif node.op == "-":
                result = self.builder.fsub(lhs, rhs)
            elif node.op == "*":
                result = self.builder.fmul(lhs, rhs)
            elif node.op == "/":
                result = self.builder.fdiv(lhs, rhs)
            else:
                raise ValueError(f"Operador no válido para double: {node.op}")

            self.stack.append((result, "double"))

        else:
            if node.op == "+":
                result = self.builder.add(lhs, rhs)
            elif node.op == "-":
                result = self.builder.sub(lhs, rhs)
            elif node.op == "*":
                result = self.builder.mul(lhs, rhs)
            elif node.op == "/":
                result = self.builder.sdiv(lhs, rhs)
            elif node.op == "%":
                result = self.builder.srem(lhs, rhs)
            else:
                raise ValueError(f"Operador desconocido: {node.op}")

            self.stack.append((result, "int"))

    def visit_compare_op(self, node: CompareOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)

        rhs, rhs_type = self.stack.pop()
        lhs, lhs_type = self.stack.pop()

        if lhs_type == "string" or rhs_type == "string":
            raise TypeError(f"No se puede comparar {lhs_type} con {rhs_type}")

        if lhs_type == "bool" or rhs_type == "bool":
            if lhs_type != rhs_type:
                raise TypeError(f"No se puede comparar {lhs_type} con {rhs_type}")

            result = self.builder.icmp_signed(node.op, lhs, rhs)
            self.stack.append((result, "bool"))
            return

        if lhs_type == "double" or rhs_type == "double":
            if lhs_type == "int":
                lhs = self.builder.sitofp(lhs, self.doubleType)

            if rhs_type == "int":
                rhs = self.builder.sitofp(rhs, self.doubleType)

            result = self.builder.fcmp_ordered(node.op, lhs, rhs)
            self.stack.append((result, "bool"))
            return

        result = self.builder.icmp_signed(node.op, lhs, rhs)
        self.stack.append((result, "bool"))

    def visit_unary_op(self, node: UnaryOp) -> None:
        node.expression.accept(self)

        value, value_type = self.stack.pop()

        if node.op == "!":
            if value_type != "bool":
                raise TypeError("El operador ! solo se puede usar con booleanos")

            result = self.builder.not_(value)
            self.stack.append((result, "bool"))

        else:
            raise ValueError(f"Operador unario desconocido: {node.op}")

    def visit_print(self, node: Print) -> None:
        if len(node.args) == 0:
            raise TypeError("printf necesita al menos un argumento")

        node.args[0].accept(self)
        fmt_value, fmt_type = self.stack.pop()

        if fmt_type != "string":
            raise TypeError("El primer argumento de printf debe ser un string")

        printf_args = [fmt_value]

        for arg in node.args[1:]:
            arg.accept(self)
            value, value_type = self.stack.pop()

            if value_type == "bool":
                value = self.builder.zext(value, self.intType)

            printf_args.append(value)

        self.builder.call(self.printf, printf_args)

    def visit_if_statement(self, node: IfStatement) -> None:
        node.condition.accept(self)

        condition, condition_type = self.stack.pop()

        if condition_type != "bool":
            raise TypeError("La condición del if debe ser bool")

        current_function = self.builder.function

        then_block = current_function.append_basic_block("if.then")
        merge_block = current_function.append_basic_block("if.end")

        if node.else_stmts is not None:
            else_block = current_function.append_basic_block("if.else")
        else:
            else_block = merge_block

        self.builder.cbranch(condition, then_block, else_block)

        # THEN
        self.builder.position_at_end(then_block)
        node.then_stmts.accept(self)

        then_terminated = self.builder.block.is_terminated

        if not then_terminated:
            self.builder.branch(merge_block)

        # ELSE
        else_terminated = False

        if node.else_stmts is not None:
            self.builder.position_at_end(else_block)
            node.else_stmts.accept(self)

            else_terminated = self.builder.block.is_terminated

            if not else_terminated:
                self.builder.branch(merge_block)

        # CONTINUACIÓN
        if node.else_stmts is not None and then_terminated and else_terminated:
            self.builder.position_at_end(merge_block)
            self.builder.unreachable()
        else:
            self.builder.position_at_end(merge_block)

    def visit_switch_statement(self, node: SwitchStatement) -> None:
        node.expression.accept(self)

        switch_value, switch_type = self.stack.pop()

        if switch_type != "int":
            raise TypeError("El switch por ahora solo acepta expresiones int")

        current_function = self.builder.function

        end_block = current_function.append_basic_block("switch.end")

        if node.default_stmts is not None:
            default_block = current_function.append_basic_block("switch.default")
        else:
            default_block = end_block

        switch_instr = self.builder.switch(switch_value, default_block)

        case_blocks = []

        for case in node.cases:
            case_block = current_function.append_basic_block(f"switch.case.{case.value}")
            case_blocks.append((case, case_block))

            case_value = ir.Constant(self.intType, case.value)
            switch_instr.add_case(case_value, case_block)

        self.break_blocks.append(end_block)

        for case, case_block in case_blocks:
            self.builder.position_at_end(case_block)
            case.statements.accept(self)

            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        if node.default_stmts is not None:
            self.builder.position_at_end(default_block)
            node.default_stmts.accept(self)

            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        self.break_blocks.pop()

        self.builder.position_at_end(end_block)

    def visit_switch_case(self, node: SwitchCase) -> None:
        node.statements.accept(self)

    def visit_break(self, node: Break) -> None:
        if not self.break_blocks:
            raise SyntaxError("break solo puede usarse dentro de switch")

        self.builder.branch(self.break_blocks[-1])

    def visit_return(self, node: Return) -> None:
        node.expression.accept(self)

        value, value_type = self.stack.pop()

        if self.return_type == "double" and value_type == "int":
            value = self.builder.sitofp(value, self.doubleType)
            value_type = "double"

        elif self.return_type != value_type:
            raise TypeError(f"No se puede retornar '{value_type}' desde una función '{self.return_type}'")

        self.builder.ret(value)
# %%
