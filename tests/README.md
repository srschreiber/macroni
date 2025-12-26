# Macroni Test Suite

This directory contains comprehensive tests for the macroni language interpreter.

## Test Files

### Core Language Features

1. **test_arithmetic.macroni** - Arithmetic operations
   - Addition, subtraction, multiplication, division, modulo
   - Negation
   - Complex expressions
   - String concatenation

2. **test_comparisons.macroni** - Comparison operators
   - Greater than, less than
   - Greater/less than or equal
   - Equality and inequality
   - Null comparisons

3. **test_logical.macroni** - Logical operators
   - AND (&&) and OR (||) operators
   - Short-circuit evaluation
   - Complex logical expressions

4. **test_conditionals.macroni** - Conditional expressions
   - If-else statements
   - Nested conditionals
   - Conditionals with logical operators

### Control Flow

5. **test_loops.macroni** - Loop statements
   - While loops
   - Break statements
   - Nested loops
   - Loop with early return
   - Accumulator patterns

6. **test_functions.macroni** - Function definitions and calls
   - Simple functions
   - Functions with parameters
   - Function calls between functions
   - Recursive functions
   - Early returns
   - Implicit returns

### Data Structures

7. **test_lists.macroni** - List operations
   - Creating lists
   - Indexing
   - Append, pop, copy, swap
   - Nested lists
   - Shuffle

8. **test_tuples.macroni** - Tuple operations
   - Creating tuples
   - Indexing
   - Destructuring assignment
   - Nested tuples
   - Functions returning tuples

### Advanced Features

9. **test_scope.macroni** - Variable scope
   - Global scope
   - Function local scope
   - Variable shadowing
   - Outer keyword for modifying outer scope
   - Nested function scopes

10. **test_assignments.macroni** - Variable assignments
    - Simple assignments
    - Multiple assignments
    - Destructuring assignments
    - Assignment from expressions and functions

11. **test_builtin_funcs.macroni** - Built-in functions (non-visual)
    - len, time
    - rand, rand_i
    - append, pop, copy, swap, shuffle

12. **test_edge_cases.macroni** - Edge cases and special scenarios
    - Empty functions
    - Deeply nested structures
    - Loops that never execute
    - Null handling
    - Out of bounds access
    - Multiple return paths

## Running Tests

To run a test file:

```bash
python3 -m macroni.cli tests/test_arithmetic.macroni
```

To run all tests:

```bash
for test in tests/test_*.macroni; do
    echo "Running $test..."
    python3 -m macroni.cli "$test"
    echo "---"
done
```

## Expected Behavior

Each test file includes expected output in comments. Review the output to verify correctness.

## Notes

- These tests do NOT include vision/mouse/pixel color functions
- Tests focus on language semantics and core features
- Some edge cases may intentionally cause errors to test error handling
