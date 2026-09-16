# Common Python Errors

## SyntaxError
Occurs when the parser encounters a syntax error.
- **Example:** Missing a colon at the end of an if statement.
- **Fix:** Double-check your indentation, parentheses, quotes, and colons.

## IndentationError
A subclass of SyntaxError, this happens when there is an incorrect indentation.
- **Example:** Mixing tabs and spaces, or forgetting to indent the body of a loop.
- **Fix:** Use standard 4 spaces for indentation. Most modern IDEs can auto-format this.

## TypeError
Raised when an operation or function is applied to an object of inappropriate type.
- **Example:** Adding a string to an integer: `"The number is " + 5`.
- **Fix:** Convert types explicitly, e.g., `"The number is " + str(5)`.

## NameError
Raised when a local or global name is not found.
- **Example:** Using a variable before it is defined, or a typo in a variable name.
- **Fix:** Ensure the variable is initialized and spelled correctly.

## IndexError
Raised when a sequence subscript is out of range.
- **Example:** Trying to access the 5th element of a list that only has 3 items: `my_list[4]`.
- **Fix:** Ensure you are accessing within the valid bounds of the sequence (0 to len-1).

## KeyError
Raised when a dictionary key is not found in the set of existing keys.
- **Example:** `my_dict['age']` when 'age' is not a key in the dictionary.
- **Fix:** Check if the key exists using `if key in dict:` or use `dict.get(key)`.

## AttributeError
Raised when an attribute reference or assignment fails.
- **Example:** Calling a method that doesn't exist on an object, e.g., `'hello'.append('!')`.
- **Fix:** Verify the object's type and its available methods.

## ValueError
Raised when an operation or function receives an argument that has the right type but an inappropriate value.
- **Example:** `int('hello')`
- **Fix:** Ensure the value is appropriate for the operation or function.

## ZeroDivisionError
Raised when the second argument of a division or modulo operation is zero.
- **Example:** `10 / 0`
- **Fix:** Check if the denominator is zero before performing division.
