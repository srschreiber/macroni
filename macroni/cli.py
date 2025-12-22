import click
from macroni.interpreter.macroni_interpret import Interpreter
from macroni.interpreter.macroni_interpret import DBG
from macroni.interpreter.grammar import calc_parser
from macroni.interpreter.types import ExecutionContext

@click.command()
@click.option('-f', '--file', 'filepath', required=True, help='Path to the macroni script file to execute.', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode with verbose output.')
# list of breakpoints
@click.option('-b', '--breakpoints', multiple=True, help='List of breakpoints to set in the script (by line number).')
def main(filepath, debug, breakpoints: list):
    """Run a macroni script from a file."""
    # Read the script from the file
    with open(filepath, 'r') as f:
        script_content = f.read()
    
    if debug:
        DBG.set_breakpoints(list(breakpoints))

    # Parse and execute the script
    interp = Interpreter()
    tree = calc_parser.parse(script_content)
    root_context = ExecutionContext(node=tree, debug=debug, eval_cback=interp.eval)
    interp.eval(root_context)


if __name__ == "__main__":
    main()
