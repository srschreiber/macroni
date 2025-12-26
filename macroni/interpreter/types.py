from dataclasses import dataclass


class ExecutionContext:
    def __init__(
        self,
        vars=None,
        funcs=None,
        depth=0,
        node: any = None,
        eval_cback=None,
        debug=False,
        parent: "ExecutionContext" = None,
        outer_vars=None,
    ):
        """
        Initialize execution context.

        Args:
            vars: Dictionary of variables (if None, creates empty dict)
            funcs: Dictionary of functions (if None, creates empty dict)
            depth: Current recursion depth
            outer_vars: Dictionary mapping variable names to their outer contexts
        """
        self.vars = vars if vars is not None else {}
        self.funcs = funcs if funcs is not None else {}
        self.depth = depth
        self.node = node  # Current AST node being executed
        self.eval_cback = eval_cback  # Optional callback to evaluate nodes
        self.debug = debug  # Enable debugging features
        self.parent = parent  # Reference to parent context, if any
        self.outer_vars = outer_vars if outer_vars is not None else {}

    def create_sibling_context(self, node: any = None):
        """
        Create a sibling context at the same depth.
        Shares vars and funcs references (not copies) so changes are visible across siblings.

        Returns:
            ExecutionContext: New sibling context
        """
        return ExecutionContext(
            vars=self.vars,
            funcs=self.funcs,
            depth=self.depth,
            node=node,
            debug=self.debug,
            eval_cback=self.eval_cback,
            parent=self.parent,
            outer_vars=self.outer_vars,
        )

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

        return ExecutionContext(
            vars=child_vars,
            funcs=child_funcs,
            depth=self.depth + 1,
            node=node,
            debug=self.debug,
            eval_cback=self.eval_cback,
            parent=self,
            outer_vars={},  # Start with empty outer_vars for child context
        )
