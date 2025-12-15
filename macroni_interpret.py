from lark import Lark, Tree, Token
import ast
import time
import random
from mouse_utils import move_mouse_to
from template_match import locate_one_template_on_screen

calc_grammar = r'''
start: program

program: stmt*                              -> stmt_block

?stmt: func_def
     | while_stmt
     | assign_stmt
     | expr_stmt

# ---------- statements ----------

assign_stmt: NAME ("," NAME)* "=" expr ";"              -> store_val
expr_stmt: expr ";"                         -> expr_stmt
            | conditional_expr        -> expr_stmt

# ---------- built-ins ----------
built_in_calls: print_stmt
          | wait_stmt
          | rand_stmt
          | foreach_tick_stmt
          | mouse_move_stmt
          | set_template_dir_stmt
          | find_template_stmt

print_stmt: "@print" "(" expr ")"           -> print_func
wait_stmt: "@wait" "(" args ")"             -> wait_func
rand_stmt: "@rand" "(" args ")"             -> rand_func
foreach_tick_stmt: "@foreach_tick" "(" NAME "," NAME ")" -> foreach_tick_func
mouse_move_stmt: "@mouse_move" "(" args ")" -> mouse_move_func
set_template_dir_stmt: "@set_template_dir" "(" expr ")" -> set_template_dir_func
find_template_stmt: "@find_template" "(" args ")" -> find_template_func

# ---------- function definition ----------

func_def: "fn" NAME "(" [params] ")" block  -> func_def
params: NAME ("," NAME)*                    -> params

# ---------- blocks ----------

block: "{" stmt* "}"                        -> stmt_block

# ---------- while loop ----------

while_stmt: "while" expr block              -> loop_stmt

# ---------- expressions ----------

?expr: comparison
     | conditional_expr

?conditional_expr: "if" comparison block ["else" block]  -> conditional_expr

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


call: NAME "(" [args] ")"                    -> call
args: expr ("," expr)*                       -> args

COMMENT: /\#[^\n]*/
%ignore COMMENT
%import common.CNAME -> NAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
'''

calc_parser = Lark(calc_grammar, parser="lalr")
EXIT_SIGNAL = 1


class Interpreter:
    def __init__(self):
        self.vars = {}
        self.funcs = {}  # name -> (param_names, body_tree)
        """
            TEMPLATE DIR: 
            Each file will be: target/ex1.png target/ex2.png etc.
        """
        self.template_dir = "./templates"

    def eval(self, node, env=None):
        if env is None:
            env = self.vars

        # Tokens
        if isinstance(node, Token):
            if node.type == "NUMBER":
                if float(node).is_integer():
                    return int(node)
                return float(node)
            if node.type == "STRING":
                s = str(node)
                return ast.literal_eval(str(node))
            if node.type == "NAME":
                name = str(node)
                if name in env:
                    return env[name]
                raise Exception(f"Variable not found: {name}")
            return str(node)

        # Trees
        if isinstance(node, Tree):
            t = node.data
            c = node.children

            if t == "stmt_block":
                last = 0
                for stmt in c:
                    last = self.eval(stmt, env)
                return last

            if t == "params":
                return [str(x) for x in c]
            
            if t == "index":
                container = self.eval(c[0], env)
                idx = self.eval(c[1], env)

                if not isinstance(idx, int):
                    raise Exception("Index must be an integer")

                try:
                    return container[idx] if container and len(container) > idx else None
                except Exception as e:
                    raise Exception(f"Index error: {e}")

            if t == "store_val":
                num_names = 0
                for i in range(len(c) - 1):
                    if isinstance(c[i], Token) and c[i].type == "NAME":
                        num_names += 1
                # now eval all exprs
                exprs = c[num_names:]
                vals = [self.eval(e, env) for e in exprs]
                # if tuples, flatten
                vals_flat = []
                for v in vals:
                    if isinstance(v, tuple):
                        vals_flat.extend(v)
                    else:
                        vals_flat.append(v)
                vals = vals_flat
                if len(vals) != num_names:
                    raise Exception("Arity mismatch in multiple assignment")
                for i in range(num_names):
                    name = str(c[i])
                    val = vals[i]
                    env[name] = val
                return None
                 

            if t == "expr_stmt":
                return self.eval(c[0], env)

            if t == "print_func":
                val = self.eval(c[0], env)
                print(val, end="")
                return val

            if t == "func_def":
                name = str(c[0])

                # Find the block/tree child (stmt_block)
                body = None
                params = []

                for child in c[1:]:
                    if isinstance(child, Tree) and child.data == "params":
                        params = self.eval(child, env)
                    elif isinstance(child, Tree) and child.data == "stmt_block":
                        body = child

                if body is None:
                    raise Exception(f"Function body missing for {name}")

                self.funcs[name] = (params, body)
                return f"Defined {name}({', '.join(params)})"


            if t == "args":
                return [self.eval(x, env) for x in c]

            if t == "call":
                name = str(c[0])
                arg_values = []
                if len(c) == 2 and isinstance(c[1], Tree) and c[1].data == "args":
                    arg_values = self.eval(c[1], env)

                if name not in self.funcs:
                    raise Exception(f"Function not found: {name}")

                params, body = self.funcs[name]
                if len(arg_values) != len(params):
                    raise Exception(f"Arity mismatch: {name} expects {len(params)} args")

                local_env = dict(env)  # allow read-through to globals
                local_env.update(dict(zip(params, arg_values)))
                return self.eval(body, local_env)

            # arithmetic
            if t == "add":
                a = self.eval(c[0], env)
                b = self.eval(c[1], env)
                if isinstance(a, str) or isinstance(b, str):
                    return str(a) + str(b)
                return a + b
            if t == "sub":
                return self.eval(c[0], env) - self.eval(c[1], env)
            if t == "neg":
                return -self.eval(c[0], env)
            if t == "mul":
                return self.eval(c[0], env) * self.eval(c[1], env)
            if t == "div":
                return self.eval(c[0], env) / self.eval(c[1], env)
            if t == "mod":
                return self.eval(c[0], env) % self.eval(c[1], env)
            if t == "null":
                return None

            # comparisons (return 1/0 like you had)
            if t == "gt":
                return 1 if self.eval(c[0], env) > self.eval(c[1], env) else 0
            if t == "lt":
                return 1 if self.eval(c[0], env) < self.eval(c[1], env) else 0
            if t == "ge":
                return 1 if self.eval(c[0], env) >= self.eval(c[1], env) else 0
            if t == "le":
                return 1 if self.eval(c[0], env) <= self.eval(c[1], env) else 0
            if t == "eq":
                # check if comparing to null
                first_eval = self.eval(c[0], env)
                second_eval = self.eval(c[1], env)
                # check for null comparison
                if first_eval is None:
                    return 1 if second_eval is None else 0
                if second_eval is None:
                    return 1 if first_eval is None else 0
                return 1 if first_eval == second_eval else 0
            if t == "ne":
                return 1 if self.eval(c[0], env) != self.eval(c[1], env) else 0

            if t == "loop_stmt":
                while self.eval(c[0], env) != 0:
                    self.eval(c[1], env)  # block
                return 0
            
            if t == "wait_func":
                args = self.eval(c[0], env)
                if len(args) >= 1 and len(args) <= 3:
                    duration = args[0]
                    # if second arg is scalar, make it (0, scalar)
                    random_range = (0, 0)

                    if len(args) == 3:
                        random_range = (args[1], args[2])
                    elif len(args) == 2:
                        random_range = (0, args[1])
                else:
                    raise Exception(f"wait() takes 1 - 3 arguments, got {len(args)}")
                return wait_func(duration, random_range)
            
            if t == "rand_func":
                args = self.eval(c[0], env)
                if len(args) == 1:
                    low = 0
                    high = args[0]
                elif len(args) == 2:
                    low = args[0]
                    high = args[1]
                else:
                    raise Exception(f"rand() takes 1 or 2 arguments, got {len(args)}")
                return random.uniform(low, high)
            if t == "foreach_tick_func":
                while True:
                    tick_provider_name = str(c[0])
                    func_name = str(c[1])

                    if tick_provider_name not in self.funcs:
                        raise Exception(f"Tick provider func not found: {tick_provider_name}")
                    _, tick_provider_body = self.funcs[tick_provider_name]


                    # controls timeout
                    results = self.eval(tick_provider_body, env)
                    if results == EXIT_SIGNAL:
                        break
                    # call the function
                    if func_name not in self.funcs:
                        raise Exception(f"Function not found: {func_name}")
                    _, body = self.funcs[func_name]
                   # local_env = dict(env)  # allow read-through to globals
                    results = self.eval(body, env)
                return results
            if t == "mouse_move_func":
                args = self.eval(c[0], env)
                if len(args) < 3:
                    raise Exception(f"mouse_move() takes at least 3 arguments, got {len(args)}")
                x_offset = args[0]
                y_offset = args[1]
                if x_offset is None or y_offset is None:
                    return None
                pps = args[2]
                humanLike = bool(args[3]) if len(args) >= 4 else True
                move_mouse_to(x_offset, y_offset, pps, humanLike)
                return 0
            if t == "set_template_dir_func":
                args = self.eval(c[0], env)
                if len(args) == 0:
                    raise Exception(f"set_template_dir() takes exactly 1 argument, got {len(args)}")
                self.template_dir = str(args)
                print(f"Template directory set to: {self.template_dir}")
                return self.template_dir
                # Here you would set the template directory in your application
            if t == "find_template_func":
                args = self.eval(c[0], env)
                if len(args) != 1:
                    raise Exception(f"find_template() takes exactly 1 argument, got {len(args)}")
                template_name = str(args[0])
                pos = locate_one_template_on_screen(
                    template_dir=self.template_dir,
                    template_name=template_name,
                    downscale=0.5,
                )
                if pos is not None:
                    return pos
                return None, None  # not found
            
            if t == "conditional_expr":
                condition, t_block, f_block = c[0], c[1], c[2] if len(c) == 3 else None
                condition = self.eval(c[0], env)
                if condition:
                    return self.eval(t_block, env)
                elif len(c) == 3:
                    return self.eval(f_block, env)
                return None

            # passthrough for inlined rules
            if len(c) == 1:
                return self.eval(c[0], env)

            raise Exception(f"Unknown tree node: {t}")

        raise Exception(f"Unknown node type: {type(node)}")

def wait_func(duration, random_range: tuple = (0,0)):
    wait_time = duration
    random_delay = random.uniform(random_range[0], random_range[1])
    print(f"Waiting for {wait_time + random_delay} ms...")
    time.sleep((wait_time + random_delay) / 1000)
    return wait_time + random_delay

def macroni_script():
    return r"""
fn print_grid(cell_char, size) {
    size_copy = size;
    while size > 0 {
        inner_size = size_copy;
        while inner_size > 0 {
            @print(cell_char);
            inner_size = inner_size - 1;
            @print(cell_char);
        }
        @print("\n");
        size = size - 1;
    }
}

global_ticks = 0;
fn tick_provider(c,d) {
    @wait(500, 0, 50);
    global_ticks = global_ticks + 1;
    @print(global_ticks);
    global_ticks > 5; # exit if 1. return is currently last expr
}

fn tick_handler() {
    # @print("TICK!\n");
    # star_x, star_y = @find_template("star");
    # @mouse_move(star_x, star_y, 2000, 1);
    # pent_x, pent_y = @find_template("pentagon");
    # @mouse_move(pent_x, pent_y, 2000, 1);
    # file_menu_x, file_menu_y = @find_template("filemenu");
    # @mouse_move(file_menu_x, file_menu_y, 2000, 1);
    # @wait(1000, 0, 500);
    # save_x, save_y = @find_template("filemenusave");
    # @mouse_move(save_x, save_y, 2000, 1);
    windmill_x, windmill_y = @find_template("windmill");
    @mouse_move(windmill_x, windmill_y, 2000, 1);
}

# set template dir
template_dir = "/Users/sam.schreiber/src/macroni/templates";
@set_template_dir(template_dir);
@foreach_tick(tick_provider, tick_handler);
"""

def main():
    interp = Interpreter()
    tree = calc_parser.parse(macroni_script())
    interp.eval(tree)


if __name__ == "__main__":
    main()
