#%%
"""
================================================================ 
                       L I B R A R I E S
================================================================
"""

# PLY sirve para construir analizadores léxicos y sintácticos en Python.
import ply.lex as lex
import ply.yacc as yacc

from arbol import Visitor, IRGenerator, Program, Declarations, Declaration, Statements, Literal, Variable, BinaryOp, Assignment
from llvmlite import ir

# %%
"""
================================================================ 
                L E X E R   D E F I N I T I O N
================================================================
"""

reserved = {
    'int': 'INT',
    'double': 'DOUBLE'
}

tokens = ['ID', 'INTLIT', 'DOUBLELIT'] + list(reserved.values())
t_ignore = ' \t'

literals = '+-*/%(){},;='

#Reconocimiento de nombres
"""
>>> REGLA:
Debe empezar con una letra o guion bajo.
Después puede tener letras, números o guion bajo.
"""
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

#Reconocimiento de números decimales
"""
REGLA:
Debe de ser número decimal positivo
"""
def t_DOUBLELIT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t


#Reconocimiento de números
"""
REGLA:
Debe de ser número entero positivo
"""
def t_INTLIT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

#Reconocimiento de saltos de lineas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#Reconocimiento de errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

#%%
"""
================================================================ 
            P A R S E R   D E F I N I T I O N
================================================================
"""

def p_Program(p):
    """
    Program : Type ID '(' ')' '{' Declarations Statements '}'
    """
    p[0] = Program(p[1], p[2], p[6], p[7])

def p_Declarations(p):
    """
    Declarations : Declarations Declaration
                 | empty
    """
    if len(p) == 2:
        p[0] = Declarations([])
    else:
        p[1].declarations.append(p[2])
        p[0] = p[1]
#VER NOTA 1

def p_Declaration(p):
    """
    Declaration : Type ID ';'
    """
    p[0] = Declaration(p[1], p[2])


def p_Statements(p):
    """
    Statements : Statements Statement
               | empty
    """
    if len(p) == 2:
        p[0] = Statements([])
    else:
        p[1].statements.append(p[2])
        p[0] = p[1]
#VER NOTA 1

def p_Statement(p):
    """
    Statement : Assignment
    """
    p[0] = p[1]


def p_Assignment(p):
    """
    Assignment : ID '=' Expression ';'
    """
    p[0] = Assignment(p[1], p[3])

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
           | DOUBLELIT
           | ID
           | '(' Expression ')'
    """
    if len(p) == 2:
        if isinstance(p[1], int):
            p[0] = Literal(p[1], 'INT')
        elif isinstance(p[1], float):
            p[0] = Literal(p[1], 'DOUBLE')
        else:
            p[0] = Variable(p[1], None)
    else:
        p[0] = p[2]

def p_Type(p):
    """
    Type : INT
         | DOUBLE
    """
    p[0] = p[1]

def p_empty(p):
    """
    empty :
    """
    p[0] = None

def p_error(p):
    print("Syntax error in input!", p)

#%%
"""
================================================================ 
                     N O T A S   P A R S E R
================================================================
"""

"""
>>> CONCEPTOS IMPORTANTES:
Cuando el parser reconoce un elemento de la gramática completo, 
construye un nodo del elemento del AST usando las 
partes importantes que encontró.

Ejemplo con p_Program(p)

p[0] = resultado final de la regla 'Program'
p[1] = primer ID        → int
p[2] = segundo ID       → main
p[3] = (
p[4] = )
p[5] = {
p[6] = Declarations    → declaraciones de variables
p[7] = Statements      → instrucciones del programa
p[8] = }

Al nosotros definir "p[0] = Program(p[6], p[7])", 
construye un objeto Program, que será un nodo del 
AST, usando los nodos que ya fueron construidos por 
las reglas Declarations y Statements.:

Program(
    decls = p[6],
    stmts = p[7]
)

p[6] y p[7] no son texto plano.
Son los resultados que dejaron otras reglas del parser.

p[6] viene de la regla Declarations
p[7] viene de la regla Statements
"""

"""
>>> NOTA 1:
'Program' espera encontrar una parte llamada Declarations.

Declarations representa cero o más declaraciones. Por eso 
su regla tiene dos casos:
1. empty
2. Declarations Declaration

El caso empty sirve como punto de inicio: crea una lista vacía 
de declaraciones.

Cuando el parser encuentra una declaración como:
int x;
la reconoce con la regla:
Declaration : ID ID ';'

Entonces el parser puede combinar:
Declarations([]) + Declaration("int", "x")
usando la regla:
Declarations : Declarations Declaration

En ese momento agrega la nueva Declaration a la lista interna 
de Declarations. Así, Declarations pasa de ser:
Declarations([])
a:
Declarations([
    Declaration("int", "x")
])
"""

# %%

"""
================================================================ 
                        L L V M   I R
================================================================
"""

data = """
double main()
{
    int x;
    int y;
    int z;

    x = 10;
    y = 2;
    z = x + y;

}
"""
lexer = lex.lex()
parser = yacc.yacc()
tree = parser.parse(data, lexer=lexer)

if tree is None:
    raise SyntaxError("El parser no pudo construir el AST.")

# Configuración inicial LLVM IR:
intType = ir.IntType(32)
doubleType = ir.DoubleType()

if tree.return_type == "int":
    returnType = intType
elif tree.return_type == "double":
    returnType = doubleType
else:
    raise ValueError(f"Tipo de retorno desconocido: {tree.return_type}")

module = ir.Module(name="prog")

fnty = ir.FunctionType(returnType, [])
func = ir.Function(module, fnty, name=tree.name)

block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)

print(tree)

irgen = IRGenerator(builder, intType, doubleType)
tree.accept(irgen)

result, result_type = irgen.stack.pop()
if tree.return_type == "double" and result_type == "int":
    # Signed integer to floating point
    result = builder.sitofp(result, doubleType)

elif tree.return_type == "int" and result_type == "double":
    raise TypeError("No se puede retornar double desde una función 'INT' sin conversión explícita")

builder.ret(result)

print(module)
# %%
