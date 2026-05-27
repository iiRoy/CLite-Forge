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

from arbol import Visitor, IRGenerator, Program, FunctionDefinition, Parameter, Declarations, Declaration, Statements, Literal, Variable, BinaryOp, Assignment, Return, Print, IfStatement, CompareOp, UnaryOp, SwitchStatement, SwitchCase, Break, WhileStatement, DoWhileStatement, ForStatement, LogicalOp, Call, CallStatement, BlockStatement, EmptyStatement, ArrayAccess, GlobalDeclaration
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
    elif type_name == "char":
        return charType
    elif type_name == "void":
        return ir.VoidType()
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
    'char': 'CHAR',
    'void': 'VOID',
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

tokens = ['ID', 'INTLIT', 'FLOATLIT', 'STRINGLIT', 'CHARLIT', 'EQ', 'NE', 'LE', 'GE', 'AND', 'OR'] + list(reserved.values())
t_ignore = ' \t'

literals = '+-*/%(){}[],;=<>!:'

precedence = (
    ('nonassoc', 'IFX'),
    ('nonassoc', 'ELSE'),
)

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
Debe de estar entre comillas dobles y debe de ser un arreglo de chars
"""
def t_STRINGLIT(t):
    r'\"([^\"\\]|\\.)*\"'
    t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
    return t

#Reconocimiento de chars
"""
REGLA:
Debe de estar entre comillas simples y debe de ser solo un carácter
"""
def t_CHARLIT(t):
    r"'([^'\\]|\\.)'"
    char_text = t.value[1:-1]
    char_text = bytes(char_text, "utf-8").decode("unicode_escape")

    if len(char_text) != 1:
        raise ValueError("Un char debe contener exactamente un carácter")

    t.value = ord(char_text)
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

# Ignorar directivas de preprocesador como #include <stdio.h>
def t_PREPROCESSOR(t):
    r'\#[^\n]*'
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
    Program : ProgramItems
    """
    p[0] = Program(p[1])


def p_ProgramItems_one(p):
    """
    ProgramItems : ProgramItem
    """
    p[0] = [p[1]]


def p_ProgramItems_many(p):
    """
    ProgramItems : ProgramItems ProgramItem
    """
    p[1].append(p[2])
    p[0] = p[1]


def p_ProgramItem_typed(p):
    """
    ProgramItem : Type ID ProgramItemTail
    """
    if p[3][0] == "function":
        params = p[3][1]
        block = p[3][2]

        p[0] = FunctionDefinition(
            p[1],
            p[2],
            params,
            block.decls,
            block.stmts
        )

    else:
        first_array_size = p[3][1]
        rest_decls = p[3][2]

        first_decl = Declaration(
            p[1],
            p[2],
            array_size=first_array_size
        )

        for decl in rest_decls:
            decl.var_type = p[1]

        p[0] = GlobalDeclaration([first_decl] + rest_decls)


def p_ProgramItem_void_function(p):
    """
    ProgramItem : VOID ID '(' Parameters ')' BlockStatement
    """
    p[0] = FunctionDefinition(
        p[1],
        p[2],
        p[4],
        p[6].decls,
        p[6].stmts
    )


def p_ProgramItemTail_function(p):
    """
    ProgramItemTail : '(' Parameters ')' BlockStatement
    """
    p[0] = ("function", p[2], p[4])


def p_ProgramItemTail_global(p):
    """
    ProgramItemTail : DeclaratorSuffix GlobalDeclaratorTail ';'
    """
    p[0] = ("global", p[1], p[2])


def p_DeclaratorSuffix_array(p):
    """
    DeclaratorSuffix : '[' INTLIT ']'
    """
    p[0] = p[2]


def p_DeclaratorSuffix_empty(p):
    """
    DeclaratorSuffix : empty
    """
    p[0] = None


def p_GlobalDeclaratorTail_many(p):
    """
    GlobalDeclaratorTail : ',' Declarator GlobalDeclaratorTail
    """
    p[0] = [p[2]] + p[3]


def p_GlobalDeclaratorTail_empty(p):
    """
    GlobalDeclaratorTail : empty
    """
    p[0] = []

def p_Parameters(p):
    """
    Parameters : ParameterList
               | VOID
               | empty
    """
    if p[1] is None:
        p[0] = []
    elif p[1] == "void":
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
         | CHAR
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
        p[1].declarations.extend(p[2])
        p[0] = p[1]
#VER NOTA 1

def p_Declaration(p):
    """
    Declaration : Type DeclaratorList ';'
                | Type ID '=' Expression ';'
    """
    if len(p) == 4:
        p[0] = p[2]
        for decl in p[0]:
            decl.var_type = p[1]
    else:
        p[0] = [Declaration(p[1], p[2], p[4])]


def p_DeclaratorList_one(p):
    """
    DeclaratorList : Declarator
    """
    p[0] = [p[1]]


def p_DeclaratorList_many(p):
    """
    DeclaratorList : DeclaratorList ',' Declarator
    """
    p[1].append(p[3])
    p[0] = p[1]


def p_Declarator_variable(p):
    """
    Declarator : ID
    """
    p[0] = Declaration(None, p[1])


def p_Declarator_array(p):
    """
    Declarator : ID '[' INTLIT ']'
    """
    p[0] = Declaration(None, p[1], array_size=p[3])

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
                | BlockStatement
                | EmptyStatement
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
               | ArrayAccess '=' Expression ';'
    """
    p[0] = Assignment(p[1], p[3])

def p_IfStatement_if(p):
    """
    IfStatement : IF '(' Expression ')' Statement %prec IFX
    """
    p[0] = IfStatement(p[3], Statements([p[5]]), None)


def p_IfStatement_if_else(p):
    """
    IfStatement : IF '(' Expression ')' Statement ELSE Statement
    """
    p[0] = IfStatement(p[3], Statements([p[5]]), Statements([p[7]]))

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
    WhileStatement : WHILE '(' Expression ')' Statement
    """
    p[0] = WhileStatement(p[3], Statements([p[5]]))

def p_DoWhileStatement(p):
    """
    DoWhileStatement : DO BlockStatement WHILE '(' Expression ')' ';'
    """
    p[0] = DoWhileStatement(p[2], p[5])

def p_ForStatement(p):
    """
    ForStatement : FOR '(' ForInit ';' Expression ';' ForUpdate ')' BlockStatement
    """
    p[0] = ForStatement(p[3], p[5], p[7], p[9])

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

def p_BlockStatement(p):
    """
    BlockStatement : '{' Declarations Statements '}'
    """
    p[0] = BlockStatement(p[2], p[3])

def p_EmptyStatement(p):
    """
    EmptyStatement : ';'
    """
    p[0] = EmptyStatement()

def p_Return_expr(p):
    """
    Return : RETURN Expression ';'
    """
    p[0] = Return(p[2])


def p_Return_void(p):
    """
    Return : RETURN ';'
    """
    p[0] = Return()

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

def p_Call(p):
    """
    Call : ID '(' OptionalArguments ')'
    """
    p[0] = Call(p[1], p[3])

def p_ArrayAccess(p):
    """
    ArrayAccess : ID '[' Expression ']'
    """
    p[0] = ArrayAccess(p[1], p[3])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                  E x p r e s s i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Expression(p):
    """
    Expression : Expression OR Conjunction
               | Conjunction
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalOp("||", p[1], p[3])

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
                  C o n d i t i o n s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""

def p_Conjunction(p):
    """
    Conjunction : Conjunction AND Equality
                | Equality
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = LogicalOp("&&", p[1], p[3])


def p_Equality(p):
    """
    Equality : Relation EQ Relation
             | Relation NE Relation
             | Relation
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CompareOp(p[2], p[1], p[3])


def p_Relation(p):
    """
    Relation : Addition '<' Addition
             | Addition '>' Addition
             | Addition LE Addition
             | Addition GE Addition
             | Addition
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = CompareOp(p[2], p[1], p[3])


def p_Addition(p):
    """
    Addition : Addition '+' Term
             | Addition '-' Term
             | Term
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                    L i t e r a l s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
def p_Literal_int(p):
    """
    Literal : INTLIT
    """
    p[0] = Literal(p[1], "INT")

def p_Literal_float(p):
    """
    Literal : FLOATLIT
    """
    p[0] = Literal(p[1], "FLOAT")

def p_Literal_string(p):
    """
    Literal : STRINGLIT
    """
    p[0] = Literal(p[1], "STRING")

def p_Literal_bool(p):
    """
    Literal : TRUE
           | FALSE
    """
    p[0] = Literal(p[1], "BOOL")

def p_Literal_char(p):
    """
    Literal : CHARLIT
    """
    p[0] = Literal(p[1], "CHAR")

"""
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
                     F a c t o r s
▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌
"""
def p_Factor_primary(p):
    """
    Factor : Primary
    """
    p[0] = p[1]


def p_Factor_unary_minus(p):
    """
    Factor : '-' Primary
    """
    p[0] = UnaryOp("-", p[2])


def p_Factor_not(p):
    """
    Factor : '!' Primary
    """
    p[0] = UnaryOp("!", p[2])


def p_Primary_variable(p):
    """
    Primary : ID
    """
    p[0] = Variable(p[1], None)


def p_Primary_array_access(p):
    """
    Primary : ArrayAccess
    """
    p[0] = p[1]


def p_Primary_literal(p):
    """
    Primary : Literal
    """
    p[0] = p[1]


def p_Primary_group(p):
    """
    Primary : '(' Expression ')'
    """
    p[0] = p[2]


def p_Primary_call(p):
    """
    Primary : Call
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
int globalCounter, globalArray[3];

int inc(int x)
{
    return x + 1;
}

float mix(int a, float b)
{
    return a + b;
}

bool isValid(int value, char marker)
{
    return value >= 0 && value != 3 || marker == 'A';
}

void touch(void)
{
    ;
    return;
}

int main()
{
    int i, total, arr[5];
    float f;
    bool flag;
    char letter;

    total = 0;
    i = 0;
    letter = 'A';

    touch();

    for (i = 0; i < 5; i = i + 1) {
        arr[i] = inc(i);
        total = total + arr[i];
    }

    f = mix(total, 2.5);

    flag = isValid(total, letter);

    if (flag)
        total = total + 1;
    else
        total = total - 1;

    while (total < 20)
        total = total + 2;

    do {
        total = total - 1;
    } while (total > 18);

    switch (total) {
        case 17:
            total = total + 100;
            break;
        case 18:
            total = total + 200;
            break;
        default:
            total = total + 300;
    }

    if (!(total == 218) || -1 > 0) {
        total = total + 1;
    } else {
        total = total + 2;
    }

    return total;
}
"""

def compile_source(data: str):
    lexer = lex.lex()
    parser = yacc.yacc()
    tree = parser.parse(data, lexer=lexer)

    if tree is None:
        raise SyntaxError("El parser no pudo construir el AST.")

    # Configuración inicial LLVM IR
    intType = ir.IntType(32)
    floatType = ir.FloatType()
    stringType = ir.IntType(8).as_pointer()
    boolType = ir.IntType(1)
    charType = ir.IntType(8)

    module = ir.Module(name="prog")

    def get_llvm_type(type_name):
        if type_name == "int":
            return intType
        elif type_name == "float":
            return floatType
        elif type_name == "string":
            return stringType
        elif type_name == "bool":
            return boolType
        elif type_name == "char":
            return charType
        elif type_name == "void":
            return ir.VoidType()
        else:
            raise ValueError(f"Tipo desconocido: {type_name}")

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
            charType,
            module,
            function_node.return_type,
            function_table
        )

        function_node.accept(irgen)

        if not builder.block.is_terminated:
            if function_node.return_type == "void":
                builder.ret_void()
            else:
                raise TypeError(
                    f"La función '{function_node.name}' no tiene return en todos los caminos"
                )

    return module

module = compile_source(data)
print(module)

# %%
"""
================================================================ 
                        A N A L I Z E R
================================================================
"""

from pathlib import Path

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

EXAMPLES_DIR = BASE_DIR / "Examples"

parser = yacc.yacc()

parser = yacc.yacc()

for example_path in sorted(EXAMPLES_DIR.glob("*.c")):
    print("\n==============================")
    print(f"Parsing: {example_path.name}")
    print("==============================")

    data = example_path.read_text(encoding="utf-8")

    module = compile_source(data)

    print(module)

#%%