# SAID examples

The examples are partitioned by wire-format output. Three wire formats are
covered: [CBOR](cbor/), [CESR](cesr/), and [JSON](json/). Each wire-format
subfolder contains its examples. They generate representations of digest-based
SAID values from the synthetic cleartext in [common/preimage.data](common/preimage.data).
These examples test digest representations, not the self-referential SAID
derivation procedure. The [URN examples](urn/) show CESR SAIDs in the
`urn:cesr:said:` namespace; URN is an identifier form, not a fourth wire format.

## URN examples

[said-urn-sha-256.urn](urn/said-urn-sha-256.urn) and
[said-urn-blake2b-512.urn](urn/said-urn-blake2b-512.urn) prefix the SHA-256 and
BLAKE2b-512 CESR values with `urn:cesr:said:`. Their `.json` companions are
JSON string instances used for schema validation.

## CBOR representation examples

The `.diag` fixtures use slash-delimited diagnostic annotations, following the
CoRIM examples.

### Algorithm/digest tuple

[said-cbor-alg-digest.diag](cbor/said-cbor-alg-digest.diag) is diagnostic
notation for a two-element array:

- `1` is the IANA Named Information Hash Algorithm identifier for SHA-256.
- The byte string is the raw 32-byte SHA-256 digest of
  [common/preimage.data](common/preimage.data).

It tests the `said-alg-digest` alternative in `said-cbor`.

### CESR text

[said-cbor-cesr.diag](cbor/said-cbor-cesr.diag) is diagnostic notation for a
CBOR text string containing the CESR-encoded SHA-256 digest. It tests the
`said-cesr` alternative in `said-cbor`.

### BLAKE2b-512

[said-cbor-blake2b-512-cesr.diag](cbor/said-cbor-blake2b-512-cesr.diag)
tests a CBOR text string containing a BLAKE2b-512 CESR value. Its `0E`
derivation code is followed by 86 base64url characters. The JSON digest-object
example uses the algorithm name `blake2b-512`; no numeric IANA hash-algorithm
ID is assigned for a CBOR tuple example.

Run `make -C examples check` to generate the wire-format artifacts and validate
them against the CDDL and JSON Schema definitions. The CBOR diagnostics are
converted to CBOR and validated against a CDDL root that selects `said-cbor`.
Each CBOR output also gets a `.pretty` companion from `cbor2pretty.rb` for
inspection; schema validation is performed against the binary `.cbor` file.
