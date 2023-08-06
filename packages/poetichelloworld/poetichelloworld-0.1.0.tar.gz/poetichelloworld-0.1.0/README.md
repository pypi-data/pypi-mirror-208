how_long
========

Simple Decorator to measure a function execution time.

Example
--------

```python
from poetichelloworld import timer

@timer
def some_function():
    return [x for x in range(10_000_000)]
```