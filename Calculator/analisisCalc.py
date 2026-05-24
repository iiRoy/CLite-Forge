#%%
"""
================================================================ 
                       L I B R A R I E S
================================================================
"""

import importlib
import arbolCalc
importlib.reload(arbolCalc)

import ply.lex as lex
import ply.yacc as yacc
from arbolCalc import Literal, BinaryOp, Calculator, IRGenerator, Visitor, Variable
from llvmlite import ir

# %%
"""
================================================================ 
                L E X E R   D E F I N I T I O N
================================================================
"""

literals = ['+', '-', '*', '/', '%', '(', ')']
tokens   = ['INTLIT']
t_ignore = ' \t'

def t_INTLIT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

#%%
"""
================================================================ 
            P A R S E R   D E F I N I T I O N
================================================================
"""

def p_Expression(p):
    """
    Expression : Expression '+' Term
               | Expression '-' Term
               | Term
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

def p_Term(p):
    """
    Term : Term '*' Factor
         | Term '/' Factor
         | Term '%' Factor
         | Factor
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

def p_Factor(p):
    """
    Factor : INTLIT
           | '(' Expression ')'
    """
    if len(p) == 2:
        p[0] = Literal(p[1], 'INT')
    else:
        p[0] = p[2]

def p_error(p):
    print("Syntax error in input!", p)



# %%
"""
================================================================ 
                        L L V M   I R
================================================================
"""

# Configuración inicial LLVM IR:
intType = ir.IntType(64) # Tipo Entero
module  = ir.Module(name="prog") # Archivo donde se guarda el módulo.

fnty    = ir.FunctionType(intType, []) # Función que retorna i64 y no recibe parámetros
func    = ir.Function(module, fnty, name='main') # Crea una función 'main'.
entry   = func.append_basic_block('entry') # Crea el bloque inicial del LLVM IR.
builder = ir.IRBuilder(entry) # Objeto que escribe instrucciones LLVM dentro del bloque entry.

# Definición
data = '10 + 5 * 3'

lexer  = lex.lex()
parser = yacc.yacc()

root = parser.parse(data)
irgen = IRGenerator()
root.accept(irgen)

# Al esperar un elemento LLVM, del método IRGenerator saca el
# elemento de la lista generada por la función para rescatar el
# LLVM generado para builder.ret. El resultado natural es una
# lista de Python, por lo que al sacar el único elemento de la
# lista, devuelve el LLVM completo.
result = irgen.stack.pop()
builder.ret(result)

print(module)
#print(irgen.stack) # Para ver cómo sale el resultado original.

# %%
"""
================================================================ 
                    C A L C U L A T O R
================================================================
"""

data = '10 + 5 * 3'
lexer  = lex.lex()
parser = yacc.yacc()

root = parser.parse(data)
calc = Calculator()
root.accept(calc)

print(calc.stack)

# %%
