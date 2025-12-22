import click
from macroni.interpreter.macroni_interpret import Interpreter
from macroni.interpreter.macroni_interpret import DBG
from macroni.interpreter.grammar import calc_parser
from macroni.interpreter.types import ExecutionContext

def count_brackets(text):
    """Count unmatched opening brackets/braces in text."""
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    closing = set(pairs.values())

    for char in text:
        if char in pairs:
            stack.append(char)
        elif char in closing:
            if stack and pairs[stack[-1]] == char:
                stack.pop()

    return len(stack)

def run_interactive(debug=False):
    """Run macroni in interactive mode."""
    print("Macroni Interactive Mode")
    print("Enter code (will execute when brackets/braces are balanced)")
    print()

    interp = Interpreter()
    # Create a persistent context to maintain variables between commands
    persistent_context = ExecutionContext(debug=debug, eval_cback=interp.eval)

    while True:
        try:
            buffer = ""
            prompt = ">>> "

            while True:
                line = input(prompt)
                buffer += line + "\n"

                # Check if we have any closing brackets or braces
                has_closing = ']' in line or '}' in line
                end_of_stmt = line.strip().endswith(';') or line.strip() == ''

                # Count unmatched brackets
                unclosed = count_brackets(buffer)

                # Execute when we see a closing bracket/brace and all brackets are balanced
                if has_closing and unclosed == 0:
                    print("Executing...")
                    break
                elif unclosed == 0 and end_of_stmt:
                    print("Executing...")
                    break


                # Continue reading on next line if brackets not balanced
                prompt = "... "

            # Parse and execute the accumulated code
            if buffer.strip():
                tree = calc_parser.parse(buffer)
                # Update the node in the persistent context and execute
                persistent_context.node = tree
                result = interp.eval(persistent_context)
                if result is not None:
                    print(result)

        except EOFError:
            print("\nExiting...")
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Use Ctrl+D to exit.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

@click.command()
@click.option('-f', '--file', 'filepath', required=False, help='Path to the macroni script file to execute.', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode with verbose output.')
# list of breakpoints
@click.option('-b', '--breakpoints', multiple=True, help='List of breakpoints to set in the script (by line number).')
def main(filepath, debug, breakpoints: list):
    """Run a macroni script from a file or start interactive mode."""

    # If no file provided, start interactive mode
    if not filepath:
        run_interactive(debug=debug)
        return

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
