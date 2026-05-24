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

# Abstract Base Class:
# Una clase abstracta es una clase que funciona como plantilla. 
# No está pensada para usarse directamente, sino para obligar a 
# sus clases hijas a implementar ciertos métodos.

#%%
"""
================================================================ 
            A B S T R A C T   S Y N T A X   T R E E
================================================================
"""

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
    # Todo nodo del AST debe implementar accept().
    # accept() permite que un Visitor visite el nodo.
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass

class Literal(ASTNode):
    def __init__(self, value: Any, type: str) -> None:
        self.value = value
        self.type = type

    def accept(self, visitor: Visitor):
        visitor.visit_literal(self)

    def _str_(self):
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

    def _str_(self):
        return f"[{self.op}, {self.lhs}, {self.rhs}]"

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
    def visit_literal(self, node: Literal) -> None:
        pass
    @abstractmethod
    def visit_variable(self, node: Variable) -> None:
        pass
    @abstractmethod
    def visit_binary_op(self, node: BinaryOp) -> None:
        pass

class IRGenerator(Visitor):
    def __init__(self, builder, intType):
        self.stack = []
        self.builder = builder
        self.intType = intType

    def visit_literal(self, node: Literal) -> None:
        self.stack.append(
            ir.Constant(self.intType, node.value)
        )

    def visit_variable(self, node: Variable) -> None:
        pass

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)

        rhs = self.stack.pop()
        lhs = self.stack.pop()

        if node.op == '+':
            result = self.builder.add(lhs, rhs)
        elif node.op == '-':
            result = self.builder.sub(lhs, rhs)
        elif node.op == '*':
            result = self.builder.mul(lhs, rhs)
        elif node.op == '/':
            result = self.builder.sdiv(lhs, rhs)
        elif node.op == '%':
            result = self.builder.srem(lhs, rhs)
        else:
            raise ValueError(f"Operador desconocido: {node.op}")
        
        self.stack.append(result)

class Calculator(Visitor):
    def __init__(self):
        self.stack = []

    def visit_literal(self, node: Literal) -> None:
        self.stack.append(node.value)
    
    def visit_variable(self, node: Variable) -> None:
        pass

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)
        rhs = self.stack.pop()
        lhs = self.stack.pop()
        if node.op == '+':
            self.stack.append(lhs + rhs)
        elif node.op == '-':
            self.stack.append(lhs - rhs)
        elif node.op == '*':
            self.stack.append(lhs * rhs)
        elif node.op == '/':
            self.stack.append(lhs / rhs)
        elif node.op == '%':
            self.stack.append(lhs % rhs)

"""
================================================================ 
      F R E Q U E N T L Y   A S K E D   Q U E S T I O N S
================================================================

1. ¿Por qué 'Calculator' y 'IRGenerator' hereda 'Visitor' 
   y no 'ASTNodes'?
R: Porque las herencias de 'ASTNodes' son directamente partes
   del código fuente. Calculator es una herramienta que recorre
   el árbol. Las herencias de 'Visitor' son directamente funciones
   que saben recorrer el AST armado. Es decir, si tu quieres
   visitar cualquier parte del AST de cierta manera (en este caso
   hacer operaciones matemáticas mientras recorres el AST), debes
   de saber cómo recorrerlo bien.
"""
# %%
