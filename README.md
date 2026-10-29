# acceptance-examples

This repository holds requirements and will hold acceptance manifests.
It uses the [acceptance format](https://github.com/ivmat/acceptance-format).

The three layers are:

- `requirements/`: the core requirements, independent of an implementation.
- `bindings/`: language specifics that affect a requirement.
- `implementations/`: will hold one acceptance manifest per library.

To apply a list, first declare which rows apply and why.
Then give one claim per row with proof, test evidence, or no evidence.
State the scope and limits of each claim.

Lists are flat today. A later format version may let a row split into child rows.
More manifests will follow.

## Checks

Run `bash gates/run_all.sh` to check the lists, links, text hygiene, secrets, licence files and packages.

License: Apache-2.0 OR MIT, at your option. See `LICENSE-APACHE` and `LICENSE-MIT`.
