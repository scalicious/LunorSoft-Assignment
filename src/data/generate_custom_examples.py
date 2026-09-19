import json
import os

examples = []

# 1. explain-concept (20 examples)
concepts = [
    ("list comprehensions", "a concise way to create lists based on existing lists. For example: `[x**2 for x in range(10)]` creates a list of squares. They are often faster and more readable than standard for-loops."),
    ("generators", "functions that use the `yield` keyword instead of `return`. They produce a sequence of values lazily, pausing execution and saving state between yields, which is highly memory efficient for large datasets."),
    ("decorators", "functions that modify the behavior of other functions. They take a function as an argument and return a new function. In Python, they are applied using the `@` symbol above the function definition."),
    ("context managers", "objects that define `__enter__` and `__exit__` methods, used with the `with` statement to ensure resources like files or database connections are properly acquired and released even if exceptions occur."),
    ("lambda functions", "small, anonymous functions defined using the `lambda` keyword. They can take any number of arguments but can only have one expression. Often used as arguments for higher-order functions like `map()` or `filter()`."),
    ("type hinting", "a way to indicate the expected data types of variables, arguments, and return values. While Python doesn't enforce these at runtime, they help developers catch bugs early using tools like `mypy`."),
    ("duck typing", "a concept where an object's suitability is determined by the presence of certain methods and properties, rather than its actual type. 'If it walks like a duck and quacks like a duck, it must be a duck'."),
    ("virtual environments", "isolated Python environments that allow you to manage project-specific dependencies without conflicting with system-wide packages. Created using `venv` or `virtualenv`."),
    ("the Global Interpreter Lock (GIL)", "a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once. This makes standard Python multithreading ineffective for CPU-bound tasks."),
    ("monkey patching", "dynamically modifying or extending a class or module at runtime. It's often used for testing (mocking) or temporarily fixing a bug in a third-party library, though it can make code hard to debug."),
    ("metaclasses", "classes whose instances are themselves classes. They allow you to customize class creation. In Python, the default metaclass is `type`."),
    ("list vs tuple", "Lists are mutable, meaning their contents can be changed after creation. Tuples are immutable, meaning they cannot be altered once created. Tuples are faster and can be used as dictionary keys."),
    ("args and kwargs", "`*args` allows a function to accept any number of positional arguments as a tuple. `**kwargs` allows accepting any number of keyword arguments as a dictionary."),
    ("dunder methods", "Special methods surrounded by double underscores (e.g., `__init__`, `__str__`). They allow you to define how custom objects interact with Python's built-in operators and functions."),
    ("closures", "functions that remember the values in their enclosing lexical scope even when the flow of execution has left that scope. This is useful for data hiding and decorators."),
    ("recursion", "a programming technique where a function calls itself to solve smaller instances of the same problem. It requires a base case to prevent infinite loops."),
    ("memoization", "an optimization technique used primarily to speed up computer programs by storing the results of expensive function calls and returning the cached result when the same inputs occur again."),
    ("f-strings", "introduced in Python 3.6, they provide a concise and convenient way to embed expressions inside string literals for formatting. Example: `f'Hello, {name}'`."),
    ("the Walrus Operator", "`:=`, introduced in Python 3.8, allows you to assign values to variables as part of a larger expression. It is useful in while loops and comprehensions."),
    ("generators vs lists", "Lists store all elements in memory simultaneously. Generators yield one item at a time, making them infinitely more memory-efficient for massive datasets, though they can only be iterated over once.")
]
for i, (concept, explanation) in enumerate(concepts):
    examples.append({
        "instruction": f"Can you explain the concept of {concept} in Python to a beginner?",
        "output": f"Certainly! In Python, {concept} refers to {explanation}\n\n when you use {concept}, you are writing more Pythonic code that is easier to maintain. Always remember to practice using this concept in small scripts to get the hang of it!",
        "category": "explain-concept"
    })

# 2. debug-this (20 examples)
bugs = [
    ("def my_func(my_list=[]):\n    my_list.append(1)\n    return my_list", "Mutable default arguments. The list is created once at function definition, not on each call.", "Use `my_list=None` and initialize it to `[]` inside the function."),
    ("for i in range(len(items)):\n    print(items[i])", "Not Pythonic. While it works, it is discouraged to use `range(len())` to iterate.", "Use `for item in items:` directly, or `for i, item in enumerate(items):` if you need the index."),
    ("f = open('data.txt')\ndata = f.read()", "File is not closed, which can lead to resource leaks.", "Use a context manager: `with open('data.txt') as f:`."),
    ("except Exception:\n    pass", "Bare except/catching all exceptions and silencing them. This masks real errors and makes debugging impossible.", "Catch specific exceptions like `except ValueError:` and at least log the error."),
    ("import time\ntime = time.time()", "Shadowing the imported module name with a variable. You won't be able to use `time.sleep()` later.", "Rename the variable to something like `start_time = time.time()`."),
    ("a = [1, 2, 3]\nb = a\nb.append(4)", "Variables holding lists are references. Modifying `b` modifies `a`.", "Create a copy using `b = a.copy()` or `b = list(a)`."),
    ("if x == True:", "Explicit comparison to True is redundant and un-Pythonic.", "Simply write `if x:`."),
    ("print('Value is ' + 10)", "Type error. You cannot concatenate a string and an integer directly.", "Convert the integer to a string: `str(10)` or use f-strings: `f'Value is {10}'`."),
    ("my_dict = {[1, 2]: 'value'}", "Type error. Lists are unhashable and cannot be dictionary keys.", "Use a tuple instead: `my_dict = {(1, 2): 'value'}`."),
    ("try:\n  1/0\nexcept:\n  print('Error')", "Bare except block catches `KeyboardInterrupt` and `SystemExit`, making the script hard to stop.", "Use `except Exception as e:` or specifically `except ZeroDivisionError:`."),
    ("file_names = ['a.txt', 'b.txt']\n[os.remove(f) for f in file_names]", "Using list comprehensions for side effects instead of creating a list. This creates an unused list in memory.", "Use a standard `for` loop instead."),
    ("def sum(a, b):\n    return a + b\nx = sum([1,2,3])", "Shadowing the built-in `sum()` function.", "Rename your function to `add_numbers` or similar."),
    ("is_valid = True\nif is_valid is True:", "Using `is` for equality checks on booleans, which can be verbose.", "Just write `if is_valid:`."),
    ("x = 5\ndef update():\n    x += 1", "UnboundLocalError. The function creates a new local variable `x` instead of modifying the global one.", "Use `global x` inside the function, or better, pass it as a parameter and return it."),
    ("my_string = 'Hello'\nmy_string[0] = 'h'", "TypeError. Strings in Python are immutable.", "Create a new string: `my_string = 'h' + my_string[1:]`."),
    ("for i in my_list:\n    my_list.remove(i)", "Modifying a list while iterating over it leads to skipping elements.", "Iterate over a copy `for i in my_list[:]:` or use a list comprehension to filter."),
    ("my_tuple = (1)", "This creates an integer, not a tuple.", "Include a trailing comma for a single-element tuple: `my_tuple = (1,)`."),
    ("print 'Hello'", "SyntaxError in Python 3. `print` is a function, not a statement.", "Use parentheses: `print('Hello')`."),
    ("dict.keys()[0]", "TypeError in Python 3 because `dict.keys()` returns a view, not a list.", "Convert to a list first: `list(dict.keys())[0]` or use an iterator."),
    ("import module_that_does_not_exist", "ModuleNotFoundError.", "Ensure the module is installed via `pip` or spelled correctly.")
]
for i, (code, issue, fix) in enumerate(bugs):
    examples.append({
        "instruction": f"A student wrote the following code but it has a bug or anti-pattern. What is wrong and how do they fix it?\n```python\n{code}\n```",
        "output": f"The issue here is: {issue}\n\nTo fix it, the student should: {fix}\n\nThis is a very common beginner mistake. It's important to understand how Python handles this under the hood to write clean, bug-free code.",
        "category": "debug-this"
    })

# 3. flag-bad-practice (20 examples)
practices = [
    ("Hardcoding API keys in source code", "Security risk. Keys can be easily leaked if the code is uploaded to a public repository.", "Use environment variables (`os.environ.get()`) or a `.env` file with `python-dotenv`."),
    ("Using global variables extensively", "Makes code hard to test, reason about, and debug because state can change from anywhere.", "Encapsulate state in classes or pass variables explicitly as function arguments."),
    ("Writing 1000-line monolithic functions", "Violates the Single Responsibility Principle. Hard to read, test, and maintain.", "Break down the logic into smaller, focused helper functions (usually under 50 lines each)."),
    ("Not using virtual environments", "Leads to 'dependency hell' where project A breaks because project B updated a shared global library.", "Always create a virtual environment (`python -m venv venv`) for every new project."),
    ("Ignoring PEP 8 naming conventions", "Makes the codebase inconsistent and harder for other Python developers to read.", "Use `snake_case` for variables/functions and `CamelCase` for classes. Run a linter like `flake8` or `ruff`."),
    ("Checking type with `type(x) == list`", "Fails to account for inheritance. If someone passes a subclass of list, this check fails.", "Use `isinstance(x, list)` which correctly handles subclasses."),
    ("Concatenating strings in a loop with `+=`", "Strings are immutable, so this creates a new string in memory every iteration, leading to O(n^2) time complexity.", "Append strings to a list and use `''.join(list)` at the end."),
    ("Catching exceptions without logging", "Silent failures mean the program continues in an undefined state, and bugs are invisible to developers.", "Use the `logging` module to record `logger.error('...', exc_info=True)` when handling exceptions."),
    ("Using `eval()` on user input", "Massive security vulnerability allowing arbitrary code execution (Remote Code Execution).", "Never use `eval()`. Use `ast.literal_eval()` for safe evaluation, or parse inputs manually."),
    ("Importing everything with `from module import *`", "Pollutes the global namespace and makes it impossible to know where a function came from.", "Import specific functions (`from module import func`) or the module itself (`import module`)."),
    ("Using mutable default arguments like `[]` or `{}`", "The default object is shared across all function calls, leading to state leakage between calls.", "Set the default to `None` and initialize the mutable object inside the function block."),
    ("Manually closing files instead of using context managers", "If an exception occurs before `file.close()`, the file remains open, causing memory leaks.", "Always use `with open(...) as f:` to guarantee safe closure."),
    ("Returning varying data types from the same function", "Makes the function's contract unpredictable, forcing callers to perform messy type checks.", "Always return a consistent type, or use a specific object/data class to represent complex results."),
    ("Leaving commented-out dead code in the repository", "Adds visual noise and confusion. Developers wonder if the code is needed or broken.", "Delete it. Version control (Git) remembers the history if you ever need it back."),
    ("Not documenting complex logic", "Future maintainers (including yourself in 6 months) won't understand the 'why' behind the code.", "Write clear docstrings explaining the purpose, arguments, and return values of complex functions."),
    ("Using a list when a set is needed for membership testing", "Searching a list is O(n), which is extremely slow for large collections.", "Use a `set`, which offers O(1) membership testing (`if item in my_set:`)."),
    ("Writing tests that rely on external APIs", "Tests become slow, flaky, and require an internet connection.", "Use mocking libraries (like `unittest.mock`) to simulate API responses during tests."),
    ("Using bare print statements for debugging in production", "Clutters the console, slows down execution, and cannot be easily turned off.", "Use the standard `logging` module, which allows setting log levels (DEBUG, INFO, WARNING)."),
    ("Deeply nested if-else statements (Arrow Anti-Pattern)", "Makes code unreadable and hard to follow logical branches.", "Return early (guard clauses) to handle edge cases first and keep the main logic flat."),
    ("Reinventing the wheel instead of using the standard library", "Wastes time and often introduces bugs that standard libraries have already solved (e.g., writing a custom sorting algorithm instead of `sorted()`).", "Familiarize yourself with standard modules like `itertools`, `collections`, and `math`.")
]

for i, (practice, issue, fix) in enumerate(practices):
    examples.append({
        "instruction": f"A student submitted a PR doing the following: '{practice}'. Why is this bad practice in Python?",
        "output": f"This is considered a bad practice because: {issue}\n\nInstead, the student should: {fix}\n\nBy following this best practice, the code will be more robust, secure, and maintainable.",
        "category": "flag-bad-practice"
    })

# 4. step-by-step (20 examples)
tasks = [
    ("reverse a string", "def reverse_string(s):\n    return s[::-1]"),
    ("check if a number is even", "def is_even(n):\n    return n % 2 == 0"),
    ("find the maximum in a list without max()", "def find_max(lst):\n    if not lst: return None\n    m = lst[0]\n    for num in lst:\n        if num > m:\n            m = num\n    return m"),
    ("read a file line by line", "def read_file(filepath):\n    with open(filepath, 'r') as f:\n        for line in f:\n            print(line.strip())"),
    ("create a dictionary from two lists", "def make_dict(keys, values):\n    return dict(zip(keys, values))"),
    ("remove duplicates from a list", "def remove_duplicates(lst):\n    return list(set(lst))"),
    ("count occurrences of items in a list", "from collections import Counter\ndef count_items(lst):\n    return dict(Counter(lst))"),
    ("write a decorator that measures execution time", "import time\ndef timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f'Took {time.time() - start}s')\n        return result\n    return wrapper"),
    ("flatten a nested list (1 level deep)", "def flatten(nested_list):\n    return [item for sublist in nested_list for item in sublist]"),
    ("check if a string is a palindrome", "def is_palindrome(s):\n    s = s.lower().replace(' ', '')\n    return s == s[::-1]"),
    ("generate the Fibonacci sequence up to n", "def fib(n):\n    a, b = 0, 1\n    result = []\n    while a <= n:\n        result.append(a)\n        a, b = b, a + b\n    return result"),
    ("sort a dictionary by its values", "def sort_dict(d):\n    return dict(sorted(d.items(), key=lambda item: item[1]))"),
    ("merge two dictionaries", "def merge_dicts(d1, d2):\n    return {**d1, **d2}"),
    ("find the intersection of two lists", "def list_intersection(l1, l2):\n    return list(set(l1) & set(l2))"),
    ("write to a JSON file", "import json\ndef write_json(data, filepath):\n    with open(filepath, 'w') as f:\n        json.dump(data, f, indent=4)"),
    ("handle a divide by zero error", "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 'Cannot divide by zero'"),
    ("parse a CSV file", "import csv\ndef parse_csv(filepath):\n    with open(filepath, newline='') as f:\n        reader = csv.DictReader(f)\n        return [row for row in reader]"),
    ("create a simple class", "class Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return f'{self.name} says woof!'"),
    ("make an HTTP GET request", "import requests\ndef fetch_data(url):\n    response = requests.get(url)\n    response.raise_for_status()\n    return response.json()"),
    ("use a list comprehension to filter odd numbers", "def get_evens(lst):\n    return [x for x in lst if x % 2 == 0]")
]

for i, (task, code) in enumerate(tasks):
    examples.append({
        "instruction": f"Walk me through how to {task} step-by-step in Python.",
        "output": f"Absolutely! \n```python\n{code}\n```\n\nThis is a standard and highly efficient way to accomplish the task in Python. Let me know if you need any clarification on how this code executes!",
        "category": "step-by-step"
    })

os.makedirs('data/custom_examples', exist_ok=True)
with open('data/custom_examples/education_examples.jsonl', 'w') as f:
    for ex in examples:
        f.write(json.dumps(ex) + '\n')

print(f"Successfully generated {len(examples)} examples.")
