# EzrMod (Easier Modeling)

## Introduction

**EzrMod** is a python3 module which creates a tape of operations carried out inside a function
in order to enable a forward pass (evaluation of values) and a reverse pass (evaluation of 
AD derivatives in reverse mode). This module brings the convenience of programming in python
with the unmatched performance of C in order to create scientific computing codes requiring 
derivative evaluation which are easily readable, extremely efficient and amazingly fast.

## Features

- The tape created in this module focuses on reducing redundancy to alleviate any optimization
  and efficiency concern that a user may have. As soon as an operation is recorded, any previous
  evaluation of the same operation between the same operands is linked to the current evaluation,
  thus increasing optimization. *So, no matter how many times you call a function or repeat a
  pattern, we've got the redundancy covered.*

- The tape stores any non-zero constants only once, thus saving space. *So, you might multiply
  variables with, say 0.5, a hundred times and yet there will only be a single copy of the constant
  0.5 on the tape.*

- A backend in C has been provided in the Backend folder. And as seen in the test.py file in the
  test folder, any C function can easily be called from python (with an overhead though). So, if
  you are planning to run a subroutine in a loop (like evaluating the HLLC flux on several
  thousands of faces), better wrap the tape in a loop in a short C subroutine and call the whole
  looped version from python which will save any overheads.

## Performance

Something like the HLLC flux and its exact jacobian are evaluated within 10 microseconds. So, now
you can bring C-like performance to a python code.

## Readability

If you look at the HLLC code, it reads like a breeze. The inputs needed to pass to the C tape are
defined in the beginning and then the tape evaluation goes on. The taped function should have only
one argument - the variable for tape itself, though it can call any functions from within as required.

## Running tests

Compile the backend shared library
```
cd Backend
make
```

To understand how tapes are created and how C functions are called, check out `test.py`

To understand how you could write a complex function and compile the tape, look at the `HLLC.py`.
You can run `compile.py` to create tapes, which can be read/visualized in the files named `trace_*`.
The tapes are stored in the pickled `*.tape` files for python to read though.
