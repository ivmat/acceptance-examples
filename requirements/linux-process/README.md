# Linux process requirements

This folder holds lists of rules that the Linux kernel states for its own code and process.
Each list is a flat clause list. The source documents are GPL-2.0 kernel files and are not part of this repository.

## Linux C code rules

[code-rules.clauses.toml](code-rules.clauses.toml) has id `linux-code-rules` and contains 88 rows: 19 from `deprecated.rst` and 69 from `coding-style.rst`.
Edition: Linux v7.3 (`c03c1a14507dfaf8b856c2608f9ac216021fc222`), `Documentation/process/deprecated.rst` and `coding-style.rst`.
The list is a declared slice. It takes every entry of `deprecated.rst`. It takes the `coding-style.rst` rules that a tool or a precise reading can decide.

Each id has the form `KCR-<doc>-<section>-<n>`. `DEP` is `deprecated.rst`; the section is the entry's position in the file. `CS` is `coding-style.rst`; the section is the chapter number.
Titles are short paraphrases. `source`, `line_start` and `line_end` locate the rule in the file at the pinned tag. Read the kernel document for the exact wording.
`force` is MUST, MUST NOT, SHOULD, SHOULD NOT, or `guidance` where the document itself is advisory. `side` is `author`, the person who writes the code.
`method` names how a row is decided: `checkpatch`, `compiler`, `grep` (a text scan) or `reading`; a plus sign joins two.
An acceptance profile that applies this list to two kernel files is in preparation.

## Linux acceptance of a change and of an integration request

Two lists state what the kernel's own process documents ask a maintainer to check.
[commit.clauses.toml](commit.clauses.toml) has id `linux-commit-acceptance` and contains 33 rows for accepting one change.
[pull.clauses.toml](pull.clauses.toml) has id `linux-pull-acceptance` and contains 11 rows for accepting an integration request.
Edition: Linux v7.3, `submitting-patches.rst`, `5.Posting.rst`, `stable-kernel-rules.rst`, `coding-assistants.rst`, `pull-requests.rst`, `rebasing-and-merging.rst`, `handling-regressions.rst`.
Both lists are declared slices. Mail-only, tone and tooling advice is not a row.

Ids have the form `KCA-<doc>-<section>-<n>` and `KPA-<doc>-<section>-<n>`. Titles are short paraphrases. `source`, `line_start` and `line_end` locate the rule at the pinned tag.
Rows are phrased by what the rule requires. A `binding_note` appears only where the document names a git or email mechanism. The mapping to git is in [bindings/git](../../bindings/git/README.md).

`method` has three values. `mechanical` rows can be decided by a script over recorded metadata: 22 in the first list and 7 in the second (one of them an observation row, `force = "observation"`, which records a fact and is never a deviation).
`reading` rows need a person to read the text: 6 and 2. `not-decidable-from-history` rows need facts that the record does not hold, such as mail, a keyring or a build: 5 and 2.

Rules are dated. `in_force_from` is the date the rule text entered the document, found by comparing the document at release tags and its revisions.
`in_force_basis` says how the date was found: the revision that added the text, the release date of the first release holding it, or the start of recorded history.
`in_force_to` is set for the two rows on AI disclosure. A later change, dated 2026-10-14 and not in the pinned release, removed the `Assisted-by` rule from the documents.
A row applies to a change or request only if its date is inside the window. The window is tested against the committer date.
Applications of the lists to the history of two kernel files are in preparation.
