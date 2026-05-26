#%%
"""
================================================================ 
                       L I B R A R I E S
================================================================
"""

# PLY sirve para construir analizadores léxicos y sintácticos en Python.
import ply.lex as lex
import ply.yacc as yacc

from arbol import Visitor, IRGenerator, Program, Declarations, Declaration, Statements, Literal, Variable, BinaryOp, Assignment, Return, Print, IfStatement, CompareOp, UnaryOp, SwitchStatement, SwitchCase, Break, WhileStatement, DoWhileStatement, ForStatement
from llvmlite import ir

# %%
"""
================================================================ 
                L E X E R   D E F I N I T I O N
================================================================
"""

reserved = {
    'int': 'INT',
    'double': 'DOUBLE',
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

tokens = ['ID', 'INTLIT', 'DOUBLELIT', 'STRINGLIT', 'EQ', 'NE', 'LE', 'GE'] + list(reserved.values())
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
def t_DOUBLELIT(t):
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
    Program : Type ID '(' ')' '{' Declarations Statements '}'
    """
    p[0] = Program(p[1], p[2], p[6], p[7])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                        T y p e s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Type(p):
    """
    Type : INT
         | DOUBLE 
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
    """
    p[0] = p[1]

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

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  C o n d i t i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Condition_compare(p):
    """
    Condition : Expression '<' Expression
              | Expression '>' Expression
              | Expression EQ Expression
              | Expression NE Expression
              | Expression LE Expression
              | Expression GE Expression
    """
    p[0] = CompareOp(p[2], p[1], p[3])


def p_Condition_bool(p):
    """
    Condition : Expression
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


def p_Factor_double(p):
    """
    Factor : DOUBLELIT
    """
    p[0] = Literal(p[1], "DOUBLE")


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
double main()
{
    // MAIN DECLARATIONS
    double x = 10 - 0.5;
    int y = 2;
    double z;

    // CASE 1: IF STATEMENT
    /*
    bool a = TRUE;

    if (true == !a) {
        z = x + y;
    } else {
        return 0;
    }
    */

    // CASE 2: SWITCH STATEMENT
    /*
    switch (y) {
        case 1:
            z = 10;
            return 1;

        case 2:
            z = x + y;
            break;

        default:
            return 0;
    }
    */

    // CASE 3: WHILE STATEMENT
    /*
    while (x < 15) {
        x = x + 1;
    }
    */

    // CASE 4: DO WHILE STATEMENT
    /*
    do {
        x = x - 1;
    } while (x > 5);
    */

    // CASE 5: FOR WHILE STATEMENT

    int i;
    for (i = 0; i < 5; i = i + 1) {
        x = x + i;
    }

    //END CASE
    printf("z = %i\n", z);
    return z;
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
stringType = ir.IntType(8).as_pointer()
boolType = ir.IntType(1)

if tree.return_type == "int":
    returnType = intType
elif tree.return_type == "double":
    returnType = doubleType
elif tree.return_type == "string":
    returnType = stringType
elif tree.return_type == "bool":
    returnType = boolType
else:
    raise ValueError(f"Tipo de retorno desconocido: {tree.return_type}")

module = ir.Module(name="prog")

fnty = ir.FunctionType(returnType, [])
func = ir.Function(module, fnty, name=tree.name)

block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)

print(tree)

irgen = IRGenerator(builder, intType, doubleType, stringType, boolType, module, tree.return_type)
tree.accept(irgen)

if not builder.block.is_terminated:
    raise TypeError("La función no tiene return en todos los caminos")

print(module)
# %%
