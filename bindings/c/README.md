# C binding

v0, incomplete.

C has no native big-integer type: INTEGER and ENUMERATED content reaches
the caller as raw big-endian two's-complement bytes, not a fixed-width
value, so overflow is the caller's problem.

Length is `size_t`. A compiled grammar drives decoding through bytecode
(tag-match opcodes plus caller-supplied action callbacks), not generated
per-type parse functions, so a row about value-level checks (BOOLEAN's
canonical `0xff`, INTEGER's minimal form, string character sets) is the
action callback's job, never the decoder's. An applicability record
should cite the action that does the check, where one exists.
