# Python & FastAPI Interview Preparation Guide

## 🎯 The Complete Interview Resource for Product-Based Companies

**Date:** April 2026  
**Coverage:** Beginner to Advanced  
**Focus:** Theory + Practical + Output-Based Questions

---

# Table of Contents

## Part 1: Python Fundamentals
1. [Basic Syntax & Data Types](#1-basic-syntax--data-types)
2. [Variables & Memory Management](#2-variables--memory-management)
3. [Operators & Expressions](#3-operators--expressions)
4. [Control Flow](#4-control-flow)

## Part 2: Functions
5. [Function Basics](#5-function-basics)
6. [Lambda Functions](#6-lambda-functions)
7. [Recursion](#7-recursion)
8. [Closures & Decorators](#8-closures--decorators)

## Part 3: Data Structures
9. [Built-in Data Structures](#9-built-in-data-structures)
10. [Comprehensions](#10-comprehensions)
11. [Advanced Data Structures](#11-advanced-data-structures)
12. [Collections Module](#12-collections-module)

## Part 4: Object-Oriented Programming
13. [Classes & Objects](#13-classes--objects)
14. [Inheritance & MRO](#14-inheritance--mro)
15. [Polymorphism](#15-polymorphism)
16. [Encapsulation & Abstraction](#16-encapsulation--abstraction)
17. [Magic Methods](#17-magic-methods)
18. [Dataclasses](#18-dataclasses)

## Part 5: Advanced Python
19. [Iterators & Generators](#19-iterators--generators)
20. [Context Managers](#20-context-managers)
21. [Async Programming](#21-async-programming)
22. [Threading & Multiprocessing](#22-threading--multiprocessing)
23. [GIL Deep Dive](#23-gil-deep-dive)
24. [Memory Optimization](#24-memory-optimization)

## Part 6: Core Concepts
25. [Exception Handling](#25-exception-handling)
26. [Modules & Packages](#26-modules--packages)
27. [File Handling](#27-file-handling)

## Part 7: Popular Libraries
28. [NumPy](#28-numpy)
29. [Pandas](#29-pandas)
30. [Requests](#30-requests)
31. [Datetime](#31-datetime)
32. [OS & Sys](#32-os--sys)
33. [Logging](#33-logging)
34. [Regex](#34-regex)
35. [SQLAlchemy Basics](#35-sqlalchemy-basics)
36. [Pydantic](#36-pydantic)

## Part 8: FastAPI
37. [FastAPI Fundamentals](#37-fastapi-fundamentals)
38. [Routing & Path Operations](#38-routing--path-operations)
39. [Request Handling](#39-request-handling)
40. [Pydantic Models](#40-pydantic-models)
41. [Dependency Injection](#41-dependency-injection)
42. [Middleware](#42-middleware)
43. [Background Tasks](#43-background-tasks)
44. [File Uploads](#44-file-uploads)
45. [WebSockets](#45-websockets)
46. [Authentication & Authorization](#46-authentication--authorization)
47. [Exception Handling in FastAPI](#47-exception-handling-in-fastapi)
48. [API Versioning](#48-api-versioning)

## Part 9: Database & Testing
49. [SQLAlchemy ORM](#49-sqlalchemy-orm)
50. [Alembic Migrations](#50-alembic-migrations)
51. [Testing with Pytest](#51-testing-with-pytest)
52. [FastAPI Testing](#52-fastapi-testing)

## Part 10: DevOps & Deployment
53. [Docker](#53-docker)
54. [Environment Management](#54-environment-management)
55. [Deployment Strategies](#55-deployment-strategies)

## Part 11: Output-Based Questions
56. [100+ Python Output Questions](#56-python-output-questions)

## Part 12: Scenario-Based Questions
57. [Real-World Backend Problems](#57-real-world-backend-problems)
58. [API Design Questions](#58-api-design-questions)

## Part 13: Coding Questions
59. [Interview Coding Problems](#59-interview-coding-problems)

## Part 14: System Design
60. [Backend System Design](#60-backend-system-design)

---

# Part 1: Python Fundamentals

## 1. Basic Syntax & Data Types

### Q1: What are Python's built-in data types?

**Answer:**
```python
# Numeric Types
integer = 42                    # int
floating = 3.14                 # float
complex_num = 3 + 4j            # complex

# Sequence Types
string = "Hello"                # str
list_data = [1, 2, 3]           # list
tuple_data = (1, 2, 3)          # tuple
range_data = range(5)           # range

# Mapping Type
dictionary = {"key": "value"}   # dict

# Set Types
set_data = {1, 2, 3}            # set
frozen = frozenset([1, 2, 3])   # frozenset

# Boolean Type
boolean = True                  # bool

# Binary Types
bytes_data = b"hello"           # bytes
bytearray_data = bytearray(5)   # bytearray
memoryview_data = memoryview(bytes(5))  # memoryview

# None Type
none_value = None               # NoneType
```

### Q2: What is type hinting and why use it?

**Answer:**
```python
from typing import List, Dict, Optional, Union, Callable

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Collection types
def process_items(items: List[int]) -> Dict[str, int]:
    return {"sum": sum(items), "count": len(items)}

# Optional types
def find_user(user_id: int) -> Optional[str]:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)  # Returns None if not found

# Union types
def parse_value(value: Union[int, str]) -> int:
    return int(value)

# Callable types
def apply_function(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)
```

**Benefits:**
- Better IDE autocomplete
- Static type checking with mypy
- Self-documenting code
- Catches errors early

### Q3: Explain mutable vs immutable types

**Answer:**

**Immutable Types:** Cannot be changed after creation
```python
# int, float, str, tuple, frozenset, bool
x = 10
print(id(x))  # 140234567890
x = 20
print(id(x))  # 140234567920 (New object!)

# Strings are immutable
s = "hello"
# s[0] = 'H'  # TypeError: 'str' object does not support item assignment
s = "Hello"    # Creates new string object
```

**Mutable Types:** Can be changed in-place
```python
# list, dict, set
numbers = [1, 2, 3]
print(id(numbers))  # 140234567890
numbers.append(4)
print(id(numbers))  # 140234567890 (Same object!)

# Dictionary is mutable
data = {"name": "Alice"}
data["age"] = 25  # Modifies in-place
```

**Important Implication:**
```python
# Mutable default argument pitfall
def add_item(item, items=[]):  # BUG!
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - Unexpected!

# Correct approach
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Q4: What is the difference between `is` and `==`?

**Answer:**
```python
# == compares VALUES
# is compares IDENTITY (memory address)

a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True (same values)
print(a is b)  # False (different objects)
print(a is c)  # True (same object)

# Small integer caching (-5 to 256)
x = 256
y = 256
print(x is y)  # True (cached)

x = 257
y = 257
print(x is y)  # False (not cached, implementation dependent)

# String interning
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True (interned)

s1 = "hello world"
s2 = "hello world"
print(s1 is s2)  # False (not interned, has space)
```

### Q5: Explain truthiness and falsiness in Python

**Answer:**
```python
# Falsy values
print(bool(False))      # False
print(bool(None))       # False
print(bool(0))          # False
print(bool(0.0))        # False
print(bool(""))         # False
print(bool([]))         # False
print(bool({}))         # False
print(bool(()))         # False
print(bool(set()))      # False

# Everything else is truthy
print(bool(1))          # True
print(bool(-1))         # True
print(bool("0"))        # True (non-empty string)
print(bool([0]))        # True (non-empty list)
print(bool(" "))        # True (whitespace counts)

# Practical usage
data = []
if data:
    print("Has data")
else:
    print("No data")  # This executes
```

---

## 2. Variables & Memory Management

### Q6: How does Python manage memory?

**Answer:**

**Memory Management Components:**
1. **Private heap space** - All objects stored here
2. **Reference counting** - Tracks object references
3. **Garbage collection** - Removes unreferenced objects
4. **Memory pools** - Optimizes small object allocation

```python
import sys

# Reference counting
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (a + temporary reference in getrefcount)

b = a
print(sys.getrefcount(a))  # 3

del b
print(sys.getrefcount(a))  # 2

# Object identity
x = 1000
y = 1000
print(id(x))  # Different
print(id(y))  # Different (for large numbers)

# Small integers are cached
x = 5
y = 5
print(id(x) == id(y))  # True (same object)
```

### Q7: What is garbage collection in Python?

**Answer:**
```python
import gc

# Garbage collector handles circular references
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

# Create circular reference
a = Node(1)
b = Node(2)
a.next = b
b.next = a  # Circular reference

# Even after deleting, reference count isn't zero
del a, b
# Garbage collector will clean this up

# Manual garbage collection
gc.collect()  # Force collection
print(gc.get_count())  # Get collection counts

# Disable/enable GC
gc.disable()
# ...operations...
gc.enable()

# Check if object is tracked
x = []
print(gc.is_tracked(x))  # True
y = 5
print(gc.is_tracked(y))  # False (small int)
```

### Q8: Explain variable scopes (LEGB rule)

**Answer:**
```python
x = "global"  # Global scope

def outer():
    x = "enclosing"  # Enclosing scope
    
    def inner():
        x = "local"  # Local scope
        print("Inner:", x)
        
        # Built-in scope
        print("Length:", len([1, 2, 3]))
    
    inner()
    print("Outer:", x)

outer()
print("Global:", x)

# Output:
# Inner: local
# Enclosing: enclosing
# Global: global

# LEGB: Local → Enclosing → Global → Built-in
```

### Q9: What are `global` and `nonlocal` keywords?

**Answer:**
```python
# global keyword
count = 0

def increment():
    global count  # Modify global variable
    count += 1

increment()
increment()
print(count)  # 2

# nonlocal keyword
def outer():
    count = 0
    
    def inner():
        nonlocal count  # Modify enclosing variable
        count += 1
    
    inner()
    inner()
    print(count)  # 2

outer()

# Without nonlocal (creates new local variable)
def outer2():
    count = 0
    
    def inner():
        count = 1  # Creates new local variable!
        print("Inner:", count)
    
    inner()
    print("Outer:", count)  # Still 0

outer2()
```

### Q10: Explain shallow copy vs deep copy

**Answer:**
```python
import copy

# Original list with nested list
original = [[1, 2, 3], [4, 5, 6]]

# Shallow copy - copies outer list, references inner lists
shallow = copy.copy(original)
# or
shallow = original.copy()
# or
shallow = original[:]

shallow[0][0] = 999
print(original)  # [[999, 2, 3], [4, 5, 6]] - AFFECTED!
print(shallow)   # [[999, 2, 3], [4, 5, 6]]

# Deep copy - recursively copies all nested objects
original = [[1, 2, 3], [4, 5, 6]]
deep = copy.deepcopy(original)

deep[0][0] = 999
print(original)  # [[1, 2, 3], [4, 5, 6]] - NOT affected
print(deep)      # [[999, 2, 3], [4, 5, 6]]

# Dictionary example
original_dict = {"a": [1, 2, 3], "b": [4, 5, 6]}
shallow_dict = original_dict.copy()
shallow_dict["a"][0] = 999
print(original_dict)  # {"a": [999, 2, 3], ...} - AFFECTED!

deep_dict = copy.deepcopy(original_dict)
deep_dict["a"][0] = 100
print(original_dict)  # {"a": [999, 2, 3], ...} - NOT affected
```

---

## 3. Operators & Expressions

### Q11: What are Python's operator types?

**Answer:**
```python
# Arithmetic Operators
print(10 + 3)   # 13 (Addition)
print(10 - 3)   # 7  (Subtraction)
print(10 * 3)   # 30 (Multiplication)
print(10 / 3)   # 3.333... (True division)
print(10 // 3)  # 3 (Floor division)
print(10 % 3)   # 1 (Modulus)
print(10 ** 3)  # 1000 (Exponentiation)

# Comparison Operators
print(5 == 5)   # True
print(5 != 3)   # True
print(5 > 3)    # True
print(5 < 3)    # False
print(5 >= 5)   # True
print(5 <= 3)   # False

# Logical Operators
print(True and False)  # False
print(True or False)   # True
print(not True)        # False

# Bitwise Operators
print(5 & 3)    # 1  (AND)
print(5 | 3)    # 7  (OR)
print(5 ^ 3)    # 6  (XOR)
print(~5)       # -6 (NOT)
print(5 << 1)   # 10 (Left shift)
print(5 >> 1)   # 2  (Right shift)

# Assignment Operators
x = 10
x += 5   # x = x + 5
x -= 3   # x = x - 3
x *= 2   # x = x * 2
x /= 4   # x = x / 4

# Identity Operators
print([] is [])      # False
print([] is not [])  # True

# Membership Operators
print(3 in [1, 2, 3])      # True
print(3 not in [1, 2, 3])  # False
```

### Q12: Explain operator precedence

**Answer:**
```python
# Order (highest to lowest):
# 1. Parentheses ()
# 2. Exponentiation **
# 3. Unary +, -, ~
# 4. *, /, //, %
# 5. +, -
# 6. Bitwise shifts <<, >>
# 7. Bitwise AND &
# 8. Bitwise XOR ^
# 9. Bitwise OR |
# 10. Comparisons ==, !=, <, >, <=, >=, is, in
# 11. not
# 12. and
# 13. or

# Examples
print(2 + 3 * 4)        # 14 (not 20)
print((2 + 3) * 4)      # 20
print(2 ** 3 ** 2)      # 512 (not 64, right associative)
print((2 ** 3) ** 2)    # 64
print(5 == 5 and 3 > 2) # True
print(5 == 5 or 3 < 2)  # True
```

### Q13: What is the walrus operator (`:=`)?

**Answer:**
```python
# Assignment expression (Python 3.8+)
# Assigns AND returns value in one expression

# Without walrus
data = [1, 2, 3, 4, 5]
n = len(data)
if n > 3:
    print(f"List has {n} items")

# With walrus
if (n := len(data)) > 3:
    print(f"List has {n} items")

# Useful in while loops
# Without walrus
while True:
    line = input("Enter text: ")
    if line == "quit":
        break
    print(f"You entered: {line}")

# With walrus
while (line := input("Enter text: ")) != "quit":
    print(f"You entered: {line}")

# In list comprehensions
data = [1, 2, 3, 4, 5]
# Compute expensive operation once
results = [y for x in data if (y := x * 2) > 4]
print(results)  # [6, 8, 10]
```

---

## 4. Control Flow

### Q14: Explain if-elif-else with examples

**Answer:**
```python
# Basic if-elif-else
score = 85

if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
elif score >= 70:
    grade = 'C'
else:
    grade = 'F'

print(grade)  # B

# Ternary operator
is_even = True if 10 % 2 == 0 else False
print(is_even)  # True

# Multiple conditions
age = 25
has_license = True

if age >= 18 and has_license:
    print("Can drive")
elif age >= 18:
    print("Need license")
else:
    print("Too young")

# Using in operator
fruit = "apple"
if fruit in ["apple", "banana", "orange"]:
    print("Valid fruit")
```

### Q15: What are the different types of loops?

**Answer:**
```python
# for loop
for i in range(5):
    print(i, end=" ")  # 0 1 2 3 4

# Iterate over collection
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# enumerate - get index and value
for idx, fruit in enumerate(fruits):
    print(f"{idx}: {fruit}")

# zip - iterate multiple iterables
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# while loop
count = 0
while count < 5:
    print(count)
    count += 1

# break statement
for i in range(10):
    if i == 5:
        break
    print(i)  # 0 1 2 3 4

# continue statement
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0 1 3 4

# else clause (executes if loop completes normally)
for i in range(5):
    print(i)
else:
    print("Loop completed")  # This executes

# else with break (doesn't execute if break is hit)
for i in range(5):
    if i == 3:
        break
else:
    print("Not executed")
```

### Q16: Explain match-case statement (Python 3.10+)

**Answer:**
```python
# Basic match-case (structural pattern matching)
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:  # Multiple patterns
            return "Server Error"
        case _:  # Default case
            return "Unknown"

print(http_status(200))  # OK
print(http_status(404))  # Not Found

# Match with conditions (guards)
def categorize_number(num):
    match num:
        case n if n < 0:
            return "Negative"
        case 0:
            return "Zero"
        case n if n > 0 and n < 10:
            return "Small positive"
        case _:
            return "Large positive"

# Match with data structures
def process_command(command):
    match command:
        case ["quit"]:
            return "Quitting"
        case ["load", filename]:
            return f"Loading {filename}"
        case ["save", filename, format]:
            return f"Saving {filename} as {format}"
        case _:
            return "Unknown command"

print(process_command(["load", "data.txt"]))
# Output: Loading data.txt

# Match with dictionaries
def process_user(user):
    match user:
        case {"name": name, "role": "admin"}:
            return f"Admin: {name}"
        case {"name": name, "role": "user"}:
            return f"User: {name}"
        case _:
            return "Unknown user"

# Match with classes
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def describe_point(point):
    match point:
        case Point(x=0, y=0):
            return "Origin"
        case Point(x=0, y=y):
            return f"On Y-axis at {y}"
        case Point(x=x, y=0):
            return f"On X-axis at {x}"
        case Point(x=x, y=y):
            return f"Point at ({x}, {y})"
```

---

# Part 2: Functions

## 5. Function Basics

### Q17: What are the different types of function arguments?

**Answer:**
```python
# 1. Positional arguments
def greet(name, age):
    print(f"{name} is {age} years old")

greet("Alice", 25)  # Must provide in order

# 2. Keyword arguments
greet(age=30, name="Bob")  # Order doesn't matter

# 3. Default arguments
def greet(name, age=18):
    print(f"{name} is {age} years old")

greet("Charlie")  # Uses default age=18

# 4. Variable positional arguments (*args)
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4, 5))  # 15

# 5. Variable keyword arguments (**kwargs)
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")

# 6. Combined usage (ORDER MATTERS!)
def complex_function(pos1, pos2, *args, kw1="default", **kwargs):
    print(f"Positional: {pos1}, {pos2}")
    print(f"Args: {args}")
    print(f"Keyword: {kw1}")
    print(f"Kwargs: {kwargs}")

complex_function(1, 2, 3, 4, 5, kw1="custom", extra="value")

# 7. Positional-only parameters (Python 3.8+)
def divide(a, b, /):  # / means a and b are positional-only
    return a / b

divide(10, 2)  # OK
# divide(a=10, b=2)  # TypeError!

# 8. Keyword-only parameters
def greet(*, name, age):  # * means name and age are keyword-only
    print(f"{name} is {age} years old")

greet(name="Alice", age=25)  # OK
# greet("Alice", 25)  # TypeError!

# 9. Combined positional-only and keyword-only
def func(pos_only, /, standard, *, kw_only):
    pass

func(1, 2, kw_only=3)          # OK
func(1, standard=2, kw_only=3) # OK
# func(pos_only=1, standard=2, kw_only=3)  # TypeError!
```

### Q18: Explain function annotations and docstrings

**Answer:**
```python
from typing import List, Dict

def calculate_average(numbers: List[float]) -> float:
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: A list of floating-point numbers
        
    Returns:
        The arithmetic mean of the numbers
        
    Raises:
        ValueError: If the list is empty
        
    Examples:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

# Access docstring
print(calculate_average.__doc__)

# Access annotations
print(calculate_average.__annotations__)
# {'numbers': typing.List[float], 'return': <class 'float'>}

# Multiple return types
def process_data(data: List[int]) -> tuple[int, int, float]:
    """Returns (min, max, average)"""
    return min(data), max(data), sum(data) / len(data)
```

### Q19: What are first-class functions?

**Answer:**
```python
# Functions are objects - can be assigned, passed, returned

# 1. Assign function to variable
def greet(name):
    return f"Hello, {name}"

say_hello = greet
print(say_hello("Alice"))  # Hello, Alice

# 2. Pass function as argument
def apply_operation(func, value):
    return func(value)

def square(x):
    return x ** 2

result = apply_operation(square, 5)
print(result)  # 25

# 3. Return function from function
def create_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

times_three = create_multiplier(3)
print(times_three(10))  # 30

# 4. Store functions in data structures
operations = {
    'add': lambda x, y: x + y,
    'subtract': lambda x, y: x - y,
    'multiply': lambda x, y: x * y,
}

print(operations['add'](5, 3))  # 8

# 5. Higher-order functions
numbers = [1, 2, 3, 4, 5]

# map
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# reduce
from functools import reduce
sum_all = reduce(lambda x, y: x + y, numbers)
print(sum_all)  # 15
```

---

## 6. Lambda Functions

### Q20: Explain lambda functions with examples

**Answer:**
```python
# Basic lambda
square = lambda x: x ** 2
print(square(5))  # 25

# Lambda with multiple arguments
add = lambda x, y: x + y
print(add(3, 4))  # 7

# Lambda in sorting
students = [
    {"name": "Alice", "grade": 85},
    {"name": "Bob", "grade": 92},
    {"name": "Charlie", "grade": 78}
]

# Sort by grade
sorted_students = sorted(students, key=lambda s: s["grade"])
print(sorted_students[0]["name"])  # Charlie

# Lambda with map
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)  # [2, 4, 6, 8, 10]

# Lambda with filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# Lambda in conditional
max_value = lambda x, y: x if x > y else y
print(max_value(10, 20))  # 20

# CAUTION: Lambda limitations
# 1. Single expression only (no statements)
# 2. No type annotations
# 3. Less readable for complex logic

# Bad use of lambda (use regular function instead)
complex_lambda = lambda x: x ** 2 if x > 0 else -x if x < 0 else 0

# Better as regular function
def complex_function(x):
    if x > 0:
        return x ** 2
    elif x < 0:
        return -x
    else:
        return 0
```

### Q21: Lambda vs Regular Function - When to use what?

**Answer:**
```python
# Use lambda for:
# 1. Short, simple operations
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))

# 2. Sorting keys
users = [("Alice", 25), ("Bob", 30), ("Charlie", 20)]
sorted_users = sorted(users, key=lambda x: x[1])

# 3. Callbacks
button.onclick = lambda: print("Clicked!")

# Use regular function for:
# 1. Multiple statements
def process_data(data):
    cleaned = [x.strip() for x in data]
    filtered = [x for x in cleaned if x]
    return sorted(filtered)

# 2. Complex logic
def calculate_tax(income):
    if income <= 50000:
        return income * 0.1
    elif income <= 100000:
        return 5000 + (income - 50000) * 0.2
    else:
        return 15000 + (income - 100000) * 0.3

# 3. Need docstrings and type hints
def find_user(user_id: int) -> Optional[dict]:
    """
    Find user by ID.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        User dictionary or None if not found
    """
    # Implementation
    pass
```

---

## 7. Recursion

### Q22: Explain recursion with examples

**Answer:**
```python
# Basic recursion - factorial
def factorial(n):
    # Base case
    if n == 0 or n == 1:
        return 1
    # Recursive case
    return n * factorial(n - 1)

print(factorial(5))  # 120

# Fibonacci sequence
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(6))  # 8

# Fibonacci with memoization (optimized)
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

# Sum of list
def sum_list(lst):
    if not lst:
        return 0
    return lst[0] + sum_list(lst[1:])

print(sum_list([1, 2, 3, 4, 5]))  # 15

# Binary search (recursive)
def binary_search(arr, target, low, high):
    if low > high:
        return -1
    
    mid = (low + high) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] > target:
        return binary_search(arr, target, low, mid - 1)
    else:
        return binary_search(arr, target, mid + 1, high)

arr = [1, 3, 5, 7, 9, 11, 13]
print(binary_search(arr, 7, 0, len(arr) - 1))  # 3

# Flatten nested list
def flatten(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

nested = [1, [2, 3, [4, 5]], 6, [7, [8, 9]]]
print(flatten(nested))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Q23: What is tail recursion and does Python optimize it?

**Answer:**
```python
# Tail recursion - last operation is recursive call
def factorial_tail(n, accumulator=1):
    if n == 0:
        return accumulator
    return factorial_tail(n - 1, n * accumulator)

print(factorial_tail(5))  # 120

# NOT tail recursive (multiplication after recursive call)
def factorial_not_tail(n):
    if n == 0:
        return 1
    return n * factorial_not_tail(n - 1)

# IMPORTANT: Python does NOT optimize tail recursion!
# Stack frames are still created
# Can hit maximum recursion depth

import sys
print(sys.getrecursionlimit())  # Usually 1000

# Can increase (but not recommended)
sys.setrecursionlimit(2000)

# Better: Use iteration for deep recursion
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# Or use built-in
import math
print(math.factorial(5))  # 120
```

---

## 8. Closures & Decorators

### Q24: What is a closure?

**Answer:**
```python
# Closure - inner function remembers outer function's variables

def outer(x):
    # x is in enclosing scope
    def inner(y):
        return x + y  # inner "closes over" x
    return inner

add_five = outer(5)
print(add_five(10))  # 15
print(add_five(20))  # 25

# Check closure
print(add_five.__closure__)  # (<cell at 0x...: int object at 0x...>,)
print(add_five.__closure__[0].cell_contents)  # 5

# Practical example - multiplier factory
def make_multiplier(factor):
    def multiply(number):
        return number * factor
    return multiply

times_two = make_multiplier(2)
times_three = make_multiplier(3)

print(times_two(10))    # 20
print(times_three(10))  # 30

# Counter using closure
def make_counter():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3

# Multiple functions sharing closure
def make_account(initial_balance):
    balance = initial_balance
    
    def deposit(amount):
        nonlocal balance
        balance += amount
        return balance
    
    def withdraw(amount):
        nonlocal balance
        if amount > balance:
            return "Insufficient funds"
        balance -= amount
        return balance
    
    def get_balance():
        return balance
    
    return deposit, withdraw, get_balance

deposit, withdraw, get_balance = make_account(100)
print(deposit(50))      # 150
print(withdraw(30))     # 120
print(get_balance())    # 120
```

### Q25: Explain decorators in detail

**Answer:**
```python
# Basic decorator
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function call
# Hello!
# After function call

# Decorator with arguments (using *args, **kwargs)
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(3, 5)  # Calls wrapper which calls original add

# Preserve function metadata with functools.wraps
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Preserves original function's metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone"""
    return f"Hello, {name}"

print(greet.__name__)  # greet (not wrapper)
print(greet.__doc__)   # Greet someone

# Decorator with parameters
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hi():
    print("Hi!")

say_hi()
# Output:
# Hi!
# Hi!
# Hi!

# Multiple decorators (applied bottom-up)
def bold(func):
    @wraps(func)
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper():
        return f"<i>{func()}</i>"
    return wrapper

@bold
@italic
def greet():
    return "Hello"

print(greet())  # <b><i>Hello</i></b>
# Equivalent to: bold(italic(greet))()
```

### Q26: Common decorator patterns

**Answer:**
```python
from functools import wraps
import time

# 1. Timer decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()  # slow_function took 1.0001 seconds

# 2. Memoization decorator
def memoize(func):
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # Fast!

# 3. Retry decorator
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_api_call():
    import random
    if random.random() < 0.7:
        raise Exception("API Error")
    return "Success"

# 4. Authentication decorator
def require_auth(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.get("authenticated"):
            raise PermissionError("Not authenticated")
        return func(user, *args, **kwargs)
    return wrapper

@require_auth
def get_sensitive_data(user):
    return "Secret data"

# 5. Logging decorator
def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(3, 5)
# Output:
# Calling add(3, 5)
# add returned 8

# 6. Class decorator
def singleton(cls):
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("Connecting to database...")

db1 = Database()  # Connecting to database...
db2 = Database()  # Uses existing instance
print(db1 is db===

### Q27: Class-based decorators

**Answer:**
```python
# Class as decorator
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # Call 1 of say_hello
say_hello()  # Call 2 of say_hello
print(say_hello.count)  # 2

# Class decorator with parameters
class Retry:
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed, retrying...")
        return wrapper

@Retry(max_attempts=5)
def flaky_function():
    import random
    if random.random() < 0.8:
        raise Exception("Random failure")
    return "Success"
```

---

# Part 3: Data Structures

## 9. Built-in Data Structures

### Q28: Explain List operations and methods

**Answer:**
```python
# Creating lists
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
nested = [[1, 2], [3, 4], [5, 6]]
empty = []

# Accessing elements
print(numbers[0])   # 1 (first)
print(numbers[-1])  # 5 (last)
print(numbers[1:4]) # [2, 3, 4] (slicing)
print(numbers[:3])  # [1, 2, 3] (first 3)
print(numbers[::2]) # [1, 3, 5] (every 2nd)

# Modifying lists
numbers.append(6)           # Add to end
numbers.insert(0, 0)        # Insert at index
numbers.extend([7, 8, 9])   # Add multiple
numbers.remove(5)           # Remove first occurrence
numbers.pop()               # Remove and return last
numbers.pop(0)              # Remove and return at index
del numbers[1]              # Delete at index
numbers.clear()             # Remove all

# Common methods
lst = [3, 1, 4, 1, 5, 9, 2, 6]
lst.sort()                  # Sort in-place
sorted_lst = sorted(lst)    # Return sorted copy
lst.reverse()               # Reverse in-place
reversed_lst = lst[::-1]    # Return reversed copy
count = lst.count(1)        # Count occurrences
index = lst.index(4)        # Find index of value

# List operations
combined = [1, 2] + [3, 4]        # Concatenation
repeated = [0] * 5                # Repetition
print(3 in [1, 2, 3])             # Membership: True
print(len([1, 2, 3]))             # Length: 3
print(min([1, 2, 3]))             # Min: 1
print(max([1, 2, 3]))             # Max: 3
print(sum([1, 2, 3]))             # Sum: 6

# Copying lists
original = [1, 2, 3]
shallow = original.copy()   # or original[:]
import copy
deep = copy.deepcopy(original)

# List unpacking
a, b, c = [1, 2, 3]
first, *rest = [1, 2, 3, 4, 5]
print(first)  # 1
print(rest)   # [2, 3, 4, 5]
```

### Q29: Explain Tuple operations

**Answer:**
```python
# Creating tuples
numbers = (1, 2, 3, 4, 5)
single = (1,)  # Note the comma!
without_parens = 1, 2, 3
empty = ()

# Tuples are immutable
# numbers[0] = 10  # TypeError!

# Accessing (same as lists)
print(numbers[0])    # 1
print(numbers[-1])   # 5
print(numbers[1:4])  # (2, 3, 4)

# Methods (only 2!)
count = numbers.count(3)  # Count occurrences
index = numbers.index(4)  # Find index

# Tuple unpacking
x, y, z = (1, 2, 3)
coordinates = (10, 20, 30)
x, y, z = coordinates

# Swap variables using tuples
a, b = 5, 10
a, b = b, a  # Swap!

# Named tuples
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
print(p[0], p[1])  # 10 20 (also works)

# Convert to dict
print(p._asdict())  # {'x': 10, 'y': 20}

# When to use tuples?
# 1. Return multiple values from function
def get_coordinates():
    return (10, 20)

# 2. Dictionary keys (immutable required)
locations = {
    (0, 0): "origin",
    (1, 0): "right",
    (0, 1): "up"
}

# 3. Immutable collection (prevents accidental modification)
config = ("localhost", 8000, "production")
```

### Q30: Explain Set operations

**Answer:**
```python
# Creating sets
numbers = {1, 2, 3, 4, 5}
from_list = set([1, 2, 2, 3, 3])  # {1, 2, 3} - duplicates removed
empty = set()  # Note: {} creates empty dict!

# Sets are unordered and unique
print({3, 1, 2})  # {1, 2, 3} (may vary)

# Adding/removing
numbers.add(6)
numbers.update([7, 8, 9])
numbers.remove(1)      # Raises KeyError if not found
numbers.discard(1)     # No error if not found
numbers.pop()          # Remove arbitrary element
numbers.clear()

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Union (all elements)
print(a | b)                # {1, 2, 3, 4, 5, 6}
print(a.union(b))           # Same

# Intersection (common elements)  
print(a & b)                # {3, 4}
print(a.intersection(b))    # Same

# Difference (in a but not in b)
print(a - b)                # {1, 2}
print(a.difference(b))      # Same

# Symmetric difference (in either, but not both)
print(a ^ b)                           # {1, 2, 5, 6}
print(a.symmetric_difference(b))       # Same

# Subset/Superset
print({1, 2} <= {1, 2, 3})  # True (subset)
print({1, 2} < {1, 2})      # False (proper subset)
print({1, 2, 3} >= {1, 2})  # True (superset)

# Frozenset (immutable set)
frozen = frozenset([1, 2, 3])
# frozen.add(4)  # AttributeError!

# Can be used as dict key
mapping = {frozen: "value"}
```

### Q31: Explain Dictionary operations

**Answer:**
```python
# Creating dictionaries
person = {"name": "Alice", "age": 25}
from_keys = dict.fromkeys(["a", "b", "c"], 0)  # {'a': 0, 'b': 0, 'c': 0}
from_pairs = dict([("a", 1), ("b", 2)])
empty = {}

# Accessing
print(person["name"])        # Alice
print(person.get("name"))    # Alice
print(person.get("city", "Unknown"))  # Unknown (default)

# Modifying
person["age"] = 26           # Update
person["city"] = "NYC"       # Add new key
del person["city"]           # Delete
age = person.pop("age")      # Remove and return
person.clear()               # Remove all

# Dictionary methods
person = {"name": "Alice", "age": 25, "city": "NYC"}

print(person.keys())         # dict_keys(['name', 'age', 'city'])
print(person.values())       # dict_values(['Alice', 25, 'NYC'])
print(person.items())        # dict_items([('name', 'Alice'), ...])

# Iterating
for key in person:
    print(key)

for key, value in person.items():
    print(f"{key}: {value}")

# Merging dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}

# Method 1: update (in-place)
dict1.update(dict2)

# Method 2: unpacking (Python 3.5+)
merged = {**dict1, **dict2}

# Method 3: union operator (Python 3.9+)
merged = dict1 | dict2

# setdefault - get or set default
count = {}
for char in "hello":
    count.setdefault(char, 0)
    count[char] += 1
print(count)  # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# Dictionary views (dynamic)
person = {"name": "Alice"}
keys_view = person.keys()
person["age"] = 25
print(keys_view)  # dict_keys(['name', 'age']) - updated!

# Nested dictionaries
users = {
    1: {"name": "Alice", "age": 25},
    2: {"name": "Bob", "age": 30}
}

print(users[1]["name"])  # Alice
```

---

## 10. Comprehensions

### Q32: Explain list comprehensions

**Answer:**
```python
# Basic list comprehension
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8]

# With if-else (different syntax!)
labels = ['even' if x % 2 == 0 else 'odd' for x in range(5)]
print(labels)  # ['even', 'odd', 'even', 'odd', 'even']

# Nested loops
pairs = [(x, y) for x in range(3) for y in range(3)]
print(pairs)  # [(0,0), (0,1), (0,2), (1,0), (1,1), ...]

# Flattening 2D list
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# With function calls
words = ["hello", "world", "python"]
uppercase = [w.upper() for w in words]
print(uppercase)  # ['HELLO', 'WORLD', 'PYTHON']

# Multiple conditions
nums = [x for x in range(20) if x % 2 == 0 if x % 3 == 0]
print(nums)  # [0, 6, 12, 18]

# Equivalent to:
nums = []
for x in range(20):
    if x % 2 == 0:
        if x % 3 == 0:
            nums.append(x)

# List comprehension vs map/filter
# List comprehension
result = [x**2 for x in range(10) if x % 2 == 0]

# Equivalent with map and filter
result = list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, range(10))))

# List comprehensions are generally more readable
```

### Q33: Explain dict and set comprehensions

**Answer:**
```python
# Dictionary comprehension
squares_dict = {x: x**2 for x in range(5)}
print(squares_dict)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Swap keys and values
original = {"a": 1, "b": 2, "c": 3}
swapped = {value: key for key, value in original.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}

# With condition
high_scores = {"Alice": 95, "Bob": 72, "Charlie": 88}
passed = {name: score for name, score in high_scores.items() if score >= 80}
print(passed)  # {'Alice': 95, 'Charlie': 88}

# From two lists
keys = ["name", "age", "city"]
values = ["Alice", 25, "NYC"]
person = {k: v for k, v in zip(keys, values)}
print(person)  # {'name': 'Alice', 'age': 25, 'city': 'NYC'}

# Set comprehension
squares_set = {x**2 for x in range(10)}
print(squares_set)  # {0, 1, 4, 9, 16, 25, 36, 49, 64, 81}

# Unique character lengths
words = ["hello", "world", "hi", "python"]
lengths = {len(w) for w in words}
print(lengths)  # {2, 5, 6}

# With condition
words = ["hello", "world", "hi", "python", "hey"]
long_word_lengths = {len(w) for w in words if len(w) > 3}
print(long_word_lengths)  # {5, 6}

# Generator expression (parentheses instead of brackets)
# Doesn't create list in memory
squares_gen = (x**2 for x in range(1000000))  # Memory efficient!
print(type(squares_gen))  # <class 'generator'>
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1
```

### Q34: Complex comprehension examples

**Answer:**
```python
# Nested list comprehension
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

# Transpose matrix
transposed = [[row[i] for row in matrix] for i in range(3)]
print(transposed)  # [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# Flatten with condition
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
evens = [num for row in matrix for num in row if num % 2 == 0]
print(evens)  # [2, 4, 6, 8]

# Cartesian product
colors = ["red", "green", "blue"]
sizes = ["S", "M", "L"]
products = [f"{color}-{size}" for color in colors for size in sizes]
print(products)  
# ['red-S', 'red-M', 'red-L', 'green-S', 'green-M', ...]

# Dictionary from list with enumeration
fruits = ["apple", "banana", "cherry"]
fruit_dict = {i: fruit for i, fruit in enumerate(fruits)}
print(fruit_dict)  # {0: 'apple', 1: 'banana', 2: 'cherry'}

# Conditional dictionary comprehension
numbers = [1, 2, 3, 4, 5]
labels = {n: ('even' if n % 2 == 0 else 'odd') for n in numbers}
print(labels)  # {1: 'odd', 2: 'even', 3: 'odd', ...}

# Nested dictionary comprehension
matrix = {i: {j: i*j for j in range(3)} for i in range(3)}
print(matrix)
# {0: {0: 0, 1: 0, 2: 0},
#  1: {0: 0, 1: 1, 2: 2},
#  2: {0: 0, 1: 2, 2: 4}}
```

---

## 11. Advanced Data Structures

### Q35: Explain Stack implementation

**Answer:**
```python
# Stack using list (LIFO - Last In First Out)
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Pop from empty stack")
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Peek from empty stack")
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# Usage
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)
print(stack.pop())   # 3
print(stack.peek())  # 2

# Simple stack with list
stack = []
stack.append(1)  # push
stack.append(2)
stack.append(3)
print(stack.pop())  # 3

# Stack application: balanced parentheses
def is_balanced(expression):
    stack = []
    matching = {'(': ')', '[': ']', '{': '}'}
    
    for char in expression:
        if char in matching:
            stack.append(char)
        elif char in matching.values():
            if not stack or matching[stack.pop()] != char:
                return False
    
    return len(stack) == 0

print(is_balanced("()[]{}"))     # True
print(is_balanced("([)]"))       # False
print(is_balanced("((()))"))     # True
```

### Q36: Explain Queue implementation

**Answer:**
```python
# Queue using collections.deque (FIFO - First In First Out)
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        raise IndexError("Dequeue from empty queue")
    
    def front(self):
        if not self.is_empty():
            return self.items[0]
        raise IndexError("Front from empty queue")
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# Usage
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
queue.enqueue(3)
print(queue.dequeue())  # 1
print(queue.front())    # 2

# Simple queue with deque
from collections import deque
queue = deque()
queue.append(1)     # enqueue
queue.append(2)
queue.append(3)
print(queue.popleft())  # 1 - dequeue

# Priority Queue using heapq
import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0
    
    def push(self, item, priority):
        # heapq is min-heap, so negate for max priority
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1
    
    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[2]
        raise IndexError("Pop from empty priority queue")
    
    def is_empty(self):
        return len(self.heap) == 0

# Usage
pq = PriorityQueue()
pq.push("task1", priority=3)
pq.push("task2", priority=1)  # Higher priority
pq.push("task3", priority=2)
print(pq.pop())  # task2 (priority 1)
print(pq.pop())  # task3 (priority 2)
```

### Q37: Explain Heap operations (heapq)

**Answer:**
```python
import heapq

# Create heap (min-heap by default)
numbers = [5, 7, 9, 1, 3]
heapq.heapify(numbers)  # In-place conversion to heap
print(numbers)  # [1, 3, 9, 7, 5]

# Push (add) element
heapq.heappush(numbers, 2)
print(numbers)  # [1, 3, 2, 7, 5, 9]

# Pop (remove and return smallest)
smallest = heapq.heappop(numbers)
print(smallest)  # 1
print(numbers)   # [2, 3, 9, 7, 5]

# Push and pop in one operation
result = heapq.heappushpop(numbers, 4)  # Push 4, pop smallest
print(result)   # 2
print(numbers)  # [3, 4, 9, 7, 5]

# Replace (pop then push - more efficient)
result = heapq.heapreplace(numbers, 1)  # Pop smallest, push 1
print(result)   # 3
print(numbers)  # [1, 4, 9, 7, 5]

# N smallest/largest
numbers = [5, 7, 9, 1, 3, 8, 2]
print(heapq.nsmallest(3, numbers))  # [1, 2, 3]
print(heapq.nlargest(3, numbers))   # [9, 8, 7]

# Max heap (negate values)
max_heap = []
for num in [5, 7, 9, 1, 3]:
    heapq.heappush(max_heap, -num)

largest = -heapq.heappop(max_heap)
print(largest)  # 9

# Heap with custom objects
tasks = [
    (3, "Low priority task"),
    (1, "High priority task"),
    (2, "Medium priority task")
]
heapq.heapify(tasks)
while tasks:
    priority, task = heapq.heappop(tasks)
    print(f"Priority {priority}: {task}")
# Output (in priority order):
# Priority 1: High priority task
# Priority 2: Medium priority task  
# Priority 3: Low priority task
```

---

## 12. Collections Module

### Q38: Explain Counter

**Answer:**
```python
from collections import Counter

# Create Counter
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counter = Counter(words)
print(counter)  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# From string
text = "hello world"
char_count = Counter(text)
print(char_count)  # Counter({'l': 3, 'o': 2, 'h': 1, ...})

# Most common elements
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]

# Accessing counts
print(counter['apple'])    # 3
print(counter['grape'])    # 0 (no KeyError!)

# Update counter
counter.update(['apple', 'grape', 'grape'])
print(counter)  # Counter({'apple': 4, 'grape': 2, ...})

# Subtract
counter.subtract(['apple', 'apple'])
print(counter)  # Counter({'apple': 2, ...})

# Arithmetic operations
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)

print(c1 + c2)  # Counter({'a': 4, 'b': 3})
print(c1 - c2)  # Counter({'a': 2}) - keeps only positive
print(c1 & c2)  # Counter({'a': 1, 'b': 1}) - intersection (min)
print(c1 | c2)  # Counter({'a': 3, 'b': 2}) - union (max)

# Convert to regular dict
regular_dict = dict(counter)

# Elements (returns iterator)
c = Counter(a=3, b=2)
print(list(c.elements()))  # ['a', 'a', 'a', 'b', 'b']

# Practical example: finding anagrams
def are_anagrams(str1, str2):
    return Counter(str1) == Counter(str2)

print(are_anagrams("listen", "silent"))  # True
print(are_anagrams("hello", "world"))    # False
```

### Q39: Explain defaultdict

**Answer:**
```python
from collections import defaultdict

# Regular dict - KeyError if key doesn't exist
regular_dict = {}
# regular_dict['key'] += 1  # KeyError!

# defaultdict - provides default value
dd = defaultdict(int)  # Default value is 0
dd['key'] += 1
print(dd['key'])  # 1

# With list as default
dd_list = defaultdict(list)
dd_list['fruits'].append('apple')
dd_list['fruits'].append('banana')
print(dd_list['fruits'])  # ['apple', 'banana']

# With set as default
dd_set = defaultdict(set)
dd_set['numbers'].add(1)
dd_set['numbers'].add(2)
dd_set['numbers'].add(1)  # Duplicate ignored
print(dd_set['numbers'])  # {1, 2}

# Custom default factory
def default_value():
    return "Unknown"

dd_custom = defaultdict(default_value)
print(dd_custom['missing'])  # "Unknown"

# Grouping with defaultdict
students = [
    ('Alice', 'Math'),
    ('Bob', 'Science'),
    ('Charlie', 'Math'),
    ('David', 'Science'),
    ('Eve', 'Math')
]

groups = defaultdict(list)
for name, subject in students:
    groups[subject].append(name)

print(groups)
# defaultdict(<class 'list'>, {
#     'Math': ['Alice', 'Charlie', 'Eve'],
#     'Science': ['Bob', 'David']
# })

# Word count example
text = "the quick brown fox jumps over the lazy dog"
word_count = defaultdict(int)
for word in text.split():
    word_count[word] += 1

print(dict(word_count))  # {'the': 2, 'quick': 1, ...}

# Nested defaultdict
nested = defaultdict(lambda: defaultdict(int))
nested['user1']['posts'] = 5
nested['user1']['likes'] = 10
print(nested)  # defaultdict(<..., {'user1': {'posts': 5, 'likes': 10}})
```

### Q40: Explain deque (double-ended queue)

**Answer:**
```python
from collections import deque

# Create deque
dq = deque([1, 2, 3])
print(dq)  # deque([1, 2, 3])

# Add to right (end)
dq.append(4)
print(dq)  # deque([1, 2, 3, 4])

# Add to left (beginning)
dq.appendleft(0)
print(dq)  # deque([0, 1, 2, 3, 4])

# Remove from right
print(dq.pop())  # 4
print(dq)        # deque([0, 1, 2, 3])

# Remove from left
print(dq.popleft())  # 0
print(dq)             # deque([1, 2, 3])

# Extend
dq.extend([4, 5, 6])
print(dq)  # deque([1, 2, 3, 4, 5, 6])

dq.extendleft([0, -1, -2])  # Note: adds in reverse order!
print(dq)  # deque([-2, -1, 0, 1, 2, 3, 4, 5, 6])

# Rotate
dq = deque([1, 2, 3, 4, 5])
dq.rotate(2)   # Rotate right
print(dq)      # deque([4, 5, 1, 2, 3])

dq.rotate(-2)  # Rotate left
print(dq)      # deque([1, 2, 3, 4, 5])

# Max length (bounded deque)
bounded = deque(maxlen=3)
bounded.append(1)
bounded.append(2)
bounded.append(3)
bounded.append(4)  # Removes oldest (1)
print(bounded)     # deque([2, 3, 4], maxlen=3)

# Access like list
dq = deque([1, 2, 3, 4, 5])
print(dq[0])   # 1
print(dq[-1])  # 5

# Count and remove
dq = deque([1, 2, 3, 2, 4, 2])
print(dq.count(2))  # 3
dq.remove(2)        # Removes first occurrence
print(dq)           # deque([1, 3, 2, 4, 2])

# Clear
dq.clear()
print(dq)  # deque([])

# Use cases:
# 1. Fast appends/pops from both ends (O(1))
# 2. Sliding window
# 3. Breadth-first search
# 4. Task queue
```

### Q41: Other collections: OrderedDict, ChainMap, namedtuple

**Answer:**
```python
from collections import OrderedDict, ChainMap, namedtuple

# OrderedDict (maintains insertion order)
# Note: Regular dict maintains order in Python 3.7+
# OrderedDict is still useful for:
# 1. Explicit intent
# 2. move_to_end() method
# 3. Equality comparison considers order

od = OrderedDict()
od['first'] = 1
od['second'] = 2
od['third'] = 3

# Move to end
od.move_to_end('first')
print(od)  # OrderedDict([('second', 2), ('third', 3), ('first', 1)])

# Move to beginning
od.move_to_end('third', last=False)
print(od)  # OrderedDict([('third', 3), ('second', 2), ('first', 1)])

# ChainMap - combines multiple dicts
defaults = {'color': 'red', 'size': 'M'}
user_settings = {'color': 'blue'}

settings = ChainMap(user_settings, defaults)
print(settings['color'])  # 'blue' (from user_settings)
print(settings['size'])   # 'M' (from defaults)

# Update only affects first dict
settings['price'] = 10
print(user_settings)  # {'color': 'blue', 'price': 10}
print(defaults)       # {'color': 'red', 'size': 'M'} - unchanged

# namedtuple - tuple with named fields
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
print(p[0], p[1])  # 10 20 (also works)

# Can unpack like tuple
x, y = p

# Immutable (like tuple)
# p.x = 30  # AttributeError!

# Create from iterable
p2 = Point._make([30, 40])

# Convert to dict
print(p._asdict())  # {'x': 10, 'y': 20}

# Replace (returns new instance)
p3 = p._replace(x=50)
print(p3)  # Point(x=50, y=20)

# With defaults (Python 3.7+)
Node = namedtuple('Node', ['value', 'left', 'right'], defaults=[None, None])
node = Node(5)  # left and right default to None
print(node)  # Node(value=5, left=None, right=None)
```

---

*Continuing in next part due to length...*

This is Part 1 of the comprehensive interview guide. Shall I continue creating the remaining sections?

