from lark import Tree, Token
import ast
import time
import random
import pyautogui
import json
import os
from PIL import ImageGrab
from macroni.util.mouse_utils import move_mouse_to
from macroni.util.template_match import locate_template_on_screen
from macroni.util.input_handler import send_input, left_click, press_and_release
from pynput import mouse, keyboard
from threading import Event
import threading
from macroni.util.ocr import region_capture, ocr_find_text
from macroni.interpreter.macroni_debugger import Debugger
from .types import ExecutionContext
from typing import Any


EXIT_SIGNAL = 1

DBG = Debugger()
class Interpreter:
    def __init__(self):
        """
            TEMPLATE DIR:
            Each file will be: target/ex1.png target/ex2.png etc.
        """
        self.template_dir = "./templates"
        # outer_vars may point to different ExecutionContext instances
        self.outer_vars: dict[str, ExecutionContext] = {}

    def eval(self, context: ExecutionContext) -> Any:
        node = context.node

        # Tokens
        match node:
            case Token(type="NUMBER"):
                val = float(node)
                if val.is_integer():
                    return int(val)
                return val
            case Token(type="STRING"):
                s = str(node)
                return ast.literal_eval(str(node))
            case Token(type="NAME"):
                name = str(node)
                # outer?
                if name in self.outer_vars:
                    outer_ctx = self.outer_vars[name]
                    return outer_ctx.vars.get(name, None)
                
                if name in context.vars:
                    return context.vars[name]
                raise Exception(f"Variable not found: {name}")
            case Token():
                return str(node)

        # Trees
        if isinstance(node, Tree):
            t = node.data
            c = node.children

            match t:
                case "outer_stmt":
                    name = str(c[0])
                    # search parents until found
                    ctx = context.parent
                    while ctx is not None:
                        if name in ctx.vars:
                            self.outer_vars[name] = ctx
                            return None
                        ctx = ctx.parent
                    return None
                case "stmt_block":
                    last = 0
                    for stmt in c:
                        stmt_ctx = context.create_sibling_context(node=stmt)
                        DBG.maybe_pause(ctx=stmt_ctx)
                        last = self.eval(stmt_ctx)
                    return last

                case "params":
                    return [str(x) for x in c]

                case "index":
                    container = self.eval(context.create_sibling_context(node=c[0]))
                    idx = self.eval(context.create_sibling_context(node=c[1]))

                    if not isinstance(idx, int):
                        raise Exception("Index must be an integer")

                    try:
                        return container[idx] if container and len(container) > idx else None
                    except Exception as e:
                        raise Exception(f"Index error: {e}")

                case "store_val":
                    num_names = 0
                    for i in range(len(c) - 1):
                        if isinstance(c[i], Token) and c[i].type == "NAME":
                            num_names += 1
                    # now eval all exprs
                    exprs = c[num_names:]
                    vals = [self.eval(context.create_sibling_context(node=e)) for e in exprs]

                    # Only flatten tuples/lists if we have multiple names (destructuring)
                    if num_names > 1:
                        # if tuples or lists, flatten
                        vals_flat = []
                        for v in vals:
                            if isinstance(v, (tuple, list)):
                                vals_flat.extend(v)
                            else:
                                vals_flat.append(v)
                        vals = vals_flat
                        if len(vals) != num_names:
                            raise Exception("Arity mismatch in multiple assignment")
                    else:
                        # Single name assignment - don't flatten, just assign the value directly
                        if len(vals) != 1:
                            raise Exception(f"Expected 1 value for single assignment, got {len(vals)}")
                        vals = [vals[0]]

                    for i in range(num_names):
                        name = str(c[i])
                        val = vals[i]
                        # check if outer
                        if name in self.outer_vars:
                            outer_ctx = self.outer_vars[name]
                            outer_ctx.vars[name] = val
                        else:
                            context.vars[name] = val
                    return None

                case "expr_stmt":
                    return self.eval(context.create_sibling_context(node=c[0]))

                case "print_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    # Print all arguments separated by spaces
                    print(*args)
                    return None

                case "swap_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    # make sure first arg is list
                    if len(args) != 3:
                        raise Exception(f"swap() takes exactly 3 arguments, got {len(args)}")
                    lst = args[0]
                    idx1 = int(args[1])
                    idx2 = int(args[2])
                    if not isinstance(lst, list):
                        raise Exception("First argument to swap() must be a list")
                    if idx1 < 0 or idx1 >= len(lst) or idx2 < 0 or idx2 >= len(lst):
                        raise Exception("swap() index out of range")
                    lst[idx1], lst[idx2] = lst[idx2], lst[idx1]
                    # return the modified list
                    return lst

                case "copy_func":
                    val = self.eval(context.create_sibling_context(node=c[0]))
                    if isinstance(val, list):
                        return val.copy()
                    if isinstance(val, tuple):
                        return tuple(val)
                    return val  # for other types, just return as is

                case "func_def":
                    name = str(c[0])

                    # Find the block/tree child (stmt_block)
                    body = None
                    params = []

                    for child in c[1:]:
                        if isinstance(child, Tree) and child.data == "params":
                            params = self.eval(context.create_sibling_context(node=child))
                        elif isinstance(child, Tree) and child.data == "stmt_block":
                            body = child

                    if body is None:
                        raise Exception(f"Function body missing for {name}")

                    context.funcs[name] = (params, body)
                    return f"Defined {name}({', '.join(params)})"

                case "args":
                    return [self.eval(context.create_sibling_context(node=x)) for x in c]

                case "call":
                    name = str(c[0])
                    arg_values = []
                    if len(c) == 2 and isinstance(c[1], Tree) and c[1].data == "args":
                        arg_values = self.eval(context.create_sibling_context(node=c[1]))

                    if name not in context.funcs:
                        raise Exception(f"Function not found: {name}")

                    params, body = context.funcs[name]
                    if len(arg_values) != len(params):
                        raise Exception(f"Arity mismatch: {name} expects {len(params)} args")

                    # Create child context: copy global scope and layer local scope on top
                    local_vars = dict(zip(params, arg_values))
                    child_context = context.create_child_context(local_vars, body)
                    return self.eval(child_context)

                # arithmetic
                case "add":
                    a = self.eval(context.create_sibling_context(node=c[0]))
                    b = self.eval(context.create_sibling_context(node=c[1]))
                    if isinstance(a, str) or isinstance(b, str):
                        return str(a) + str(b)
                    return a + b

                case "sub":
                    return self.eval(context.create_sibling_context(node=c[0])) - self.eval(context.create_sibling_context(node=c[1]))

                case "neg":
                    return -self.eval(context.create_sibling_context(node=c[0]))

                case "mul":
                    return self.eval(context.create_sibling_context(node=c[0])) * self.eval(context.create_sibling_context(node=c[1]))

                case "div":
                    return self.eval(context.create_sibling_context(node=c[0])) / self.eval(context.create_sibling_context(node=c[1]))

                case "mod":
                    result = self.eval(context.create_sibling_context(node=c[0])) % self.eval(context.create_sibling_context(node=c[1]))
                    # Convert to int if result is a whole number
                    if isinstance(result, float) and result.is_integer():
                        return int(result)
                    return result

                case "null":
                    return None

                case "true":
                    return 1

                case "false":
                    return 0

                case "tuple":
                    # Evaluate all children and return as tuple
                    return tuple(self.eval(context.create_sibling_context(node=child)) for child in c)

                case "list":
                    # Empty list
                    if len(c) == 0:
                        return []
                    # List with items
                    if isinstance(c[0], Tree) and c[0].data == "list_items":
                        return self.eval(context.create_sibling_context(node=c[0]))
                    return []

                case "list_items":
                    # Evaluate all items and return as list
                    return [self.eval(context.create_sibling_context(node=child)) for child in c]

                # comparisons (return 1/0 like you had)
                case "gt":
                    return 1 if self.eval(context.create_sibling_context(node=c[0])) > self.eval(context.create_sibling_context(node=c[1])) else 0

                case "lt":
                    return 1 if self.eval(context.create_sibling_context(node=c[0])) < self.eval(context.create_sibling_context(node=c[1])) else 0

                case "ge":
                    return 1 if self.eval(context.create_sibling_context(node=c[0])) >= self.eval(context.create_sibling_context(node=c[1])) else 0

                case "le":
                    return 1 if self.eval(context.create_sibling_context(node=c[0])) <= self.eval(context.create_sibling_context(node=c[1])) else 0

                case "eq":
                    # check if comparing to null
                    first_eval = self.eval(context.create_sibling_context(node=c[0]))
                    second_eval = self.eval(context.create_sibling_context(node=c[1]))
                    # check for null comparison
                    if first_eval is None:
                        return 1 if second_eval is None else 0
                    if second_eval is None:
                        return 1 if first_eval is None else 0
                    return 1 if first_eval == second_eval else 0

                case "ne":
                    first_eval = self.eval(context.create_sibling_context(node=c[0]))
                    second_eval = self.eval(context.create_sibling_context(node=c[1]))
                    # check for null comparison
                    if first_eval is None:
                        return 0 if second_eval is None else 1
                    if second_eval is None:
                        return 0 if first_eval is None else 1

                    return 1 if first_eval != second_eval else 0

                case "loop_stmt":
                    while self.eval(context.create_sibling_context(node=c[0])) != 0:
                        self.eval(context.create_sibling_context(node=c[1]))  # block
                    return 0

                case "wait_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
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

                case "rand_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) == 1:
                        low = 0
                        high = args[0]
                    elif len(args) == 2:
                        low = args[0]
                        high = args[1]
                    else:
                        raise Exception(f"rand() takes 1 or 2 arguments, got {len(args)}")
                    return random.uniform(low, high)

                case "rand_i_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) == 1:
                        low = 0
                        high = args[0]
                    elif len(args) == 2:
                        low = args[0]
                        high = args[1]
                    else:
                        raise Exception(f"rand_i() takes 1 or 2 arguments, got {len(args)}")
                    return random.randint(low, high)

                case "foreach_tick_func":
                    while True:
                        tick_provider_name = str(c[0])
                        func_name = str(c[1])

                        if tick_provider_name not in context.funcs:
                            raise Exception(f"Tick provider func not found: {tick_provider_name}")
                        _, tick_provider_body = context.funcs[tick_provider_name]


                        # controls timeout
                        results = self.eval(context.create_sibling_context(node=tick_provider_body))
                        if results == EXIT_SIGNAL:
                            break
                        # call the function
                        if func_name not in context.funcs:
                            raise Exception(f"Function not found: {func_name}")
                        _, body = context.funcs[func_name]
                        # Evaluate function body in current context
                        results = self.eval(context.create_sibling_context(node=body))
                    return results

                case "mouse_move_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
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

                case "set_template_dir_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) == 0:
                        raise Exception(f"set_template_dir() takes exactly 1 argument, got {len(args)}")
                    self.template_dir = str(args)
                    print(f"Template directory set to: {self.template_dir}")
                    return self.template_dir
                    # Here you would set the template directory in your application

                case "find_template_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) != 1 and len(args) != 5:
                        raise Exception(f"find_template() takes 1 or 5 arguments (template_name [, left, top, width, height]), got {len(args)}")
                    template_name = str(args[0])
                    region = None
                    if len(args) == 5:
                        # region format: (left, top, width, height)
                        region = (args[1], args[2], args[3], args[4])
                    pos = locate_template_on_screen(
                        template_dir=self.template_dir,
                        template_name=template_name,
                        downscale=1.0
                    )
                    if pos is not None and len(pos) != 0:
                        return pos[0][0], pos[0][1]
                    return None, None  # not found

                case "find_templates_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 6:
                        raise Exception(f"find_templates() takes 1 to 6 arguments (template_name [, left, top, width, height, top_k]), got {len(args)}")
                    template_name = str(args[0])
                    region = None
                    top_k = 10  # default to finding up to 10 matches

                    if len(args) == 2:
                        # Just template_name and top_k
                        top_k = int(args[1])
                    elif len(args) == 6:
                        # region format: (left, top, width, height) and top_k
                        region = (args[1], args[2], args[3], args[4])
                        top_k = int(args[5])
                    elif len(args) == 5:
                        # region format: (left, top, width, height), no top_k
                        region = (args[1], args[2], args[3], args[4])

                    positions = locate_template_on_screen(
                        template_dir=self.template_dir,
                        template_name=template_name,
                        downscale=1.0,
                        top_k=top_k
                    )
                    if positions is not None and len(positions) > 0:
                        # Return tuple of tuples
                        return tuple(positions)
                    return tuple()  # empty tuple if not found

                case "get_coordinates_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 2:
                        raise Exception(f"get_coordinates() takes 1 or 2 arguments (message [, use_cache]), got {len(args)}")
                    message = str(args[0])
                    use_cache = bool(args[1]) if len(args) == 2 else False
                    x, y = get_coordinates_interactive(message, use_cache)
                    return (x, y)

                case "check_pixel_color_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 6 or len(args) > 7:
                        raise Exception(f"check_pixel_color() takes 6 or 7 arguments (x, y, radius, r, g, b [, tolerance]), got {len(args)}")
                    x = int(args[0])
                    y = int(args[1])
                    radius = int(args[2])
                    target_r = int(args[3])
                    target_g = int(args[4])
                    target_b = int(args[5])
                    tolerance = int(args[6]) if len(args) == 7 else 0
                    found = check_pixel_color_in_radius(x, y, radius, target_r, target_g, target_b, tolerance)
                    return 1 if found else 0

                case "get_pixel_color_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 2:
                        raise Exception(f"get_pixel_color() takes 1 or 2 arguments (alias [, use_cache]), got {len(args)}")
                    alias = str(args[0])
                    use_cache = bool(args[1]) if len(args) == 2 else False
                    r, g, b = get_pixel_color_interactive(alias, use_cache)
                    return (r, g, b)

                case "conditional_expr":
                    condition = self.eval(context.create_sibling_context(node=c[0]))
                    t_block = c[1]
                    f_block = c[2] if len(c) == 3 else None

                    if condition:
                        return self.eval(context.create_sibling_context(node=t_block))
                    elif f_block is not None:
                        return self.eval(context.create_sibling_context(node=f_block))
                    return None

                case "left_click_func":
                    left_click()
                    return 0

                case "send_input_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) != 3:
                        raise Exception(f"send_input() takes exactly 3 arguments (type, key, action), got {len(args)}")
                    t = str(args[0])
                    key = str(args[1])
                    action = str(args[2])
                    send_input(t, key, action)
                    return 0

                case "press_and_release_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 2:
                        raise Exception(f"press_and_release() takes at least 2 arguments (delay_ms, key1, [key2, ...]), got {len(args)}")
                    delay_ms = int(args[0])
                    keys = [str(k) for k in args[1:]]
                    press_and_release(delay_ms, *keys)
                    return 0

                case "record_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 3:
                        raise Exception(f"record() takes 1-3 arguments (recording_name [, start_button, stop_button]), got {len(args)}")
                    recording_name = str(args[0])
                    start_button = str(args[1]) if len(args) >= 2 else "space"
                    stop_button = str(args[2]) if len(args) == 3 else "esc"
                    record_interactive(recording_name, start_button, stop_button)
                    return 0

                case "playback_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 2:
                        raise Exception(f"playback() takes 1-2 arguments (recording_name [, stop_button]), got {len(args)}")
                    recording_name = str(args[0])
                    stop_button = str(args[1]) if len(args) == 2 else "esc"
                    playback_interactive(recording_name, stop_button)
                    return 0

                case "recording_exists_func":
                    recording_name = str(self.eval(context.create_sibling_context(node=c[0])))
                    return 1 if recording_exists(recording_name) else 0

                case "len_func":
                    val = self.eval(context.create_sibling_context(node=c[0]))
                    if val is None:
                        return 0
                    if isinstance(val, (tuple, list, str)):
                        return len(val)
                    raise Exception(f"len() requires a tuple, list, or string, got {type(val)}")

                case "time_func":
                    return time.time()

                case "shuffle_func":
                    val = self.eval(context.create_sibling_context(node=c[0]))
                    if val is None:
                        return tuple()
                    if isinstance(val, tuple):
                        # Convert to list, shuffle, convert back to tuple
                        lst = list(val)
                        random.shuffle(lst)
                        return tuple(lst)
                    elif isinstance(val, list):
                        # Create a copy and shuffle it
                        lst = val.copy()
                        random.shuffle(lst)
                        return lst
                    raise Exception(f"shuffle() requires a tuple or list, got {type(val)}")

                case "get_pixel_at_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) != 2:
                        raise Exception(f"get_pixel_at() takes exactly 2 arguments (x, y), got {len(args)}")
                    x = int(args[0])
                    y = int(args[1])
                    # Capture pixel color at the specified coordinates
                    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
                    pixel = screenshot.getpixel((0, 0))
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    return (r, g, b)

                case "append_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) != 2:
                        raise Exception(f"append() takes exactly 2 arguments (list, item), got {len(args)}")
                    lst = args[0]
                    item = args[1]
                    if not isinstance(lst, list):
                        raise Exception(f"append() requires a list as first argument, got {type(lst)}")
                    # Append the item to the list (modifies in place)
                    lst.append(item)
                    return lst

                case "pop_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 2:
                        raise Exception(f"pop() takes 1 or 2 arguments (list [, index]), got {len(args)}")
                    lst = args[0]
                    if not isinstance(lst, list):
                        raise Exception(f"pop() requires a list as first argument, got {type(lst)}")
                    if len(lst) == 0:
                        raise Exception("pop() called on empty list")
                    # Pop from specific index or from end
                    if len(args) == 2:
                        index = int(args[1])
                        if index < 0 or index >= len(lst):
                            raise Exception(f"pop() index {index} out of range for list of length {len(lst)}")
                        return lst.pop(index)
                    else:
                        return lst.pop()

                case "capture_region_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 1 or len(args) > 2:
                        raise Exception(f"capture_region() takes 1 or 2 arguments (region_key [, overwrite_cache]), got {len(args)}")
                    region_key = str(args[0])
                    overwrite_cache = bool(args[1]) if len(args) == 2 else False
                    region = region_capture(region_key, overwrite_cache)
                    return region

                case "ocr_find_text_func":
                    args = self.eval(context.create_sibling_context(node=c[0]))
                    if len(args) < 0 or len(args) > 4:
                        raise Exception(f"ocr_find_text() takes 0 to 4 arguments (region, min_conf, filter, upscale), got {len(args)}")

                    # Parse arguments with defaults
                    region = args[0] if len(args) >= 1 and args[0] is not None else None
                    min_conf = float(args[1]) if len(args) >= 2 else 0.45
                    if len(args) >= 3 and args[2] is not None:
                        if isinstance(args[2], (list, tuple)):
                            filter_text = [str(f) for f in args[2]]
                        else:
                            filter_text = [str(args[2])]
                    else:
                        filter_text = None
                    upscale = float(args[3]) if len(args) >= 4 else 1.0

                    # Call OCR function
                    results = ocr_find_text(region=region, min_conf=min_conf, filter=filter_text, upscale=upscale)

                    # Convert OCRResult objects to tuples for macroni
                    # Format: [(text, conf, [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]), ...]
                    return [(r.text, r.conf, r.bbox) for r in results]

                # passthrough for inlined rules
                case _ if len(c) == 1:
                    return self.eval(context.create_sibling_context(node=c[0]))

                case _:
                    raise Exception(f"Unknown tree node: {t}")

        raise Exception(f"Unknown node type: {type(node)}")

def wait_func(duration, random_range: tuple = (0,0)):
    wait_time = duration
    random_delay = random.uniform(random_range[0], random_range[1])
    print(f"Waiting for {wait_time + random_delay} ms...")
    time.sleep((wait_time + random_delay) / 1000)
    return wait_time + random_delay

def load_coordinates_cache(cache_file="coordinates_cache.json"):
    """Load cached coordinates from JSON file."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache file: {e}")
            return {}
    return {}

def save_coordinates_cache(cache, cache_file="coordinates_cache.json"):
    """Save coordinates cache to JSON file."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save cache file: {e}")

def get_coordinates_interactive(message, use_cache=False):
    """
    Shows a popup/console message and waits for the user to hover over
    a position and press Enter to capture coordinates.

    Args:
        message: Label/key for the coordinates
        use_cache: If True, check cache first before prompting

    Returns:
        tuple: (x, y) coordinates

    Note: Coordinates are always saved to cache after capture, regardless of use_cache value.
    """
    cache_file = "coordinates_cache.json"

    # If using cache, try to load cached coordinates
    if use_cache:
        cache = load_coordinates_cache(cache_file)
        if message in cache:
            x, y = cache[message]
            print(f"✓ Using cached coordinates for '{message}': ({x}, {y})")
            return x, y
        else:
            print(f"! No cached coordinates found for '{message}', prompting user...")

    # Prompt user for coordinates
    print(f"\n{'='*50}")
    print(f"SET COORDINATES FOR: {message}")
    print(f"{'='*50}")
    print("1. Hover your mouse over the desired position")
    print("2. Press ENTER to capture the coordinates")
    print(f"{'='*50}\n")

    # Wait for user to press Enter
    input("Press ENTER when ready: ")

    # Capture the current mouse position
    x, y = pyautogui.position()
    print(f"✓ Captured coordinates: ({x}, {y})\n")

    # Always save to cache
    cache = load_coordinates_cache(cache_file)
    cache[message] = [x, y]
    save_coordinates_cache(cache, cache_file)
    print(f"✓ Saved coordinates to cache for '{message}'")

    return x, y

def load_pixel_colors_cache(cache_file="pixel_colors_cache.json"):
    """Load cached pixel colors from JSON file."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load pixel colors cache file: {e}")
            return {}
    return {}

def save_pixel_colors_cache(cache, cache_file="pixel_colors_cache.json"):
    """Save pixel colors cache to JSON file."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save pixel colors cache file: {e}")

def get_pixel_color_interactive(alias, use_cache=False):
    """
    Shows a prompt and waits for the user to hover over a pixel
    and press Enter to capture its RGB color.

    Args:
        alias: Name/alias for the color
        use_cache: If True, check cache first before prompting

    Returns:
        tuple: (r, g, b) color values

    Note: Colors are always saved to cache after capture, regardless of use_cache value.
    """
    cache_file = "pixel_colors_cache.json"

    # If using cache, try to load cached color
    if use_cache:
        cache = load_pixel_colors_cache(cache_file)
        if alias in cache:
            r, g, b = cache[alias]
            print(f"✓ Using cached color for '{alias}': RGB({r}, {g}, {b})")
            return r, g, b
        else:
            print(f"! No cached color found for '{alias}', prompting user...")
    

    # Prompt user for color
    print(f"\n{'='*50}")
    print(f"CAPTURE PIXEL COLOR FOR: {alias}")
    print(f"{'='*50}")
    print("1. Hover your mouse over the desired pixel")
    print("2. Press ENTER to capture the color")
    print(f"{'='*50}\n")

    # Wait for user to press Enter
    input("Press ENTER when ready: ")

    # Capture the current mouse position and pixel color
    x, y = pyautogui.position()
    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    pixel = screenshot.getpixel((0, 0))
    r, g, b = pixel[0], pixel[1], pixel[2]

    print(f"✓ Captured color at ({x}, {y}): RGB({r}, {g}, {b})\n")

    # Always save to cache
    cache = load_pixel_colors_cache(cache_file)
    cache[alias] = [r, g, b]
    save_pixel_colors_cache(cache, cache_file)
    print(f"✓ Saved color to cache for '{alias}'")

    return r, g, b

def check_pixel_color_in_radius(center_x, center_y, radius, target_r, target_g, target_b, tolerance=0):
    """
    Check if a specific pixel color exists within a radius of given coordinates.

    Args:
        center_x: X coordinate of the center point
        center_y: Y coordinate of the center point
        radius: Radius in pixels to search around the center
        target_r: Target red value (0-255)
        target_g: Target green value (0-255)
        target_b: Target blue value (0-255)
        tolerance: Color tolerance for matching (default 0 = exact match)

    Returns:
        bool: True if the color is found within radius, False otherwise
    """
    # Define the bounding box for the screenshot
    left = center_x - radius
    top = center_y - radius
    right = center_x + radius
    bottom = center_y + radius

    # Capture screenshot of the region
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    pixels = screenshot.load()

    width, height = screenshot.size

    # Check each pixel in the captured region
    for x in range(width):
        for y in range(height):
            # Calculate distance from center
            dx = x - radius
            dy = y - radius
            distance = (dx * dx + dy * dy) ** 0.5

            # Only check pixels within the radius
            if distance <= radius:
                pixel = pixels[x, y]
                r, g, b = pixel[0], pixel[1], pixel[2]

                # Check if pixel matches target color within tolerance
                if (abs(r - target_r) <= tolerance and
                    abs(g - target_g) <= tolerance and
                    abs(b - target_b) <= tolerance):
                    return True

    return False

def load_recordings_cache(cache_file="recordings_cache.json"):
    """Load cached recordings from JSON file."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load recordings cache file: {e}")
            return {}
    return {}

def save_recordings_cache(cache, cache_file="recordings_cache.json"):
    """Save recordings cache to JSON file."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save recordings cache file: {e}")

def recording_exists(recording_name, cache_file="recordings_cache.json"):
    """
    Check if a recording exists in the cache.

    Args:
        recording_name: Name/key for the recording
        cache_file: Path to the recordings cache file

    Returns:
        bool: True if recording exists, False otherwise
    """
    cache = load_recordings_cache(cache_file)
    return recording_name in cache

def record_interactive(recording_name, start_button="space", stop_button="esc"):
    """
    Records mouse movements, clicks, and keyboard inputs.

    Args:
        recording_name: Name/key for the recording
        start_button: Button to start recording (default 'space')
        stop_button: Button to stop recording (default 'esc')

    Returns:
        None
    """
    cache_file = "recordings_cache.json"

    print(f"\n{'='*60}")
    print(f"RECORD MODE: {recording_name}")
    print(f"{'='*60}")
    print(f"Start button: {start_button.upper()}")
    print(f"Stop button: {stop_button.upper()}")
    print(f"{'='*60}")
    print(f"Press {start_button.upper()} to start recording...")
    print(f"{'='*60}\n")

    events = []
    recording = False
    start_time = None
    stop_event = Event()

    # Convert button names to pynput keys
    def get_key(button_name):
        button_name = button_name.lower()
        if button_name == "esc" or button_name == "escape":
            return keyboard.Key.esc
        elif button_name == "space":
            return keyboard.Key.space
        elif button_name == "enter":
            return keyboard.Key.enter
        elif button_name == "shift":
            return keyboard.Key.shift
        elif button_name == "ctrl":
            return keyboard.Key.ctrl
        elif button_name == "alt":
            return keyboard.Key.alt
        else:
            return button_name

    start_key = get_key(start_button)
    stop_key = get_key(stop_button)

    def on_move(x, y):
        if recording:
            timestamp = time.time() - start_time
            events.append({
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'timestamp': timestamp
            })

    def on_click(x, y, button, pressed):
        if recording:
            timestamp = time.time() - start_time
            events.append({
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'timestamp': timestamp
            })

    def on_scroll(x, y, dx, dy):
        if recording:
            timestamp = time.time() - start_time
            events.append({
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'timestamp': timestamp
            })

    def on_press(key):
        nonlocal recording, start_time

        try:
            key_str = key.char if hasattr(key, 'char') else str(key)
        except:
            key_str = str(key)

        # Check for start button
        if not recording and key == start_key:
            recording = True
            start_time = time.time()
            print(f"\n✓ Recording started! Press {stop_button.upper()} to stop.\n")
            return

        # Check for stop button
        if recording and key == stop_key:
            print(f"\n✓ Recording stopped! Captured {len(events)} events.\n")
            stop_event.set()
            return False  # Stop listener

        # Record other key presses
        if recording:
            timestamp = time.time() - start_time
            events.append({
                'type': 'key_press',
                'key': key_str,
                'timestamp': timestamp
            })

    def on_release(key):
        if recording:
            try:
                key_str = key.char if hasattr(key, 'char') else str(key)
            except:
                key_str = str(key)

            timestamp = time.time() - start_time
            events.append({
                'type': 'key_release',
                'key': key_str,
                'timestamp': timestamp
            })

    # Start listeners
    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    mouse_listener.start()
    keyboard_listener.start()

    # Wait for recording to stop
    stop_event.wait()

    # Stop listeners
    mouse_listener.stop()
    keyboard_listener.stop()

    # Save to cache
    cache = load_recordings_cache(cache_file)
    cache[recording_name] = events
    save_recordings_cache(cache, cache_file)
    print(f"✓ Saved recording '{recording_name}' to cache with {len(events)} events.")

def playback_interactive(recording_name, stop_button="esc"):
    """
    Plays back a recorded session.

    Args:
        recording_name: Name/key for the recording
        stop_button: Button to stop playback (default 'esc')

    Returns:
        None
    """
    cache_file = "recordings_cache.json"

    # Load recording from cache
    cache = load_recordings_cache(cache_file)
    if recording_name not in cache:
        print(f"✗ Error: No recording found with name '{recording_name}'")
        return

    events = cache[recording_name]

    print(f"\n{'='*60}")
    print(f"PLAYBACK MODE: {recording_name}")
    print(f"{'='*60}")
    print(f"Stop button: {stop_button.upper()}")
    print(f"Total events: {len(events)}")
    print(f"{'='*60}")
    print(f"Playback will start in 3 seconds...")
    print(f"Press {stop_button.upper()} at any time to stop playback.")
    print(f"{'='*60}\n")

    time.sleep(3)

    stop_playback = Event()

    # Convert button name to pynput key
    def get_key(button_name):
        button_name = button_name.lower()
        if button_name == "esc" or button_name == "escape":
            return keyboard.Key.esc
        elif button_name == "space":
            return keyboard.Key.space
        elif button_name == "enter":
            return keyboard.Key.enter
        elif button_name == "shift":
            return keyboard.Key.shift
        elif button_name == "ctrl":
            return keyboard.Key.ctrl
        elif button_name == "alt":
            return keyboard.Key.alt
        else:
            return button_name

    stop_key = get_key(stop_button)

    def on_press(key):
        if key == stop_key:
            print(f"\n✓ Playback stopped by user.\n")
            stop_playback.set()
            return False  # Stop listener

    # Start keyboard listener for stop button
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    # Playback events
    start_time = time.time()
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    print("✓ Playback started!\n")

    for i, event in enumerate(events):
        if stop_playback.is_set():
            break

        # Wait for the correct timestamp
        target_time = event['timestamp']
        elapsed = time.time() - start_time
        wait_time = target_time - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # Execute event
        try:
            if event['type'] == 'mouse_move':
                mouse_controller.position = (event['x'], event['y'])

            elif event['type'] == 'mouse_click':
                button_str = event['button']
                pressed = event['pressed']

                # Convert button string to pynput button
                if 'left' in button_str.lower():
                    btn = mouse.Button.left
                elif 'right' in button_str.lower():
                    btn = mouse.Button.right
                elif 'middle' in button_str.lower():
                    btn = mouse.Button.middle
                else:
                    continue

                if pressed:
                    mouse_controller.press(btn)
                else:
                    mouse_controller.release(btn)

            elif event['type'] == 'mouse_scroll':
                mouse_controller.scroll(event['dx'], event['dy'])

            elif event['type'] == 'key_press':
                key_str = event['key']
                # Try to parse the key
                try:
                    if key_str.startswith('Key.'):
                        key_name = key_str.replace('Key.', '')
                        key_obj = getattr(keyboard.Key, key_name, None)
                        if key_obj:
                            keyboard_controller.press(key_obj)
                    else:
                        keyboard_controller.press(key_str)
                except Exception as e:
                    print(f"Warning: Could not press key '{key_str}': {e}")

            elif event['type'] == 'key_release':
                key_str = event['key']
                # Try to parse the key
                try:
                    if key_str.startswith('Key.'):
                        key_name = key_str.replace('Key.', '')
                        key_obj = getattr(keyboard.Key, key_name, None)
                        if key_obj:
                            keyboard_controller.release(key_obj)
                    else:
                        keyboard_controller.release(key_str)
                except Exception as e:
                    print(f"Warning: Could not release key '{key_str}': {e}")

        except Exception as e:
            print(f"Warning: Error executing event {i}: {e}")

    keyboard_listener.stop()

    if not stop_playback.is_set():
        print(f"✓ Playback completed! Executed {len(events)} events.\n")