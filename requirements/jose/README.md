# JOSE/JWT requirements

[jose-jwt.clauses.toml](jose-jwt.clauses.toml) contains 278 rows.
Version: v1.2.0, the first public version. The `aliases` field lists ids used in earlier, unpublished versions of the same row.
The list selects requirements from RFC 7515, 7517, 7518 and 7519, with selected
rows from RFC 7638, 7797, 8037 and 8725, and examples from RFC 7520.

All 304 sentences with BCP 14 keywords were classified: 235 mapped,
23 not testable and 46 outside scope; none remained unclassified.
The 235 mapped sentences contribute 205 rows after grouping.
There are also 29 additional rule rows, six split companion rows,
22 informative example rows and 16 table rows (13 algorithm, three key-type).
Total: 205 + 29 + 6 + 22 + 16 = 278.

Each id has the form `JOSE-<RFC>-<section>-<ordinal>`.
The ordinal distinguishes requirements in the same section.
Titles and test scopes are paraphrased. Section and line references locate the source.
Line numbers count newline characters only; a form feed is not a line break.
Official text: `https://www.rfc-editor.org/rfc/rfcNNNN.txt`, replacing NNNN with the RFC number.
Read the RFC for the exact wording.
The RFC text is published by the IETF. It is not part of this repository, and this repository's licence does not cover it.

## Vocabulary

`force` uses BCP 14 keywords: MUST, MUST NOT, SHOULD, SHOULD NOT and MAY.
REQUIRED maps to MUST; RECOMMENDED to SHOULD; NOT RECOMMENDED to SHOULD NOT; OPTIONAL to MAY; table Required maps to MUST, Recommended (also Recommended+) to SHOULD, and Optional to MAY.
`grammar` marks rules on syntax, value types, serialization, definitions and processing steps, and the informative examples.
The `side` values identify these roles:

- `producer`: creates the data.
- `consumer`: reads or validates the data.
- `application`: chooses policy and uses the data.
- `key-author`: creates or describes a key.
- `both`: producer and consumer.

These differ from the format's default clause sets (`shall`/`shall-not`/… and
`encoder`/`decoder`/`both`) to retain the RFCs' own keywords and actor roles.
