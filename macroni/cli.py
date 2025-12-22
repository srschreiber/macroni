import click
from macroni.interpreter.macroni_interpret import Interpreter
from macroni.interpreter.macroni_debugger import Debugger
from macroni.interpreter.macroni_interpret import calc_parser

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
    
    dbg = Debugger()
    if debug:
        dbg.set_breakpoints(list(breakpoints))

    # Parse and execute the script
    interp = Interpreter()
    tree = calc_parser.parse(script_content)
    interp.eval(tree)


if __name__ == "__main__":
    main()
