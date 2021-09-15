.. See LICENSE.incore for details

.. _coding_style:

=============
Coding Style
=============

To maintain our source code clean and consistent, we use
`Google-Python <https://github.com/google/styleguide/blob/gh-pages/pyguide.md>`__
formatting along with a few additional naming conventions and rules. The
formatting tool can be installed by following the
`Google-yapf <https://github.com/google/styleguide/blob/gh-pages/pyguide.md>`__
guide. One can use the ``--style google`` flag in yapf to use the
Google-Python formatting.

Important Rules
~~~~~~~~~~~~~~~

-  Maximum line length is **80** characters. Exceptions are: Imports,
   URL's, Paths and docstrings that cant be split into separate lines.
-  Variables **SHOULD** be named in ``snake_case`` and not in
   ``CamelCasing``.
-  Avoid global variables.
-  Use parentheses ``()`` minimally.
-  Python's implicit line concatenation allow extending of expressions
   in ``(), [], {}``. These expressions can be split over multiple line
   without using backslashes.

   .. code:: python

       # Implicit Line Concatenation
       def function(name, age, height=100, country='IND', qualification='Some Degree',
                    Job='Unemployed', hobbies='swimming'):
                   pass

        list_of_fruits = [
            'apple', 'mango',
            'kivy',
            'peach'
        ]

-  When a literal string won't fit on a single line, use parentheses for
   implicit line joining.

   .. code:: python

       x = ('This is a very very very long long '
            'long long long long long long string')

-  Use Python3's `f-strings <https://www.python.org/dev/peps/pep-0498/>`__ wherever
   possible and avoid ``.format`` and string concatenations.

    .. code:: python

        first_name = 'John'
        last_name = 'Doe'

        # Avoid This!
        print('Full Name: {0} {1}'.format(first\_name, last\_name))
        print('Full Name: ' + first\_name + ' ' + last\_name)

        # Instead Use F-strings
        print(f'Full Name: {first\_name} {last\_name}')

-  Prefer small and focussed functions & classes. Use lambda expressions for one-line functions instead of writing new functions.

.. warning::
    Do not use functions from ``__future__`` module. Import modules/libraries that are available in Python 3.6.

Indentation
~~~~~~~~~~~
- Never use tabs and spaces together.
- Use **Tabs for indentation**.
- And each tab corresponds to 4 spaces.
- In the case of line continuation, align the new line's wrapping vertically.

Whitespaces
~~~~~~~~~~~

-  Follow standard typographic rules for the use of spaces around
   punctuation.
-  No whitespace inside parentheses, brackets or braces.
-  No whitespace before a comma, semicolon, or colon.
-  Should use whitespace after a comma, semicolon, or colon, except at
   the end of the line.
-  No trailing whitespace.
-  Surround binary operators with a single space on either side for
   assignment ``=``, comparisons
   (``==, <, >, !=, <>, <=, >=, in, not in, is, is not``), and Booleans
   (``and, or, not``).

   .. code:: python

       # Not this!
       ans = [ 'apple', { 'a' : 5 }, ( '3' , '4') ]
       #      ^          ^   ^ ^ ^    ^   ^  ^   ^
       # Instead
       ans = ['apple', {'a': 5}, ('3', '4')]

Blank Lines
~~~~~~~~~~~

-  Two blank lines between top-level definitions, for both functions and
   class definitions.
-  One blank line between method definitions and between the class line
   and the first method.
-  No blank line following a ``def`` line. Use single blank lines as you
   judge appropriate within functions or methods.

Docstrings & Comments
~~~~~~~~~~~~~~~~~~~~~

- A docstring is a string that is the first statement in a package, module, class or function.
- Always use the three double-quote ``""" docstring """`` format for docstrings (`PEP 257 <https://www.google.com/url?sa=D&q=http://www.python.org/dev/peps/pep-0257/>`__).
- A docstring should be organized as a summary line (a line not exceeding 80 characters) terminated by punctuation.
- When writing more (encouraged), this must be followed by a blank line, followed by the rest of the docstring starting at the same cursor position as the first quote of the first line.
- A function/class should have a docstring, unless it meets all of the following criteria :

    - not externally visible
    - very short
    - obvious



Naming Conventions
~~~~~~~~~~~~~~~~~~

-  Follow ``snake_casing`` strictly.
-  Avoid single-character naming to the possible extent.
-  As a rule of thumb, a name's descriptiveness should be proportional
   to its scope of visibility.
-  Avoid overriding python's internal keywords.
-  File names should not contain ``-``.

Functions & Classes
~~~~~~~~~~~~~~~~~~~

- Use lambda expressions for simple functions.
- List arguments with default values after arguments without default values in function headers.

.. code-block:: python

    # Wrong!
    def function(a=None, b):
        pass
    # Proper way
    def function(b, a=None):
        pass

- Try to specify default values for arguments as far as possible.
- Specify ``__init__`` function (constructor) for all class definitions and initialize the variables that will be used with default values.
- Usage of type annotations if highly recommended. Refer `PEP484 <https://www.python.org/dev/peps/pep-0484/>`_

.. code-block:: python

    def add_2_integers(a: int, b: int = 5) -> int:
        # adds a and b if both are specified, else returns a + 5
        return(a + b)

