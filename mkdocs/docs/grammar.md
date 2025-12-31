# Grammar Specification

Formal EBNF grammar for the Macroni language.

!!! info "Parser"
    Macroni uses [Lark](https://lark-parser.readthedocs.io/) with LALR(1) parsing.

---

## Program Structure

```ebnf
start: program

program: stmt*

stmt: func_def
    | while_stmt
    | assign_stmt
    | expr_stmt
    | outer_stmt
    | control_stmt
    | import_stmt
```

---

## Imports

```ebnf
import_stmt: "import" STRING ";"
```

**Example:**
```macroni
import "utils.macroni";
import "helpers/mouse.macroni";
```

---

## Statements

### Variable Assignment

```ebnf
assign_stmt: NAME ("," NAME)* "=" expr ";"
```

**Examples:**
```macroni
x = 10;
name = "Alice";
x, y = (100, 200);
a, b, c = [1, 2, 3];
```

### Outer Scope Declaration

```ebnf
outer_stmt: "outer" NAME ";"
```

**Example:**
```macroni
x = 10;
fn modify() {
    outer x;
    x = 20;  # Modifies outer x
}
```

### Expression Statement

```ebnf
expr_stmt: expr ";"+
         | conditional_expr
```

### Control Flow

```ebnf
control_stmt: "break" ";"+
            | "return" [expr] ";"+
            | "continue" ";"+
```

**Examples:**
```macroni
break;
return 42;
continue;
```

---

## Blocks

```ebnf
block: "{" stmt* "}" ";"*
```

**Example:**
```macroni
{
    x = 10;
    @print(x);
}
```

---

## Function Definitions

```ebnf
func_def: "fn" NAME "(" [params] ")" block

params: NAME ("," NAME)*
```

**Examples:**
```macroni
fn greet() {
    @print("Hello!");
}

fn add(a, b) {
    return a + b;
}

fn process(x, y, z) {
    return x * y + z;
}
```

---

## While Loops

```ebnf
while_stmt: "while" expr block
```

**Example:**
```macroni
while x < 10 {
    @print(x);
    x = x + 1;
}
```

---

## Expressions

### Expression Hierarchy

```ebnf
expr: logical_or
    | conditional_expr

conditional_expr: "if" logical_or block ["else" block]
```

### Logical Operators

```ebnf
logical_or: logical_and
          | logical_or "||" logical_and

logical_and: comparison
           | logical_and "&&" comparison
```

**Examples:**
```macroni
x > 5 && y < 10
enabled || debug_mode
```

### Comparison Operators

```ebnf
comparison: sum
          | sum ">" sum
          | sum "<" sum
          | sum ">=" sum
          | sum "<=" sum
          | sum "==" sum
          | sum "!=" sum
```

**Examples:**
```macroni
x > 10
count == 0
temp >= 100
```

### Arithmetic Operators

```ebnf
sum: sum "+" product
   | sum "-" product
   | "-" sum              # Negation
   | product

product: product "*" atom
       | product "/" atom
       | product "%" atom
       | atom
```

**Examples:**
```macroni
10 + 5 * 2    # 20 (multiplication first)
(10 + 5) * 2  # 30 (parentheses override)
-x            # Negation
15 % 4        # 3 (modulo)
```

---

## Atoms (Primary Expressions)

```ebnf
atom: atom "[" expr "]"          # Indexing
    | NUMBER
    | STRING
    | call
    | built_in_calls
    | NAME                       # Variable
    | "(" expr ")"               # Grouping
    | "null"
    | "true"
    | "false"
    | "(" atom ("," atom)+ ")"   # Tuple
    | "()"                       # Empty tuple
    | "[" [list_items] "]"       # List
    | "[]"                       # Empty list

list_items: expr ("," expr)*
```

**Examples:**
```macroni
# Literals
42
3.14
"hello"
true
false
null

# Collections
(1, 2, 3)
[1, 2, 3]
()
[]

# Indexing
items[0]
matrix[i][j]

# Variables
x
name
coords

# Grouping
(x + y) * 2
```

---

## Function Calls

```ebnf
call: NAME "(" [args] ")"

args: expr ("," expr)*
```

**Examples:**
```macroni
greet()
add(10, 20)
process(x, y, z * 2)
nested(outer(inner()))
```

---

## Built-in Functions

```ebnf
built_in_calls: print_stmt
              | wait_stmt
              | rand_stmt
              | mouse_move_stmt
              | set_template_dir_stmt
              | find_template_stmt
              | find_templates_stmt
              | get_coordinates_stmt
              | check_pixel_color_stmt
              | get_pixel_color_stmt
              | left_click_stmt
              | send_input_stmt
              | press_and_release_stmt
              | record_stmt
              | playback_stmt
              | recording_exists_stmt
              | len_stmt
              | rand_i_stmt
              | time_stmt
              | shuffle_stmt
              | get_pixel_at_stmt
              | append_stmt
              | pop_stmt
              | capture_region_stmt
              | ocr_find_text_stmt
              | swap_stmt
              | copy_stmt
              | mouse_position_stmt
              | int_stmt
              | float_stmt
              | str_stmt
              | is_int_stmt
              | is_float_stmt
              | is_str_stmt
              | is_tuple_stmt
              | is_list_stmt
              | bang_statement
```

### Built-in Function Definitions

```ebnf
# Type Conversion
int_stmt:   "@int" "(" expr ")"
float_stmt: "@float" "(" expr ")"
str_stmt:   "@str" "(" expr ")"

# Type Checking
is_int_stmt:   "@is_int" "(" expr ")"
is_float_stmt: "@is_float" "(" expr ")"
is_str_stmt:   "@is_str" "(" expr ")"
is_tuple_stmt: "@is_tuple" "(" expr ")"
is_list_stmt:  "@is_list" "(" expr ")"

# Utility
print_stmt: "@print" "(" args ")"
bang_statement: "!" expr                # Logical NOT

# Timing
wait_stmt: "@wait" "(" args ")"
time_stmt: "@time" "(" ")"

# Random
rand_stmt:   "@rand" "(" args ")"
rand_i_stmt: "@rand_i" "(" args ")"

# Mouse
mouse_move_stmt: "@mouse_move" "(" args ")"
left_click_stmt: "@left_click" "(" ")"
mouse_position_stmt: "@mouse_position" "(" ")"

# Keyboard
press_and_release_stmt: "@press_and_release" "(" args ")"
send_input_stmt: "@send_input" "(" args ")"

# Template Matching
set_template_dir_stmt: "@set_template_dir" "(" expr ")"
find_template_stmt:    "@find_template" "(" args ")"
find_templates_stmt:   "@find_templates" "(" args ")"

# Screen
get_coordinates_stmt:  "@get_coordinates" "(" args ")"
get_pixel_at_stmt:     "@get_pixel_at" "(" args ")"
get_pixel_color_stmt:  "@get_pixel_color" "(" args ")"
check_pixel_color_stmt: "@check_pixel_color" "(" args ")"

# OCR
capture_region_stmt: "@capture_region" "(" args ")"
ocr_find_text_stmt:  "@ocr_find_text" "(" args ")"

# Recording
record_stmt:           "@record" "(" args ")"
playback_stmt:         "@playback" "(" args ")"
recording_exists_stmt: "@recording_exists" "(" expr ")"

# List Operations
len_stmt:     "@len" "(" expr ")"
append_stmt:  "@append" "(" args ")"
pop_stmt:     "@pop" "(" args ")"
shuffle_stmt: "@shuffle" "(" expr ")"
swap_stmt:    "@swap" "(" args ")"
copy_stmt:    "@copy" "(" expr ")"
```

---

## Lexical Elements

### Tokens

```ebnf
COMMENT: /#[^\n]*/
NAME:    /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER:  /[0-9]+\.?[0-9]*/
STRING:  /"[^"]*"/
```

### Keywords

Reserved words that cannot be used as identifiers:

```
fn        # Function definition
if        # Conditional
else      # Alternative branch
while     # Loop
break     # Exit loop
continue  # Skip iteration
return    # Return from function
outer     # Outer scope
import    # Import module
true      # Boolean true
false     # Boolean false
null      # Null value
```

### Operators

```
# Arithmetic
+  -  *  /  %  (unary -)

# Comparison
>  <  >=  <=  ==  !=

# Logical
&&  ||  !

# Other
=     # Assignment
[]    # Indexing
()    # Grouping/Tuples/Calls
{}    # Blocks
,     # Separator
;     # Statement terminator
```

---

## Operator Precedence

From highest to lowest precedence:

| Level | Operators | Associativity | Example |
|-------|-----------|---------------|---------|
| 1 | `[]` (indexing) | Left | `items[0]` |
| 2 | Function calls | Left | `add(1, 2)` |
| 3 | `-` (unary) | Right | `-x` |
| 4 | `*` `/` `%` | Left | `a * b / c` |
| 5 | `+` `-` | Left | `a + b - c` |
| 6 | `>` `<` `>=` `<=` `==` `!=` | Left | `x > 5` |
| 7 | `&&` | Left | `a && b` |
| 8 | `||` | Left | `a || b` |
| 9 | `if` (conditional expression) | Right | `if x { a } else { b }` |

**Grouping with parentheses overrides precedence:**
```macroni
(a + b) * c    # Addition first
a + (b * c)    # Multiplication first (same as a + b * c)
```

---

## Complete Grammar

```ebnf
start: program

program: stmt*

?stmt: func_def
     | while_stmt
     | assign_stmt
     | expr_stmt
     | outer_stmt
     | control_stmt
     | import_stmt

import_stmt: "import" STRING ";"

outer_stmt: "outer" NAME ";"
assign_stmt: NAME ("," NAME)* "=" expr ";"
expr_stmt: expr ";"+
         | conditional_expr
control_stmt: "break" ";"+
            | "return" [expr] ";"+
            | "continue" ";"+

func_def: "fn" NAME "(" [params] ")" block
params: NAME ("," NAME)*

block: "{" stmt* "}" ";"*

while_stmt: "while" expr block

?expr: logical_or
     | conditional_expr

?conditional_expr: "if" logical_or block ["else" block]

?logical_or: logical_and
           | logical_or "||" logical_and

?logical_and: comparison
            | logical_and "&&" comparison

?comparison: sum
           | sum ">" sum
           | sum "<" sum
           | sum ">=" sum
           | sum "<=" sum
           | sum "==" sum
           | sum "!=" sum

?sum: sum "+" product
    | sum "-" product
    | "-" sum
    | product

?product: product "*" atom
        | product "/" atom
        | product "%" atom
        | atom

?atom: atom "[" expr "]"
     | NUMBER
     | STRING
     | call
     | built_in_calls
     | NAME
     | "(" expr ")"
     | "null"
     | "true"
     | "false"
     | "(" atom ("," atom)+ ")"
     | "()"
     | "[" [list_items] "]"
     | "[]"

list_items: expr ("," expr)*

call: NAME "(" [args] ")"
args: expr ("," expr)*

COMMENT: /#[^\n]*/
%ignore COMMENT
%import common.CNAME -> NAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
```

---

## Grammar Notes

!!! note "Statement Terminators"
    - All statements must end with `;`
    - Multiple semicolons are allowed (e.g., `;;`)
    - Blocks can optionally have trailing semicolons

!!! note "Expressions vs Statements"
    - Conditional `if` can be used as both expression and statement
    - Expression form: `result = if x > 0 { 1 } else { -1 };`
    - Statement form: `if x > 0 { @print("positive"); }`

!!! note "Comments"
    - Only single-line comments (`#`) are supported
    - No multi-line comment syntax
    - Comments are ignored by the parser

!!! note "Whitespace"
    - Whitespace (spaces, tabs, newlines) is ignored except within strings
    - Indentation is not significant (unlike Python)
    - Code style is flexible

!!! tip "Parser Implementation"
    The grammar is implemented using Lark with LALR(1) parsing:
    ```python
    from lark import Lark
    parser = Lark(calc_grammar, parser="lalr",
                  propagate_positions=True,
                  maybe_placeholders=False)
    ```
    Source: `macroni/interpreter/grammar.py`
