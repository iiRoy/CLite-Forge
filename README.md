<p align="center">
  <img 
    src="https://github.com/user-attachments/assets/4fe13f30-011f-41cd-a207-a7ad5d281810"
    alt="CLite Forge Logo" 
    width="600"
  />
</p>

**CLiteForge** is a Python-based compiler project that parses a simplified C-like language and generates **LLVM Intermediate Representation (LLVM IR)**.

The project includes a full compiler pipeline using **PLY** for lexical and syntax analysis, an **Abstract Syntax Tree (AST)** representation, the **Visitor design pattern**, and **llvmlite** for LLVM IR generation. It also includes a smaller calculator module that demonstrates expression parsing and LLVM IR generation with arithmetic operations.

> [!NOTE]
> This project was originally structured as `Mini-Compiler`, but **CLiteForge** is a more professional and descriptive name for the repository.

---

## Overview

**CLiteForge** is an academic compiler construction project focused on translating a simplified C-like language into LLVM IR.

The compiler supports:

- Lexical analysis.
- Syntax analysis.
- AST construction.
- Visitor-based AST traversal.
- LLVM IR generation.
- Global declarations.
- Function definitions.
- Primitive data types.
- Expressions.
- Assignments.
- Function calls.
- Control flow structures.
- Arrays.
- Example C-like programs.

The repository also contains a calculator prototype used to demonstrate how arithmetic expressions can be parsed, represented as an AST, evaluated, and translated into LLVM IR.

> [!IMPORTANT]
> This project generates LLVM IR. It does not currently include a full command-line interface for compiling arbitrary files directly from terminal arguments.

---

## Project Structure

```text
CLiteForge/
│
├── Calculator/
│   ├── analisisCalc.py
│   ├── arbolCalc.py
│   ├── parser.out
│   ├── parsetab.py
│   └── README.md
│
├── Compiler/
│   ├── Examples/
│   │   ├── countdown.c
│   │   ├── factorial.c
│   │   ├── fibonacci.c
│   │   ├── hanoiTower.c
│   │   ├── juegoDePalabras.c
│   │   └── taylorSerie.c
│   │
│   ├── analysis.py
│   ├── arbol.py
│   ├── parser.out
│   ├── parsetab.py
│   └── README.md
│
├── Documentation/
│   ├── Actividad 3.2-1.pdf
│   ├── CLite-Syntax.pdf
│   ├── LLVM IR_ Estructuras de control_ Desarrollo de aplicaciones avanzadas de ciencias computacionales (Gpo 501)-1.pdf
│   └── Reporte_Compilador_CLite_LLVM_IR_RodrigoLópezGuerra.pdf
│
├── .gitignore
└── README.md
```

---

## Main Folders

| Folder | Description |
|---|---|
| `Compiler/` | Main CLite compiler implementation. |
| `Compiler/Examples/` | Example C-like programs used to test parsing and LLVM IR generation. |
| `Calculator/` | Smaller arithmetic expression parser, evaluator, and LLVM IR generator. |
| `Documentation/` | Academic documents and reference material related to CLite and LLVM IR. |

---

## Main Files

| File | Description |
|---|---|
| `Compiler/analysis.py` | Main compiler file. Defines lexer, parser, grammar rules, test program, file analyzer, and LLVM IR generation flow. |
| `Compiler/arbol.py` | AST node definitions and visitor implementations, including the LLVM IR generator. |
| `Calculator/analisisCalc.py` | Arithmetic expression lexer, parser, calculator evaluator, and LLVM IR demo. |
| `Calculator/arbolCalc.py` | AST and visitor implementation for the calculator module. |
| `Compiler/Examples/*.c` | Sample CLite-style programs used for compiler testing. |
| `.gitignore` | Ignores Python cache files and generated PLY parser files. |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| `Python` | Main implementation language. |
| `PLY` | Lexer and parser generation. |
| `llvmlite` | LLVM IR generation. |
| `LLVM IR` | Target intermediate representation. |
| `AST` | Internal representation of parsed source code. |
| `Visitor Pattern` | Traverses AST nodes for interpretation or IR generation. |

---

## Requirements

To run this project, you need:

- Python 3.10 or newer
- `ply`
- `llvmlite`

Recommended:

```text
Python 3.11+
```

> [!TIP]
> Use a virtual environment so the compiler dependencies stay isolated from your system Python installation.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/CLiteForge.git
cd CLiteForge
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

If you use fish shell:

```fish
source .venv/bin/activate.fish
```

Install dependencies:

```bash
pip install ply llvmlite
```

---

## How to Run the Compiler

Go to the compiler folder:

```bash
cd Compiler
```

Run the main compiler script:

```bash
python analysis.py
```

The script will:

1. Build the lexer and parser.
2. Parse the built-in CLite sample program inside `analysis.py`.
3. Generate LLVM IR.
4. Print the LLVM IR output in the terminal.
5. Parse and compile the files inside `Compiler/Examples/`.

> [!NOTE]
> The current script uses an internal `data` string and then loops through files in the `Examples/` folder. It is not yet structured as a CLI tool that receives a file path as an argument.

---

## How to Run the Calculator Module

Go to the calculator folder:

```bash
cd Calculator
```

Run:

```bash
python analisisCalc.py
```

The calculator module parses the expression:

```text
10 + 5 * 3
```

It then:

1. Builds an AST.
2. Generates LLVM IR.
3. Evaluates the expression using a visitor-based calculator.
4. Prints the LLVM module and result stack.

Expected arithmetic result:

```text
25
```

---

## Compiler Pipeline

CLiteForge follows a classic compiler structure:

```text
Source Code
    ↓
Lexer
    ↓
Parser
    ↓
Abstract Syntax Tree
    ↓
Visitor Traversal
    ↓
LLVM IR Generation
```

---

## Lexer

The lexer is implemented with **PLY Lex**.

It recognizes:

- Identifiers.
- Integer literals.
- Float literals.
- String literals.
- Character literals.
- Boolean literals.
- Reserved keywords.
- Operators.
- Delimiters.
- Single-line comments.
- Multi-line comments.
- Preprocessor-style lines.

Supported reserved words include:

```text
int
float
string
bool
char
void
true
false
return
printf
if
else
switch
case
default
break
while
do
for
```

---

## Parser

The parser is implemented with **PLY Yacc**.

It defines grammar rules for a simplified C-like language.

The parser builds an AST instead of immediately executing the program.

Supported structures include:

- Program items.
- Global declarations.
- Function definitions.
- Function parameters.
- Local declarations.
- Statements.
- Assignments.
- Function calls.
- Return statements.
- Print statements.
- Conditional statements.
- Switch statements.
- While loops.
- Do-while loops.
- For loops.
- Blocks.
- Empty statements.
- Array access.
- Expressions.

---

## Supported Data Types

| Type | Description |
|---|---|
| `int` | 32-bit integer type in the compiler module. |
| `float` | Floating-point value. |
| `string` | Pointer to 8-bit characters in LLVM IR. |
| `bool` | Boolean value. |
| `char` | 8-bit character value. |
| `void` | Used for functions that do not return a value. |

---

## Supported Operators

### Arithmetic Operators

```text
+
-
*
/
%
```

### Comparison Operators

```text
==
!=
<
>
<=
>=
```

### Logical Operators

```text
&&
||
!
```

### Assignment Operator

```text
=
```

---

## Supported Control Flow

CLiteForge supports several C-like control flow structures:

```c
if (condition)
    statement;
else
    statement;
```

```c
while (condition)
    statement;
```

```c
do {
    statement;
} while (condition);
```

```c
for (i = 0; i < 10; i = i + 1) {
    statement;
}
```

```c
switch (value) {
    case 1:
        statement;
        break;
    default:
        statement;
}
```

> [!IMPORTANT]
> This compiler is educational and does not aim to implement the complete C language.

---

## Example CLite Program

```c
int inc(int x)
{
    return x + 1;
}

int main()
{
    int i, total, arr[5];

    total = 0;
    i = 0;

    for (i = 0; i < 5; i = i + 1) {
        arr[i] = inc(i);
        total = total + arr[i];
    }

    if (total > 10)
        total = total + 1;
    else
        total = total - 1;

    return total;
}
```

The compiler parses this type of input and generates LLVM IR.

---

## Example Output

Running:

```bash
python analysis.py
```

prints LLVM IR similar in structure to:

```llvm
; ModuleID = "prog"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  ...
}
```

The exact output depends on the source program being compiled.

---

## Calculator Module

The `Calculator/` folder contains a smaller version of the compiler pipeline.

It supports integer arithmetic expressions such as:

```text
10 + 5 * 3
```

The calculator module demonstrates:

- Tokenizing arithmetic expressions.
- Parsing precedence.
- Building an AST.
- Evaluating the AST.
- Generating LLVM IR for arithmetic operations.

Supported calculator operators:

```text
+
-
*
/
%
```

> [!NOTE]
> The calculator module is useful for understanding the compiler architecture before studying the full CLite compiler.

---

## Documentation

The `Documentation/` folder includes academic and reference documents related to:

- CLite syntax.
- Compiler implementation.
- LLVM IR.
- Control flow structures.
- Project report material.

These documents are useful for understanding the theoretical background of the compiler.

---

## Generated Files

PLY generates files such as:

```text
parser.out
parsetab.py
```

These files are used to speed up parser construction and debug grammar behavior.

The `.gitignore` file excludes:

```text
__pycache__/
*.pyc
parser.out
parsetab.py
```

> [!TIP]
> If the parser behaves strangely after grammar changes, delete `parser.out`, `parsetab.py`, and `__pycache__/`, then run the script again.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'ply'`

Install PLY:

```bash
pip install ply
```

---

### `ModuleNotFoundError: No module named 'llvmlite'`

Install llvmlite:

```bash
pip install llvmlite
```

---

### Parser tables are outdated

Delete generated parser files:

```bash
rm -f parser.out parsetab.py
rm -rf __pycache__
```

Then run the compiler again:

```bash
python analysis.py
```

---

### The compiler cannot find the `Examples` folder

Make sure you run the compiler from inside the `Compiler/` folder:

```bash
cd Compiler
python analysis.py
```

The script expects:

```text
Compiler/Examples/
```

relative to the compiler file location.

---

### Syntax errors when compiling an example

The compiler supports a simplified C-like grammar, not full C.

Check that the source file only uses supported features such as:

- CLite-compatible types.
- Basic declarations.
- Supported loops.
- Supported expressions.
- Supported function definitions.
- Supported array access.

---

### `main` function not found

The compiler requires a `main` function.

Make sure the source program includes:

```c
int main()
{
    return 0;
}
```

---

## Possible Improvements

Future versions could include:

- Command-line interface for compiling custom files.
- Output `.ll` files instead of only printing LLVM IR.
- Better semantic analysis.
- Type checking improvements.
- Scope validation improvements.
- More detailed error messages.
- Line and column information in syntax errors.
- Function declaration prototypes.
- String handling improvements.
- Array bounds checking.
- Support for more C-like syntax.
- Unit tests for grammar rules.
- Automated test suite for example programs.
- Cleaner separation between lexer, parser, AST, and IR generation.
- Better documentation for supported CLite grammar.
- Add `requirements.txt`.
- Add generated LLVM IR examples.

> [!TIP]
> A strong next step would be adding a CLI such as:
>
> ```bash
> python analysis.py Examples/factorial.c -o factorial.ll
> ```

---

## Educational Purpose

This project is useful for learning:

- Compiler construction.
- Lexical analysis.
- Syntax analysis.
- Grammar design.
- AST construction.
- Visitor pattern.
- LLVM IR generation.
- Function compilation.
- Expression handling.
- Control flow generation.
- Array access.
- Type representation.
- Python compiler tooling.
- PLY.
- llvmlite.

---

## License

This project is publicly available for educational and portfolio review purposes only.

The source code, visual assets, audio, videos, logos, screenshots, documentation, and other project materials may not be used, copied, modified, redistributed, sublicensed, or used commercially without explicit permission from the project authors.

All rights reserved unless otherwise stated.

> [!IMPORTANT]
> Some third-party assets, music, libraries, or references may be subject to their own licenses. Those materials remain owned by their original creators and are not covered by this project license.

---

## Disclaimer

**CLiteForge** is an academic compiler project.

It is intended for learning and experimentation with compiler design, parsing, ASTs, and LLVM IR generation.

> [!CAUTION]
> This project does not implement the complete C language and should not be used as a production compiler.
