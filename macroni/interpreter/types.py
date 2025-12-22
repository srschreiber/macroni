class ExecutionContext:
    def __init__(self, vars=None, funcs=None, depth=0, node: any = None, eval_cback = None, debug=False):
        """
        Initialize execution context.

        Args:
            vars: Dictionary of variables (if None, creates empty dict)
            funcs: Dictionary of functions (if None, creates empty dict)
            depth: Current recursion depth
        """
        self.vars = vars if vars is not None else {}
        self.funcs = funcs if funcs is not None else {}
        self.depth = depth
        self.node = node  # Current AST node being executed
        self.eval_cback = eval_cback  # Optional callback to evaluate nodes
        self.debug = debug  # Enable debugging features

    def create_sibling_context(self, node: any = None):
        """
        Create a sibling context at the same depth.
        Copies current vars and funcs.

        Returns:
            ExecutionContext: New sibling context
        """
        return ExecutionContext(vars=dict(self.vars), funcs=dict(self.funcs), depth=self.depth, node=node, debug=self.debug, eval_cback=self.eval_cback)

    def create_child_context(self, local_vars=None, node: any = None):
        """
        Create a child context for function calls.
        Copies current vars and funcs, layers local vars on top.
        Increments depth.

        Args:
            local_vars: Dictionary of local variables to layer on top

        Returns:
            ExecutionContext: New child context with incremented depth
        """
        # Copy vars and funcs from parent (global scope)
        child_vars = dict(self.vars)
        child_funcs = dict(self.funcs)

        # Layer local vars on top
        if local_vars:
            child_vars.update(local_vars)

        return ExecutionContext(vars=child_vars, funcs=child_funcs, depth=self.depth + 1, node=node, debug=self.debug, eval_cback=self.eval_cback)
