#%%
"""
================================================================ 
                       L I B R A R I E S
================================================================
"""

import importlib
import arbol
importlib.reload(arbol)

# PLY sirve para construir analizadores léxicos y sintácticos en Python.
import ply.lex as lex
import ply.yacc as yacc

from arbol import Visitor, IRGenerator, Program, FunctionDefinition, Parameter, Declarations, Declaration, Statements, Literal, Variable, BinaryOp, Assignment, Return, Print, IfStatement, CompareOp, UnaryOp, SwitchStatement, SwitchCase, Break, WhileStatement, DoWhileStatement, ForStatement, LogicalOp, Call, CallStatement
from llvmlite import ir

#%%
"""
================================================================ 
                      F U N C T I O N S
================================================================
"""
def get_llvm_type(type_name):
    if type_name == "int":
        return intType
    elif type_name == "float":
        return floatType
    elif type_name == "string":
        return stringType
    elif type_name == "bool":
        return boolType
    else:
        raise ValueError(f"Tipo desconocido: {type_name}")

# %%
"""
================================================================ 
                L E X E R   D E F I N I T I O N
================================================================
"""

reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'string': 'STRING',
    'bool': 'BOOL',
    'true': 'TRUE',
    'false': 'FALSE',
    'return': 'RETURN',
    'printf': 'PRINTF',
    'if': 'IF',
    'else': 'ELSE',
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',
    'break': 'BREAK',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR'
}

tokens = ['ID', 'INTLIT', 'FLOATLIT', 'STRINGLIT', 'EQ', 'NE', 'LE', 'GE', 'AND', 'OR'] + list(reserved.values())
t_ignore = ' \t'

literals = '+-*/%(){},;=<>!:'

#Reconocimiento de nombres
"""
>>> REGLA:
Debe empezar con una letra o guion bajo.
Después puede tener letras, números o guion bajo.
"""
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    lower_value = t.value.lower()
    t.type = reserved.get(lower_value, 'ID')

    if t.type == 'TRUE':
        t.value = True
    elif t.type == 'FALSE':
        t.value = False
    return t

#Reconocimiento de números decimales
"""
REGLA:
Debe de ser número decimal positivo
"""
def t_FLOATLIT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

#Reconocimiento de strings
"""
REGLA:
Debe de estar entre comillas 
"""
def t_STRINGLIT(t):
    r'\"([^\"\\]|\\.)*\"|\'([^\'\\]|\\.)*\''
    t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
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

t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_AND = r'&&'
t_OR  = r'\|\|'

#Reconocimiento de saltos de lineas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#Reconocimiento de comentarios simples
def t_COMMENT_SINGLELINE(t):
    r'//.*'
    pass

#Reconocimiento de comentarios multilinea
def t_COMMENT_MULTILINE(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

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

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                    E s s e n t i a l
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Program(p):
    """
    Program : FunctionList
    """
    p[0] = Program(p[1])

def p_FunctionList_one(p):
    """
    FunctionList : FunctionDefinition
    """
    p[0] = [p[1]]


def p_FunctionList_many(p):
    """
    FunctionList : FunctionList FunctionDefinition
    """
    p[1].append(p[2])
    p[0] = p[1]

def p_FunctionDefinition(p):
    """
    FunctionDefinition : Type ID '(' Parameters ')' '{' Declarations Statements '}'
    """
    p[0] = FunctionDefinition(p[1], p[2], p[4], p[7], p[8])

def p_Parameters(p):
    """
    Parameters : ParameterList
               | empty
    """
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]


def p_ParameterList_one(p):
    """
    ParameterList : Parameter
    """
    p[0] = [p[1]]


def p_ParameterList_many(p):
    """
    ParameterList : ParameterList ',' Parameter
    """
    p[1].append(p[3])
    p[0] = p[1]


def p_Parameter(p):
    """
    Parameter : Type ID
    """
    p[0] = Parameter(p[1], p[2])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                        T y p e s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Type(p):
    """
    Type : INT
         | FLOAT 
         | STRING
         | BOOL
    """
    p[0] = p[1]

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                 D e c l a r a t i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

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
                | Type ID '=' Expression ';'
    """
    if len(p) == 4:
        p[0] = Declaration(p[1], p[2])
    else:
        p[0] = Declaration(p[1], p[2], p[4])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  S t a t e m e n t s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

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
                | Return
                | Print
                | IfStatement
                | SwitchStatement
                | Break
                | WhileStatement
                | DoWhileStatement
                | ForStatement
                | CallStatement
    """
    p[0] = p[1]

def p_CallStatement(p):
    """
    CallStatement : Call ';'
    """
    p[0] = CallStatement(p[1])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
    S t a t e m e n t    I m p l e m e n t a t i o n
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
def p_Assignment(p):
    """
    Assignment : ID '=' Expression ';'
    """
    p[0] = Assignment(p[1], p[3])

def p_IfStatement_if(p):
    """
    IfStatement : IF '(' Condition ')' '{' Statements '}'
    """
    p[0] = IfStatement(p[3], p[6], None)

def p_IfStatement_if_else(p):
    """
    IfStatement : IF '(' Condition ')' '{' Statements '}' ELSE '{' Statements '}'
    """
    p[0] = IfStatement(p[3], p[6], p[10])

def p_Print(p):
    """
    Print : PRINTF '(' Arguments ')' ';'
    """
    p[0] = Print(p[3])

def p_SwitchStatement(p):
    """
    SwitchStatement : SWITCH '(' Expression ')' '{' SwitchCases DefaultCase '}'
    """
    p[0] = SwitchStatement(p[3], p[6], p[7])

def p_SwitchCases(p):
    """
    SwitchCases : SwitchCases SwitchCase
                | empty
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_SwitchCase(p):
    """
    SwitchCase : CASE INTLIT ':' Statements
    """
    p[0] = SwitchCase(p[2], p[4])

def p_DefaultCase(p):
    """
    DefaultCase : DEFAULT ':' Statements
                | empty
    """
    if len(p) == 2:
        p[0] = None
    else:
        p[0] = p[3]

def p_Break(p):
    """
    Break : BREAK ';'
    """
    p[0] = Break()

def p_WhileStatement(p):
    """
    WhileStatement : WHILE '(' Condition ')' '{' Statements '}'
    """
    p[0] = WhileStatement(p[3], p[6])

def p_DoWhileStatement(p):
    """
    DoWhileStatement : DO '{' Statements '}' WHILE '(' Condition ')' ';'
    """
    p[0] = DoWhileStatement(p[3], p[7])

def p_ForStatement(p):
    """
    ForStatement : FOR '(' ForInit ';' Condition ';' ForUpdate ')' '{' Statements '}'
    """
    p[0] = ForStatement(p[3], p[5], p[7], p[10])

def p_ForInit(p):
    """
    ForInit : ID '=' Expression
            | empty
    """
    if len(p) == 2:
        p[0] = None
    else:
        p[0] = Assignment(p[1], p[3])

def p_ForUpdate(p):
    """
    ForUpdate : ID '=' Expression
              | empty
    """
    if len(p) == 2:
        p[0] = None
    else:
        p[0] = Assignment(p[1], p[3])

def p_Return(p):
    """
    Return : RETURN Expression ';'
    """
    p[0] = Return(p[2])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                    A r g u m e n t s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Arguments_one(p):
    """
    Arguments : Expression
    """
    p[0] = [p[1]]

def p_Arguments_many(p):
    """
    Arguments : Arguments ',' Expression
    """
    p[1].append(p[3])
    p[0] = p[1]

def p_OptionalArguments(p):
    """
    OptionalArguments : Arguments
                      | empty
    """
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1]

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  C o n d i t i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Condition_or(p):
    """
    Condition : Condition OR Conjunction
    """
    p[0] = LogicalOp("||", p[1], p[3])


def p_Condition_conjunction(p):
    """
    Condition : Conjunction
    """
    p[0] = p[1]


def p_Conjunction_and(p):
    """
    Conjunction : Conjunction AND BoolFactor
    """
    p[0] = LogicalOp("&&", p[1], p[3])


def p_Conjunction_bool_factor(p):
    """
    Conjunction : BoolFactor
    """
    p[0] = p[1]


def p_BoolFactor_compare(p):
    """
    BoolFactor : Expression '<' Expression
               | Expression '>' Expression
               | Expression EQ Expression
               | Expression NE Expression
               | Expression LE Expression
               | Expression GE Expression
    """
    p[0] = CompareOp(p[2], p[1], p[3])


def p_BoolFactor_expression(p):
    """
    BoolFactor : Expression
    """
    p[0] = p[1]

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  E x p r e s s i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
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

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                     F a c t o r s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Factor_int(p):
    """
    Factor : INTLIT
    """
    p[0] = Literal(p[1], "INT")


def p_Factor_float(p):
    """
    Factor : FLOATLIT
    """
    p[0] = Literal(p[1], "FLOAT")


def p_Factor_string(p):
    """
    Factor : STRINGLIT
    """
    p[0] = Literal(p[1], "STRING")

def p_Factor_bool(p):
    """
    Factor : TRUE
           | FALSE
    """
    p[0] = Literal(p[1], "BOOL")

def p_Factor_not(p):
    """
    Factor : '!' Factor
    """
    p[0] = UnaryOp('!', p[2])

def p_Factor_unary_minus(p):
    """
    Factor : '-' Factor
    """
    p[0] = UnaryOp("-", p[2])

def p_Factor_variable(p):
    """
    Factor : ID
    """
    p[0] = Variable(p[1], None)


def p_Factor_group(p):
    """
    Factor : '(' Expression ')'
    """
    p[0] = p[2]

def p_Call(p):
    """
    Call : ID '(' OptionalArguments ')'
    """
    p[0] = Call(p[1], p[3])

def p_Factor_call(p):
    """
    Factor : Call
    """
    p[0] = p[1]

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                      H e l p e r s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
def p_empty(p):
    """
    empty :
    """
    p[0] = None

def p_error(p):
    if p:
        print(f"Syntax error: token={p.type}, value={p.value}, line={p.lineno}")
    else:
        print("Syntax error: unexpected end of input")

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
tree.return_type
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
int factorial(int n)
{
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}

int main()
{
    int result = factorial(5);
    return result;
}
"""

lexer = lex.lex()
parser = yacc.yacc()
tree = parser.parse(data, lexer=lexer)

if tree is None:
    raise SyntaxError("El parser no pudo construir el AST.")


# Configuración inicial LLVM IR:
intType = ir.IntType(32)
floatType = ir.FloatType()
stringType = ir.IntType(8).as_pointer()
boolType = ir.IntType(1)

module = ir.Module(name="prog")


# PRIMERA PASADA:
# Crear las firmas LLVM de todas las funciones.
function_table = {}

for function_node in tree.functions:
    if function_node.name in function_table:
        raise NameError(f"La función '{function_node.name}' ya fue declarada")

    returnType = get_llvm_type(function_node.return_type)

    param_types = []

    for param in function_node.params:
        param_types.append(get_llvm_type(param.var_type))

    fnty = ir.FunctionType(returnType, param_types)
    llvm_func = ir.Function(module, fnty, name=function_node.name)

    for llvm_arg, param in zip(llvm_func.args, function_node.params):
        llvm_arg.name = param.name

    function_table[function_node.name] = (
        llvm_func,
        function_node.return_type,
        [param.var_type for param in function_node.params]
    )


if "main" not in function_table:
    raise NameError("El programa debe tener una función main")


# SEGUNDA PASADA:
# Generar el cuerpo de cada función.
for function_node in tree.functions:
    llvm_func, return_type, param_types = function_table[function_node.name]

    block = llvm_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    irgen = IRGenerator(
        builder,
        intType,
        floatType,
        stringType,
        boolType,
        module,
        function_node.return_type,
        function_table
    )

    function_node.accept(irgen)

    if not builder.block.is_terminated:
        raise TypeError(
            f"La función '{function_node.name}' no tiene return en todos los caminos"
        )


print(module)
# %%