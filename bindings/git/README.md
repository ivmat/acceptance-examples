# Git binding

v0, incomplete.

The acceptance core is neutral about version control. A subject is "a change" or "an integration request".
This binding maps the neutral rows onto git and email mechanisms.

[linux-trailers.toml](linux-trailers.toml) lists, for each row of the Linux process lists, the mechanism that carries it.
The lists are in [requirements/linux-process](../../requirements/linux-process/).

- A change is a commit. Its metadata holds author, committer, time, parents and message.
- A sign-off, fix, link, report, review, test and stable request are message trailers.
- A fix names an earlier change by an id of at least 12 hex characters and its quoted subject.
- An integration request is a merge commit. Its second parent is the head of the requested history.
- A signed request is a signed tag. The merge commit records it in a `mergetag` header.
- A back merge is a merge inside the requested history that has a parent already in upstream history.

Mail-only facts (recipients, permission, linux-next contents, reflogs) are not in git history.
Rows that need them are marked not decidable from history.

The format gaps found while applying these mappings will be published with the Linux example.
