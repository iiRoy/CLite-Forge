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

class Program(ASTNode):
    def __init__(self, return_type: str, name: str, decls: Any, stmts: ASTNode) -> None:
        self.return_type = return_type
        self.name = name
        self.decls = decls
        self.stmts = stmts

    def accept(self, visitor: Visitor):
        visitor.visit_program(self)

class Declaration(ASTNode):
    def __init__(self, var_type: str, name: str) -> None:
        self.var_type = var_type
        self.name = name

    def accept(self, visitor: Visitor):
        visitor.visit_declaration(self)

    def __str__(self):
        return f"[DECL, {self.var_type}, {self.name}]"

class Declarations(ASTNode):
    def __init__(self, declarations: list[Declaration]) -> None:
        self.declarations = declarations

    def accept(self, visitor: Visitor):
        visitor.visit_declarations(self)

    def __str__(self):
        return f"[DECLS, {self.declarations}]"

class Statements(ASTNode):
    def __init__(self, statements: list[Assignment]) -> None:
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_statements(self)

    def __str__(self):
        return f"[STMTS, {self.statements}]"

class Assignment(ASTNode):
    def __init__(self, variable: Any, expression: ASTNode) -> None:
        self.variable = variable
        self.expression = expression

    def accept(self, visitor: Visitor):
        visitor.visit_assignment(self)

    def __str__(self):
        return f"[ASSIGN, {self.variable}, {self.expression}]"

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

class BinaryOp(ASTNode):
    def __init__(self, op: str, lhs: ASTNode, rhs: ASTNode) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def accept(self, visitor: Visitor):
        visitor.visit_binary_op(self)

    def __str__(self):
        return f"[{self.op}, {self.lhs}, {self.rhs}]"

class Return(ASTNode):
    def __init__(self, expression: ASTNode) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor):
        visitor.visit_return(self)

    def __str__(self):
        return f"[RETURN, {self.expression}]"

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
    def visit_assignment(self, node: Assignment) -> None:
        pass

    @abstractmethod
    def visit_return(self, node: Return) -> None:
        pass

class IRGenerator(Visitor):
    def __init__(self, builder, intType, doubleType, stringType, boolType):
        self.stack = []
        self.symbol_table = {}
        self.builder = builder
        self.intType = intType
        self.doubleType = doubleType
        self.stringType = stringType
        self.boolType = ir.IntType(1)
        self.return_value = None

    def visit_literal(self, node: Literal) -> None:
        if node.type == "INT":
            value = ir.Constant(self.intType, node.value)
            self.stack.append((value, "int"))

        elif node.type == "DOUBLE":
            value = ir.Constant(self.doubleType, node.value)
            self.stack.append((value, "double"))
        
        elif node.type == "STRING":
            value = ir.Constant(self.stringType, node.value)
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
        elif node.var_type == "string" or node.var_type == "str":
            llvm_type = self.stringType
            var_type = "string"
        elif node.var_type == "bool":
            llvm_type = self.boolType
            var_type = "bool"
        else:
            raise ValueError(f"Tipo desconocido: {node.var_type}")

        ptr = self.builder.alloca(llvm_type, name=node.name)
        self.symbol_table[node.name] = (ptr, var_type)
    
    def visit_variable(self, node: Variable) -> None:
        ptr, var_type = self.symbol_table[node.name]
        value = self.builder.load(ptr, name=node.name)
        self.stack.append((value, var_type))

    def visit_statements(self, node: Statements) -> None:
        for statement in node.statements:
            statement.accept(self)

            if self.return_value is not None:
                break

    def visit_assignment(self, node: Assignment) -> None:
        node.expression.accept(self)

        value, value_type = self.stack.pop()
        ptr, var_type = self.symbol_table[node.variable]

        if var_type == "double" and value_type == "int":
            # Signed integer to floating point
            value = self.builder.sitofp(value, self.doubleType)
            value_type = "double"

        elif var_type == "int" and value_type == "double":
            raise TypeError("No se puede asignar 'DOUBLE' a 'INT' sin conversión explícita")

        elif var_type != value_type:
            raise TypeError(f"No se puede asignar '{value_type}' a '{var_type}'")

        self.builder.store(value, ptr)

        self.stack.append((value, var_type))

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)

        rhs, rhs_type = self.stack.pop()
        lhs, lhs_type = self.stack.pop()

        if lhs_type == "string" or rhs_type == "string":
            raise TypeError(f"No se puede usar el operador {node.op} con strings")

        if lhs_type == "bool" or rhs_type == "bool":
            raise TypeError(f"No se puede usar el operador {node.op} con strings")

        if lhs_type == "double" or rhs_type == "double":
            if lhs_type == "int":
                lhs = self.builder.sitofp(lhs, self.doubleType)

            if rhs_type == "int":
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
        
    def visit_return(self, node: Return) -> None:
        node.expression.accept(self)

        value, value_type = self.stack.pop()
        self.return_value = (value, value_type)
# %%
