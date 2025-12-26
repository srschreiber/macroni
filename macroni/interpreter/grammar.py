from lark import Lark

calc_grammar = r"""
start: program

program: stmt*                              -> stmt_block

?stmt: func_def
     | while_stmt
     | assign_stmt
     | expr_stmt
     | outer_stmt
     | control_stmt
     | import_stmt

# ---------- importing modules ----------
import_stmt: "import" STRING ";"            -> import_stmt


# ---------- statements ----------
outer_stmt: "outer" NAME ";"                    -> outer_stmt
assign_stmt: NAME ("," NAME)* "=" expr ";"              -> store_val
expr_stmt: expr (";")+                         -> expr_stmt
            | conditional_expr        -> expr_stmt
control_stmt: "break" (";")+      -> break_stmt
            | "return" [expr] (";")+  -> return_stmt
              | "continue" (";")+   -> continue_stmt

# ---------- built-ins ----------
built_in_calls: print_stmt
          | wait_stmt
          | rand_stmt
          | foreach_tick_stmt
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

print_stmt: "@print" "(" args ")"           -> print_func
wait_stmt: "@wait" "(" args ")"             -> wait_func
rand_stmt: "@rand" "(" args ")"             -> rand_func
foreach_tick_stmt: "@foreach_tick" "(" NAME "," NAME ")" -> foreach_tick_func
mouse_move_stmt: "@mouse_move" "(" args ")" -> mouse_move_func
set_template_dir_stmt: "@set_template_dir" "(" expr ")" -> set_template_dir_func
find_template_stmt: "@find_template" "(" args ")" -> find_template_func
find_templates_stmt: "@find_templates" "(" args ")" -> find_templates_func
get_coordinates_stmt: "@get_coordinates" "(" args ")" -> get_coordinates_func
# params: x, y, radius, r, g, b, [tolerance]
check_pixel_color_stmt: "@check_pixel_color" "(" args ")" -> check_pixel_color_func
get_pixel_color_stmt: "@get_pixel_color" "(" args ")" -> get_pixel_color_func
left_click_stmt: "@left_click" "(" ")"               -> left_click_func
# type, key, action
send_input_stmt: "@send_input" "(" args ")"         -> send_input_func
# delay_ms, *keys
press_and_release_stmt: "@press_and_release" "(" args ")" -> press_and_release_func
# recording_name, start_button, stop_button
record_stmt: "@record" "(" args ")"                 -> record_func
# recording_name, stop_button
playback_stmt: "@playback" "(" args ")"             -> playback_func
# recording_name
recording_exists_stmt: "@recording_exists" "(" expr ")" -> recording_exists_func
len_stmt: "@len" "(" expr ")"                   -> len_func
rand_i_stmt: "@rand_i" "(" args ")"             -> rand_i_func
time_stmt: "@time" "(" ")"                      -> time_func
shuffle_stmt: "@shuffle" "(" expr ")"           -> shuffle_func
get_pixel_at_stmt: "@get_pixel_at" "(" args ")" -> get_pixel_at_func
append_stmt: "@append" "(" args ")"             -> append_func
pop_stmt: "@pop" "(" args ")"                   -> pop_func
# region_key, overwrite_cache
capture_region_stmt: "@capture_region" "(" args ")" -> capture_region_func
# region, min_conf, filter, upscale
ocr_find_text_stmt: "@ocr_find_text" "(" args ")" -> ocr_find_text_func
swap_stmt: "@swap" "(" args ")"                 -> swap_func
copy_stmt: "@copy" "(" expr ")"                 -> copy_func
mouse_position_stmt: "@mouse_position" "(" ")"   -> mouse_position_func


# ---------- function definition ----------

func_def: "fn" NAME "(" [params] ")" block  -> func_def
params: NAME ("," NAME)*                    -> params

# ---------- blocks ----------

block: "{" stmt* "}" (";")*                        -> stmt_block

# ---------- while loop ----------

while_stmt: "while" expr block              -> loop_stmt

# ---------- expressions ----------

?expr: logical_or
     | conditional_expr

?conditional_expr: "if" logical_or block ["else" block]  -> conditional_expr

?logical_or: logical_and
           | logical_or "||" logical_and -> or_op

?logical_and: comparison
            | logical_and "&&" comparison -> and_op

?comparison: sum
           | sum ">" sum   -> gt
           | sum "<" sum   -> lt
           | sum ">=" sum  -> ge
           | sum "<=" sum  -> le
           | sum "==" sum  -> eq
           | sum "!=" sum  -> ne

?sum: sum "+" product                        -> add
    | sum "-" product                        -> sub
    | "-" sum                                -> neg
    | product

?product: product "*" atom                   -> mul
        | product "/" atom                   -> div
        | product "%" atom                   -> mod
        | atom

# ---------- ATOMS (IMPORTANT PART) ----------

?atom: atom "[" expr "]"                    -> index
     | NUMBER                                -> number
     | STRING                                -> string
     | call
     | built_in_calls
     | NAME                                  -> var
     | "(" expr ")"
     | "null"                                -> null
     | "true"                                -> true
     | "false"                               -> false
     | "(" atom ("," atom)+ ")"              -> tuple
     | "[" [list_items] "]"                  -> list

list_items: expr ("," expr)*                 -> list_items


call: NAME "(" [args] ")"                    -> call
args: expr ("," expr)*                       -> args

COMMENT: /\#[^\n]*/
%ignore COMMENT
%import common.CNAME -> NAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
"""

calc_parser = Lark(
    calc_grammar, parser="lalr", propagate_positions=True, maybe_placeholders=False
)
