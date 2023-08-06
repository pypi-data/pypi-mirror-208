# WorkToy

Collection of General Utilities

## The None-aware 'maybe'

In a programming language which shall rename nameless as well as typeless,
the following syntax is available:

    const func = (arg = null) => {
        let val1 = arg || 1.0;
        let val2 = arg ?? 1.0;
        return [val1, val2]; }

In the above code, the default argument is set to null (in this context
null is treated the same as None in Python). The `??` operator is the
null-coalescence operator, which is nearly the same as the `or` operator.  
Consider the return value obtained from calling `func()`:

    func()
    >>> (2)  [1, 1]

This makes sense, but what happens when we call the function on a falsy
value other than null, such as 0:

    func(0)
    >>> (3)  [1, 0]

The first value in the return value comes from using the pipes (the
logical or operator), is not aware of the difference between null and
other falsy values. The null-coalescence operator is able to tell the
difference. The WorkToy module brings this to python along with several
derived utility functions:

### `maybe`

In the below python code, we implement the same function using the maybe
function from WorkToy:

    def func(arg: Any = None) -> Any:
        """Function using the maybe from the WorkToy module"""
        val1 = arg or 1.0
        val2 = maybe(arg, 1.0)
        return [val1, val2]

The implementation of maybe simply follows a common pattern:

    def maybe(*args) -> Any:
        """Implementation of maybe returns the first argument given that 
        is different from None. If no such argument is found None is 
        returned."""
        for arg in args:
            if arg is not None: 
                return arg
        return None

Unlike the `??` operator, the `maybe` operator handles an arbitrary
number of arguments.

### `maybeType`

The first of the derived functions finds the first argument of a
particular type:

    def maybeType(type_: type, *args) -> type_:
        """Returns the first argument of given type"""

### `maybeTypes`

Adding an 's' returns every argument of given type. Further, it supports
keyword arguments `pad: int` and `padChar: Any`. If `pad` is given it
defines the length of the returned list padded with `padChar` or `None`
by default. Setting `pad` will either pad or crop as necessary.

### `searchKeys`

A common way to handle optional keyword arguments is something like:

    def func(*args, **kwargs) -> Any:
        """Common function accepting arbitrary positional and keyword 
        arguments."""
        val = kwargs.get('key', defaultValue)
        ...

In the above code, the `get` function is used to look for a given key in
the collection of keyword arguments along with a (optional) default value.
Instead, `searchKeys` allows for multiple keys in order of priority:

    def func(*args, **kwargs) -> Any:
        """Common function accepting arbitrary positional and keyword 
        arguments."""
        dV = defaultValue
        val = searchKeys('k1', 'k2', 'k3', **kwargs)
        ...

In addition, WorkToy provides the following syntactic pork-scratchings
for the keto-aware programmer:

    def func(*args, **kwargs) -> Any:
        """Common function accepting arbitrary positional and keyword 
        arguments."""
        dV = defaultValue
        val = searchKeys('k1', 'k2', 'k3') @ int >> (kwargs, dV)
        ...

The matrix multiplication operator `@` sets a type requirement and the
right-shift operator `>>` invokes the search. The default value is then
given as the second positional argument in the tuple. Please note that
absense of `**`. This causes `kwargs` to be treated as a dictionary
entirely contained at the first positional argument. If invoked without a
default value, the parentheses may be omitted.

### `CallMeMaybe`

This abstract baseclass registers any callable object as an instance.
This makes it stronger than the built-in `callable` and even the
`Callable` from the `typing` package. If a custom class implements the
`__call__` method, instances of this class may still not be recognized as
callable by the mentioned methods.

    class FilteredClass:
        """A class requiring a callable filter before invoking some other 
        function"""

        def __init__(self, *args, **kwargs) -> None:
            filterKwarg = searchKeys('filter') @ CallMeMaybe >> kwargs
            filterArg = maybeType(CallMeMaybe, *args)
            filterDefault = lambda *arg, **kwargs: (arg, kwargs)
            self._filter = maybe(filterKwarg, filterArg, filterDefault)
            self._func = someFunction
        
        def __call__(self, *args, **kwargs) -> Any:
            """Invokes some underlying function subject to the filter"""
            return self._func(self._filter(*args, **kwargs))

Additionally, decorate functions with `CallMeMaybe` to explicitly flag
functions as being instances of `CallMeMaybe`. As expected, instances of
subclasses of `CallMeMaybe` are regarded as instances.

## String Tools

WorkToy also brings a number of convenient string related functions:

### `stringList`

Consider the following code:

`numbers = ['one', 'two', 'three', 'four']`
The above involve repeated use of `'`. On the Danish keyboard layout, the
`'` key is located as indicated `jklæø'`, meaning that the right pinky
finger must leap over two other keys. Instead, use `stringList`:

    numbers = stringList('one, two, three, four', )
    >>> ['one', 'two', 'three', 'four']

### `monoSpace`

Consider the following code:

    msg = """Hello there! I am writing a long string right here in python 
    that stretches in length beyond the allowable line length. Thankfully,
    we have the triple quotation mark syntax for indication of longer 
    strings."""

The above code takes things literally meaning that new lines are inserted.
Thus, in between 'python' at the end of the first line and 'that' at the
beginning of the second line, a `'\n'` has been inserted. Instead, use
`monoSpace`:

    msgLine = monoSpace(msg)  # msg as defined above

Now `msgLine` contains now new lines and no repeated spaces. To
explicitly set a line break in the string, insert `'<br>'` in the text.
Set a different string to denote a line break, give that string as the
second argument.

    rawLines = """This is the first line. <br>   Here is the second line. 
    Don't worry about the extra spaces surrounding the tag, they are 
    removed. """
    
    twoLines = monoSpace(rawLines)
