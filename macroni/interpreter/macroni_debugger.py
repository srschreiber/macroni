import enum
from collections.abc import Iterable

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

    def set_breakpoints(self, breakpoints: Iterable[int]):
        self.breakpoints = set(breakpoints)
    
    def maybe_pause(self, node, call_depth):
        line = getattr(node.meta, "line", None)
        if line is None:
            return


        if line in self.breakpoints:
            self._pause(node, call_depth, reason="breakpoint")
            return
        
        match self.mode:
            case StepMode.STEP:
                if self.last_line is None or line != self.last_line:
                    self.mode = StepMode.RUN
                    self._pause(node, call_depth, reason="step")
                    return
            case StepMode.NEXT:
                if call_depth <= self.target_depth and line != self.last_line:
                    self.mode = StepMode.RUN
                    self._pause(node, call_depth, reason="next")
                    return
            case StepMode.OUT:
                if call_depth < self.target_depth:
                    self.mode = StepMode.RUN
                    self._pause(node, call_depth, reason="out")
                    return

        self.last_line = line

    def _pause(self, node, call_depth, reason):
        print(f"Paused ({reason}) at line {node.meta.line}")
        self.last_line = node.meta.line
        self.repl(node, call_depth)

    def repl(self, node, call_depth):
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
                self.target_depth = call_depth
                return
            if cmd == "o":
                self.mode = StepMode.OUT
                self.target_depth = call_depth
                return
