# ctdd

## tl:dr

C test-driven development framework implemented in Python.

## Info

The testing framework is Python's native unittest, with a few extra asserts ans stuff provided by John. The tester looks for a .c and .h pair with the same name as the .py test file. It builds them into a Python extension using Crelm (which in turn uses cffi) and runs the Python tests as if it were testing Python code. C callbacks are mocked in Python (demo to follow..), meaning that there is exactly zero C code involved in the testing.

## Example

There is a demo of a TDD'd `add3` function in \_\_main\_\_.py, \_\_main\_\_.c and \_\_main\_\_.h in the root of the repo, run with `python3 .`. The silly filenames are to suit the Python auto-run mechanism.

The files are reproduced here (possibly out of date) with original filenames:

__add3.py__

```
from ctdd import Tester

class Add3Tests(Tester):

    def test_sut_compiles(self):
        with self.assertDoesNotRaise():
            self.sut

    def test_takes_three_f(self):
        with self.assertDoesNotRaise():
            self.sut.add3(0, 0, 0)

    def test_return_zero_for_zeros(self):
        expected = 0

        actual = self.sut.add3(0, 0, 0)

        self.assertEqual(expected, actual)

    def test_returns_sum(self):
        expected = 14

        actual = self.sut.add3(1, 4, 9)

        self.assertEqual(expected, actual)

Tester.go()
```

__add3.h__
```
#pragma once

int add3(int a, int b, int c);
```

__add3.c__
```
#include "__main__.h"

int add3(int a, int b, int c)
{
    return a + b + c;
}
```

To use this in real life install the package with `pip install ctdd` (in a virtualenv if you prefer), and run `python add3.py` after each add test or add code iteration.

Test output is exactly what unittest said (with distutils deprecation warning removed):

```
...........
----------------------------------------------------------------------
Ran 11 tests in 2.104s

OK

```