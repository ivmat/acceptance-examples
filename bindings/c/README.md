# C binding

v0, incomplete.

C has no native big-integer type. INTEGER and ENUMERATED content reaches the caller as raw big-endian two's-complement bytes, not as a fixed-width value. A row that bounds the size of an integer therefore needs an explicit length check by the code under test.

Lengths are `size_t`. A row about a length limit is decided against `size_t` arithmetic, including its wrap-around.

How a decoder splits its work is a property of that decoder's design, not of the C language. For example, a decoder may drive decoding from a compiled grammar and leave value-level checks to caller-supplied callbacks. Such properties are recorded in the manifest of the implementation, not in this binding. An applicability record cites the code that performs a check where one exists.
