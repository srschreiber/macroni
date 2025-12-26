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
from macroni.util import output_handler
from threading import Event
import threading
from macroni.util.ocr import region_capture, ocr_find_text
from macroni.interpreter.macroni_debugger import Debugger
from .types import ExecutionContext
from typing import Any, Iterable

try:
    import readline
except ImportError:
    try:
        import pyreadline3
    except ImportError:
        pass


class Sigl: ...


# used to track return signal
RET_SIG: Sigl = Sigl()
BRK_SIG: Sigl = Sigl()
EXIT_SIG: Sigl = Sigl()
CNT_SIG: Sigl = Sigl()
DBG = Debugger()


class ControlSignal:
    def __init__(self, values: list[Any], signal: Sigl = None):
        self.values = []
        if isinstance(values, list) or isinstance(values, tuple):
            self.values = values
        else:
            self.values = [values]
        self.signal = signal

    def is_single(self) -> bool:
        return len(self.values) == 1

    def get_single(self) -> Any:
        if self.is_single():
            return self.values[0]
        raise Exception("Multiple return values present")

    def get_multiple(self) -> list[Any]:
        return self.values

    def is_signal(self, signal: Sigl) -> bool:
        return self.signal is signal


class Interpreter:
    def __init__(self):
        """
        TEMPLATE DIR:
        Each file will be: target/ex1.png target/ex2.png etc.
        """
        self.template_dir = "./templates"

    def eval_child(self, parent_context: ExecutionContext, node: any) -> Any:
        child_context = parent_context.create_child_context(node=node)
        return self.eval(child_context)

    def eval_sibling(self, sibling_context: ExecutionContext, node: any) -> Any:
        sibling_ctx = sibling_context.create_sibling_context(node=node)
        return self.eval(sibling_ctx)

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
                if name in context.outer_vars:
                    outer_ctx = context.outer_vars[name]
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
                case "import_stmt":
                    # imports should be pre-loaded by now
                    return None
                case "outer_stmt":
                    # match list single arg
                    match c:
                        case [name]:
                            # First check if parent already has this variable marked as outer
                            if (
                                context.parent
                                and str(name) in context.parent.outer_vars
                            ):
                                # Inherit the parent's outer reference
                                context.outer_vars[str(name)] = (
                                    context.parent.outer_vars[str(name)]
                                )
                                return None

                            # Otherwise search parents until found
                            ctx = context.parent
                            while ctx is not None:
                                if str(name) in ctx.vars:
                                    context.outer_vars[str(name)] = ctx
                                    return None
                                ctx = ctx.parent
                            return None
                case "stmt_block":
                    last = 0
                    for stmt in c:
                        stmt_ctx = context.create_sibling_context(node=stmt)
                        DBG.maybe_pause(ctx=stmt_ctx)
                        last = self.eval_sibling(context, stmt)
                        match last:
                            case ControlSignal(signal=signal) if signal in (
                                RET_SIG,
                                BRK_SIG,
                                CNT_SIG,
                            ):
                                return last

                    return last

                case "params":
                    return [str(x) for x in c]

                case "index":
                    match c:
                        case [arg1, arg2]:
                            container = self.eval_sibling(context, arg1)
                            idx = self.eval_sibling(context, arg2)

                            if not isinstance(idx, int):
                                raise Exception("Index must be an integer")

                            try:
                                return (
                                    container[idx]
                                    if container and len(container) > idx
                                    else None
                                )
                            except Exception as e:
                                raise Exception(f"Index error: {e}")

                case "store_val":
                    num_names = 0
                    for i in range(len(c) - 1):
                        if isinstance(c[i], Token) and c[i].type == "NAME":
                            num_names += 1
                    # now eval all exprs
                    exprs = c[num_names:]
                    vals = [self.eval_sibling(context, e) for e in exprs]

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
                            raise Exception(
                                f"Expected 1 value for single assignment, got {len(vals)}"
                            )
                        vals = [vals[0]]

                    for i in range(num_names):
                        name = str(c[i])
                        val = vals[i]
                        # check if outer
                        if name in context.outer_vars:
                            outer_ctx = context.outer_vars[name]
                            outer_ctx.vars[name] = val
                        else:
                            context.vars[name] = val
                    return None

                case "expr_stmt":
                    match c:
                        case [expr]:
                            return self.eval_sibling(context, expr)

                case "print_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            # Print all arguments separated by spaces
                            print(*args)
                            return None

                # special type of built in that returns the evaluated arguments
                case "return_stmt":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            return ControlSignal(args, RET_SIG)

                case "swap_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            # make sure first arg is list
                            if len(args) != 3:
                                raise Exception(
                                    f"swap() takes exactly 3 arguments, got {len(args)}"
                                )
                            lst = args[0]
                            idx1 = int(args[1])
                            idx2 = int(args[2])
                            if not isinstance(lst, list):
                                raise Exception(
                                    "First argument to swap() must be a list"
                                )
                            if (
                                idx1 < 0
                                or idx1 >= len(lst)
                                or idx2 < 0
                                or idx2 >= len(lst)
                            ):
                                raise Exception("swap() index out of range")
                            lst[idx1], lst[idx2] = lst[idx2], lst[idx1]
                            # return the modified list
                            return lst

                case "copy_func":
                    match c:
                        case [val_node]:
                            val = self.eval_sibling(context, val_node)
                            if isinstance(val, list):
                                return val.copy()
                            if isinstance(val, tuple):
                                return tuple(val)
                            return val  # for other types, just return as is

                case "and_op":
                    match c:
                        case [left, right]:
                            left_val = self.eval_sibling(context, left)
                            if not left_val:
                                return 0
                            right_val = self.eval_sibling(context, right)
                            return 1 if right_val else 0
                        case _:
                            raise Exception("and_op requires exactly two operands")

                case "or_op":
                    match c:
                        case [left, right]:
                            left_val = self.eval_sibling(context, left)
                            if left_val:
                                return 1
                            right_val = self.eval_sibling(context, right)
                            return 1 if right_val else 0
                        case _:
                            raise Exception("or_op requires exactly two operands")

                case "func_def":
                    match c:
                        case [name_node, *rest]:
                            name = str(name_node)

                            # Find the block/tree child (stmt_block)
                            body = None
                            params = []

                            for child in rest:
                                if isinstance(child, Tree) and child.data == "params":
                                    params = self.eval_sibling(context, child)
                                elif (
                                    isinstance(child, Tree)
                                    and child.data == "stmt_block"
                                ):
                                    body = child

                            if body is None:
                                raise Exception(f"Function body missing for {name}")

                            context.funcs[name] = (params, body)
                            return f"Defined {name}({', '.join(params)})"

                case "args":
                    return [self.eval_sibling(context, x) for x in c]
                case "break_stmt":
                    # emit break signal
                    return ControlSignal([], BRK_SIG)
                case "continue_stmt":
                    return ControlSignal([], CNT_SIG)

                case "call":
                    match c:
                        case [name_node, args_node] if (
                            isinstance(args_node, Tree) and args_node.data == "args"
                        ):
                            name = str(name_node)
                            arg_values = self.eval_sibling(context, args_node)
                        case [name_node]:
                            name = str(name_node)
                            arg_values = []
                        case _:
                            raise Exception("Invalid call syntax")

                    if name not in context.funcs:
                        raise Exception(f"Function not found: {name}")

                    params, body = context.funcs[name]
                    if len(arg_values) != len(params):
                        raise Exception(
                            f"Arity mismatch: {name} expects {len(params)} args"
                        )

                    # Create child context: copy global scope and layer local scope on top
                    local_vars = dict(zip(params, arg_values))
                    child_context = context.create_child_context(
                        local_vars=local_vars, node=body
                    )
                    v = self.eval(child_context)
                    match v:
                        case ControlSignal(signal=signal) if signal is RET_SIG:
                            return v.get_single() if v.is_single() else v.get_multiple()

                    # return is optional, so if values are present return them
                    return v if v is not None else 0

                # arithmetic
                case "add":
                    match c:
                        case [left, right]:
                            a = self.eval_sibling(context, left)
                            b = self.eval_sibling(context, right)
                            if isinstance(a, str) or isinstance(b, str):
                                return str(a) + str(b)
                            return a + b

                case "sub":
                    match c:
                        case [left, right]:
                            return self.eval_sibling(context, left) - self.eval_sibling(
                                context, right
                            )

                case "neg":
                    match c:
                        case [operand]:
                            return -self.eval_sibling(context, operand)

                case "mul":
                    match c:
                        case [left, right]:
                            return self.eval_sibling(context, left) * self.eval_sibling(
                                context, right
                            )

                case "div":
                    match c:
                        case [left, right]:
                            return self.eval_sibling(context, left) / self.eval_sibling(
                                context, right
                            )

                case "mod":
                    match c:
                        case [left, right]:
                            result = self.eval_sibling(
                                context, left
                            ) % self.eval_sibling(context, right)
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
                    return tuple(self.eval_sibling(context, child) for child in c)

                case "list":
                    match c:
                        case []:
                            # Empty list
                            return []
                        case [list_items_node] if (
                            isinstance(list_items_node, Tree)
                            and list_items_node.data == "list_items"
                        ):
                            # List with items
                            return self.eval_sibling(context, list_items_node)
                        case _:
                            return []

                case "list_items":
                    # Evaluate all items and return as list
                    return [self.eval_sibling(context, child) for child in c]

                # comparisons (return 1/0 like you had)
                case "gt":
                    match c:
                        case [left, right]:
                            return (
                                1
                                if self.eval_sibling(context, left)
                                > self.eval_sibling(context, right)
                                else 0
                            )

                case "lt":
                    match c:
                        case [left, right]:
                            return (
                                1
                                if self.eval_sibling(context, left)
                                < self.eval_sibling(context, right)
                                else 0
                            )

                case "ge":
                    match c:
                        case [left, right]:
                            return (
                                1
                                if self.eval_sibling(context, left)
                                >= self.eval_sibling(context, right)
                                else 0
                            )

                case "le":
                    match c:
                        case [left, right]:
                            return (
                                1
                                if self.eval_sibling(context, left)
                                <= self.eval_sibling(context, right)
                                else 0
                            )

                case "eq":
                    match c:
                        case [left, right]:
                            # check if comparing to null
                            first_eval = self.eval_sibling(context, left)
                            second_eval = self.eval_sibling(context, right)
                            # check for null comparison
                            if first_eval is None:
                                return 1 if second_eval is None else 0
                            if second_eval is None:
                                return 1 if first_eval is None else 0
                            return 1 if first_eval == second_eval else 0

                case "ne":
                    match c:
                        case [left, right]:
                            first_eval = self.eval_sibling(context, left)
                            second_eval = self.eval_sibling(context, right)
                            # check for null comparison
                            if first_eval is None:
                                return 0 if second_eval is None else 1
                            if second_eval is None:
                                return 0 if first_eval is None else 1

                            return 1 if first_eval != second_eval else 0

                case "loop_stmt":
                    match c:
                        case [condition, block]:
                            while self.eval_sibling(context, condition) != 0:
                                v = self.eval_sibling(context, block)
                                match v:
                                    case ControlSignal(signal=signal) if (
                                        signal is BRK_SIG
                                    ):
                                        break
                                    case ControlSignal(signal=signal) if (
                                        signal is CNT_SIG
                                    ):
                                        continue
                                    case ControlSignal(signal=signal) if (
                                        signal is RET_SIG
                                    ):
                                        return v
                            return 0

                case "wait_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) >= 1 and len(args) <= 3:
                                duration = args[0]
                                # if second arg is scalar, make it (0, scalar)
                                random_range = (0, 0)

                                if len(args) == 3:
                                    random_range = (args[1], args[2])
                                elif len(args) == 2:
                                    random_range = (0, args[1])
                            else:
                                raise Exception(
                                    f"wait() takes 1 - 3 arguments, got {len(args)}"
                                )
                            return wait_func(duration, random_range)

                case "rand_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) == 1:
                                low = 0
                                high = args[0]
                            elif len(args) == 2:
                                low = args[0]
                                high = args[1]
                            else:
                                raise Exception(
                                    f"rand() takes 1 or 2 arguments, got {len(args)}"
                                )
                            return random.uniform(low, high)

                case "rand_i_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) == 1:
                                low = 0
                                high = args[0]
                            elif len(args) == 2:
                                low = args[0]
                                high = args[1]
                            else:
                                raise Exception(
                                    f"rand_i() takes 1 or 2 arguments, got {len(args)}"
                                )
                            return random.randint(low, high)

                case "foreach_tick_func":
                    match c:
                        case [tick_provider_name_node, func_name_node]:
                            tick_provider_name = str(tick_provider_name_node)
                            func_name = str(func_name_node)

                            while True:
                                if tick_provider_name not in context.funcs:
                                    raise Exception(
                                        f"Tick provider func not found: {tick_provider_name}"
                                    )
                                _, tick_provider_body = context.funcs[
                                    tick_provider_name
                                ]

                                # controls timeout
                                results = self.eval_sibling(context, tick_provider_body)
                                if results is None or (
                                    isinstance(results, ControlSignal)
                                    and results.is_signal(EXIT_SIG)
                                ):
                                    break
                                # call the function
                                if func_name not in context.funcs:
                                    raise Exception(f"Function not found: {func_name}")
                                _, body = context.funcs[func_name]
                                # Evaluate function body in current context
                                results = self.eval_sibling(context, body)
                            return results

                case "mouse_move_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 3:
                                raise Exception(
                                    f"mouse_move() takes at least 3 arguments, got {len(args)}"
                                )
                            x_offset = args[0]
                            y_offset = args[1]
                            if x_offset is None or y_offset is None:
                                return None
                            pps = args[2]
                            humanLike = bool(args[3]) if len(args) >= 4 else True
                            move_mouse_to(x_offset, y_offset, pps, humanLike)
                            return 0

                case "set_template_dir_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) == 0:
                                raise Exception(
                                    f"set_template_dir() takes exactly 1 argument, got {len(args)}"
                                )
                            self.template_dir = str(args)
                            print(f"Template directory set to: {self.template_dir}")
                            return self.template_dir
                            # Here you would set the template directory in your application

                case "find_template_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) != 1 and len(args) != 5:
                                raise Exception(
                                    f"find_template() takes 1 or 5 arguments (template_name [, left, top, width, height]), got {len(args)}"
                                )
                            template_name = str(args[0])
                            region = None
                            if len(args) == 5:
                                # region format: (left, top, width, height)
                                region = (args[1], args[2], args[3], args[4])
                            pos = locate_template_on_screen(
                                template_dir=self.template_dir,
                                template_name=template_name,
                                downscale=1.0,
                            )
                            if pos is not None and len(pos) != 0:
                                return pos[0][0], pos[0][1]
                            return None, None  # not found

                case "find_templates_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 1 or len(args) > 6:
                                raise Exception(
                                    f"find_templates() takes 1 to 6 arguments (template_name [, left, top, width, height, top_k]), got {len(args)}"
                                )
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
                                top_k=top_k,
                            )
                            if positions is not None and len(positions) > 0:
                                # Return tuple of tuples
                                return tuple(positions)
                            return tuple()  # empty tuple if not found

                case "get_coordinates_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 1 or len(args) > 2:
                                raise Exception(
                                    f"get_coordinates() takes 1 or 2 arguments (message [, use_cache]), got {len(args)}"
                                )
                            message = str(args[0])
                            use_cache = bool(args[1]) if len(args) == 2 else False
                            x, y = get_coordinates_interactive(message, use_cache)
                            return (x, y)

                case "check_pixel_color_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 6 or len(args) > 7:
                                raise Exception(
                                    f"check_pixel_color() takes 6 or 7 arguments (x, y, radius, r, g, b [, tolerance]), got {len(args)}"
                                )
                            x = int(args[0])
                            y = int(args[1])
                            radius = int(args[2])
                            target_r = int(args[3])
                            target_g = int(args[4])
                            target_b = int(args[5])
                            tolerance = int(args[6]) if len(args) == 7 else 0
                            found = check_pixel_color_in_radius(
                                x, y, radius, target_r, target_g, target_b, tolerance
                            )
                            return 1 if found else 0

                case "get_pixel_color_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 1 or len(args) > 2:
                                raise Exception(
                                    f"get_pixel_color() takes 1 or 2 arguments (alias [, use_cache]), got {len(args)}"
                                )
                            alias = str(args[0])
                            use_cache = bool(args[1]) if len(args) == 2 else False
                            r, g, b = get_pixel_color_interactive(alias, use_cache)
                            return (r, g, b)

                case "conditional_expr":
                    match c:
                        case [condition_node, t_block]:
                            condition = self.eval_sibling(context, condition_node)
                            if condition:
                                return self.eval_sibling(context, t_block)
                            return None
                        case [condition_node, t_block, f_block]:
                            condition = self.eval_sibling(context, condition_node)
                            if condition:
                                return self.eval_sibling(context, t_block)
                            else:
                                return self.eval_sibling(context, f_block)

                case "left_click_func":
                    left_click()
                    return 0

                case "send_input_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) != 3:
                                raise Exception(
                                    f"send_input() takes exactly 3 arguments (type, key, action), got {len(args)}"
                                )
                            t = str(args[0])
                            key = str(args[1])
                            action = str(args[2])
                            send_input(t, key, action)
                            return 0

                case "press_and_release_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 2:
                                raise Exception(
                                    f"press_and_release() takes at least 2 arguments (delay_ms, key1, [key2, ...]), got {len(args)}"
                                )
                            delay_ms = int(args[0])
                            keys = [str(k) for k in args[1:]]
                            press_and_release(delay_ms, *keys)
                            return 0

                case "record_func":
                    match c:
                        case [args_node]:
                            new_ctx = context.create_sibling_context(node=args_node)
                            new_ctx.debug = False  # disable debug during recording
                            args = self.eval(new_ctx)
                            if len(args) < 1 or len(args) > 3:
                                raise Exception(
                                    f"record() takes 1-3 arguments (recording_name [, start_button, stop_button]), got {len(args)}"
                                )
                            recording_name = str(args[0])
                            start_button = str(args[1]) if len(args) >= 2 else "space"
                            stop_button = str(args[2]) if len(args) == 3 else "esc"
                            # inf means only cares about points before events and not mimicking mouse path
                            squash_distance = (
                                int(args[3]) if len(args) == 4 else float("inf")
                            )
                            record_interactive(
                                recording_name,
                                start_button,
                                stop_button,
                                squash_distance,
                            )
                            return 0

                case "playback_func":
                    match c:
                        case [args_node]:
                            new_ctx = context.create_sibling_context(node=args_node)
                            new_ctx.debug = False  # disable debug during playback
                            args = self.eval(new_ctx)
                            if len(args) < 1 or len(args) > 2:
                                raise Exception(
                                    f"playback() takes 1-2 arguments (recording_name [, stop_button]), got {len(args)}"
                                )
                            recording_name = str(args[0])
                            stop_button = str(args[1]) if len(args) == 2 else "esc"
                            playback_interactive(recording_name, stop_button)
                            return 0

                case "recording_exists_func":
                    match c:
                        case [name_node]:
                            recording_name = str(self.eval_sibling(context, name_node))
                            return 1 if recording_exists(recording_name) else 0

                case "len_func":
                    match c:
                        case [val_node]:
                            val = self.eval_sibling(context, val_node)
                            if val is None:
                                return 0
                            if isinstance(val, (tuple, list, str)):
                                return len(val)
                            raise Exception(
                                f"len() requires a tuple, list, or string, got {type(val)}"
                            )

                case "time_func":
                    return time.time()

                case "shuffle_func":
                    match c:
                        case [val_node]:
                            val = self.eval_sibling(context, val_node)
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
                            raise Exception(
                                f"shuffle() requires a tuple or list, got {type(val)}"
                            )

                case "get_pixel_at_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) != 2:
                                raise Exception(
                                    f"get_pixel_at() takes exactly 2 arguments (x, y), got {len(args)}"
                                )
                            x = int(args[0])
                            y = int(args[1])
                            # Capture pixel color at the specified coordinates
                            screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
                            pixel = screenshot.getpixel((0, 0))
                            r, g, b = pixel[0], pixel[1], pixel[2]
                            return (r, g, b)

                case "append_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) != 2:
                                raise Exception(
                                    f"append() takes exactly 2 arguments (list, item), got {len(args)}"
                                )
                            lst = args[0]
                            item = args[1]
                            if not isinstance(lst, list):
                                raise Exception(
                                    f"append() requires a list as first argument, got {type(lst)}"
                                )
                            # Append the item to the list (modifies in place)
                            lst.append(item)
                            return lst

                case "pop_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 1 or len(args) > 2:
                                raise Exception(
                                    f"pop() takes 1 or 2 arguments (list [, index]), got {len(args)}"
                                )
                            lst = args[0]
                            if not isinstance(lst, list):
                                raise Exception(
                                    f"pop() requires a list as first argument, got {type(lst)}"
                                )
                            if len(lst) == 0:
                                raise Exception("pop() called on empty list")
                            # Pop from specific index or from end
                            if len(args) == 2:
                                index = int(args[1])
                                if index < 0 or index >= len(lst):
                                    raise Exception(
                                        f"pop() index {index} out of range for list of length {len(lst)}"
                                    )
                                return lst.pop(index)
                            else:
                                return lst.pop()

                case "capture_region_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 1 or len(args) > 2:
                                raise Exception(
                                    f"capture_region() takes 1 or 2 arguments (region_key [, overwrite_cache]), got {len(args)}"
                                )
                            region_key = str(args[0])
                            overwrite_cache = bool(args[1]) if len(args) == 2 else False
                            region = region_capture(region_key, overwrite_cache)
                            return region

                case "mouse_position_func":
                    pos = pyautogui.position()
                    return (pos.x, pos.y)

                case "ocr_find_text_func":
                    match c:
                        case [args_node]:
                            args = self.eval_sibling(context, args_node)
                            if len(args) < 0 or len(args) > 4:
                                raise Exception(
                                    f"ocr_find_text() takes 0 to 4 arguments (region, min_conf, filter, upscale), got {len(args)}"
                                )

                            # Parse arguments with defaults
                            region = (
                                args[0]
                                if len(args) >= 1 and args[0] is not None
                                else None
                            )
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
                            results = ocr_find_text(
                                region=region,
                                min_conf=min_conf,
                                filter=filter_text,
                                upscale=upscale,
                            )
                            if results is None:
                                return []
                            # Convert OCRResult objects to tuples for macroni
                            # Format: [(text, conf, [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]), ...]
                            return [(r.text, r.conf, r.bbox) for r in results]

                # passthrough for inlined rules
                case _ if len(c) == 1:
                    return self.eval_sibling(context, c[0])

                case _:
                    raise Exception(f"Unknown tree node: {t}")

        raise Exception(f"Unknown node type: {type(node)}")


def wait_func(duration, random_range: tuple = (0, 0)):
    wait_time = duration
    random_delay = random.uniform(random_range[0], random_range[1])
    print(f"Waiting for {wait_time + random_delay} ms...")
    time.sleep((wait_time + random_delay) / 1000)
    return wait_time + random_delay


def load_coordinates_cache(cache_file="coordinates_cache.json"):
    """Load cached coordinates from JSON file."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache file: {e}")
            return {}
    return {}


def save_coordinates_cache(cache, cache_file="coordinates_cache.json"):
    """Save coordinates cache to JSON file."""
    try:
        with open(cache_file, "w") as f:
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
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load pixel colors cache file: {e}")
            return {}
    return {}


def save_pixel_colors_cache(cache, cache_file="pixel_colors_cache.json"):
    """Save pixel colors cache to JSON file."""
    try:
        with open(cache_file, "w") as f:
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


def check_pixel_color_in_radius(
    center_x, center_y, radius, target_r, target_g, target_b, tolerance=0
):
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
                if (
                    abs(r - target_r) <= tolerance
                    and abs(g - target_g) <= tolerance
                    and abs(b - target_b) <= tolerance
                ):
                    return True

    return False


def load_recordings_cache(cache_file="recordings_cache.json"):
    """Load cached recordings from JSON file."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load recordings cache file: {e}")
            return {}
    return {}


def save_recordings_cache(cache, cache_file="recordings_cache.json"):
    """Save recordings cache to JSON file."""
    try:
        with open(cache_file, "w") as f:
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


def record_interactive(
    recording_name, start_button="space", stop_button="esc", squash_distance=50
):
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
    print(f"Recording will compress mouse movements for natural playback")
    print(f"{'='*60}\n")

    # Use output_handler's record function which compresses mouse movements
    events = output_handler.record(
        distance_threshold=squash_distance,
        start_button=start_button,
        stop_button=stop_button,
    )

    # Convert RecordedEvent dataclasses to dicts for JSON serialization
    import dataclasses

    events_dict = [dataclasses.asdict(e) for e in events]

    # Save to cache
    cache = load_recordings_cache(cache_file)
    cache[recording_name] = events_dict
    save_recordings_cache(cache, cache_file)
    print(f"✓ Saved recording '{recording_name}' to cache.")


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

    events_dict = cache[recording_name]

    print(f"\n{'='*60}")
    print(f"PLAYBACK MODE: {recording_name}")
    print(f"{'='*60}")
    print(f"Total events: {len(events_dict)}")
    print(f"Mouse movements will use randomized human-like curves")
    print(f"{'='*60}")
    print(f"Playback will start in 3 seconds...")
    print(f"{'='*60}\n")

    time.sleep(3)

    # Convert dict format back to RecordedEvent objects
    events = []
    for event_data in events_dict:
        events.append(
            output_handler.RecordedEvent(
                timestamp=event_data["timestamp"],
                kind=event_data["kind"],
                key=event_data["key"],
                action=event_data["action"],
                to_coordinates=(
                    tuple(event_data["to_coordinates"])
                    if "to_coordinates" in event_data and event_data["to_coordinates"]
                    else None
                ),
                from_coordinates=(
                    tuple(event_data["from_coordinates"])
                    if "from_coordinates" in event_data
                    and event_data["from_coordinates"]
                    else None
                ),
                duration_ms=event_data.get("duration_ms"),
            )
        )

    # Use output_handler's playback which uses smooth, randomized mouse movement
    output_handler.playback(events, stop_button=stop_button)
