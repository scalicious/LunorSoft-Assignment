# Python Built-in Functions

## print()
Prints the specified message to the screen or other standard output device.
Example:
```python
print("Hello, world!")
```

## len()
Returns the number of items in an object. When the object is a string, the len() function returns the number of characters in the string.
Example:
```python
my_list = [1, 2, 3]
print(len(my_list)) # Outputs: 3
```

## type()
Returns the type of the specified object.
Example:
```python
x = 5
print(type(x)) # Outputs: <class 'int'>
```

## range()
Returns a sequence of numbers, starting from 0 by default, and increments by 1 (by default), and stops before a specified number.
Example:
```python
for i in range(5):
    print(i) # Outputs 0, 1, 2, 3, 4
```

## enumerate()
Takes a collection (e.g. a tuple) and returns it as an enumerate object. This object can then be used directly for loops or converted into a list of tuples using the list() function.
Example:
```python
fruits = ['apple', 'banana', 'cherry']
for index, fruit in enumerate(fruits):
    print(index, fruit)
```

## map()
Executes a specified function for each item in an iterable. The item is sent to the function as a parameter.
Example:
```python
def myfunc(n):
  return len(n)
x = map(myfunc, ('apple', 'banana', 'cherry'))
```

## filter()
Returns an iterator where the items are filtered through a function to test if the item is accepted or not.
Example:
```python
ages = [5, 12, 17, 18, 24, 32]
def myFunc(x):
  if x < 18:
    return False
  else:
    return True
adults = filter(myFunc, ages)
```
