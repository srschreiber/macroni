import enum
from collections.abc import Iterable
from .types import ExecutionContext
from macroni.interpreter.grammar import calc_parser

try:
    import readline
except ImportError:
    try:
        import pyreadline3
    except ImportError:
        pass


class StepMode(enum.Enum):
    RUN = "run"
    STEP = "step"
    NEXT = "next"
    OUT = "out"


class Debugger:
    def __init__(self):
        self.breakpoints = set()
        self.mode: StepMode = StepMode.RUN
        self.target_depth = None
        self.last_line = None

    def set_breakpoints(self, breakpoints: Iterable[any]):
        bps = set(map(int, breakpoints))
        print(f"Setting breakpoints: {bps}")
        self.breakpoints = bps

    def maybe_pause(self, ctx: ExecutionContext = None):
        if ctx is None or not ctx.debug:
            return
        line = getattr(ctx.node.meta, "line", None)
        print(f"Checking line {line} at call depth {ctx.depth if ctx else 'unknown'}")
        if line is None:
            return

        line = int(line)
        if line in self.breakpoints:
            print(f"Hit breakpoint at line {line}")
            self._pause(ctx=ctx, reason="breakpoint")
            return

        match self.mode:
            case StepMode.STEP:
                if self.last_line is None or line != self.last_line:
                    self.mode = StepMode.RUN
                    self._pause(ctx, reason="step")
                    return
            case StepMode.NEXT:
                if ctx.depth <= self.target_depth and line != self.last_line:
                    self.mode = StepMode.RUN
                    self._pause(ctx, reason="next")
                    return
            case StepMode.OUT:
                if ctx.depth < self.target_depth:
                    self.mode = StepMode.RUN
                    self._pause(ctx, reason="out")
                    return

        self.last_line = line

    def _pause(self, ctx: ExecutionContext, reason):
        print(f"Paused ({reason}) at line {ctx.node.meta.line}")
        self.last_line = ctx.node.meta.line
        self.repl(ctx)

    def repl(self, ctx: ExecutionContext):
        while True:
            cmd = input("(dbg) ").strip()
            if cmd == "c":
                self.mode = StepMode.RUN
                return
            if cmd == "s":
                self.mode = StepMode.STEP
                return
            if cmd == "n":
                self.mode = StepMode.NEXT
                self.target_depth = ctx.depth
                return
            if cmd == "o":
                self.mode = StepMode.OUT
                self.target_depth = ctx.depth
                return
            if cmd == "mem":
                print(f"vars: {ctx.vars}")
                print(f"funcs: {ctx.funcs}")
                continue
            if cmd.startswith("eval "):
                expression = cmd[5:].strip()
                if not expression:
                    print("Error: eval requires an expression")
                    continue
                try:
                    parsed_expr = calc_parser.parse(expression)
                    eval_ctx = ctx.create_sibling_context(node=parsed_expr)
                    # do not step through eval
                    eval_ctx.debug = False
                    if ctx.eval_cback is None:
                        print("Error: eval callback not set in context")
                        continue
                    result = ctx.eval_cback(eval_ctx)
                    print(f"Result: {result}")
                except Exception as e:
                    print(f"Error evaluating expression: {e}")
                continue
