# Importing SAID schemas

SAID publishes CDDL and JSON Schema as separate assets in
[GitHub releases](https://github.com/WebOfTrust/ietf-said/releases). Use
versioned release URLs rather than the mutable `main` branch when a build needs
reproducible inputs.

## Release tags and compatibility

| Artifact | Tag pattern | Asset |
| --- | --- | --- |
| CDDL | `cddl-X.Y.Z` | `said.cddl` |
| JSON Schema | `jsons-X.Y.Z` | `said.schema.json` |

The `cddl-0.1.1` and `jsons-0.1.1` releases were built from the same commit,
`810e25b`, and form the recommended 0.1.1 pair. The respective 0.1.0 assets
are byte-identical to their 0.1.1 counterparts. The two schemas describe
different representation formats; pairing releases does not mean that CDDL
and JSON Schema validate the same wire formats.

Check release notes for future version pairings. Matching version numbers
alone do not establish that later releases were built from the same commit.
The [examples](../examples/README.md) explain the representations and their
validation.

## Downloading a pinned pair

```sh
mkdir -p imports
curl -fLSs https://github.com/WebOfTrust/ietf-said/releases/download/cddl-0.1.1/said.cddl \
  -o imports/said-0.1.1.cddl
curl -fLSs https://github.com/WebOfTrust/ietf-said/releases/download/jsons-0.1.1/said.schema.json \
  -o imports/said-0.1.1.schema.json
```

For automated builds, the [Makefile import example](../examples/Makefile.import.example)
downloads the same pair and provides stable paths for consumers. It adapts the
[vLEI integration template](https://github.com/nedmsmith/vlei-cddl/blob/d78b74bbddb11673b211773d19e0ff4f47fd5e02/Makefile.imports.template);
see the [vLEI import guide](https://github.com/nedmsmith/vlei-cddl/blob/main/imports/README.md)
for a downstream example.

Copy the example into your project or include it from your Makefile, then run
`make imports`. It creates versioned files and the links `imports/said.cddl`
and `imports/said.schema.json`. The version overrides are empty by default;
set them only for exceptional cases such as regression tests:

```sh
SCHEMA_CDDL_VERSION_OVERRIDE=0.1.0 \
SCHEMA_JSON_VERSION_OVERRIDE=0.1.0 make imports
```

Without overrides, the example selects the numerically highest `X.Y.Z`
version already present locally, falling back to 0.1.1. It does **not** query
GitHub for newer releases. To upgrade, download the desired versioned files
into `imports/` before running `make imports`. For reproducible CI builds,
provide only the intended versioned pair in that directory.

Use the CDDL asset with tooling that supports combining CDDL rules, and use
the JSON Schema asset as a schema reference (for example,
`"$ref": "imports/said.schema.json"` when the path is relative to the
referencing schema). Validate representative instances after changing versions.
The schemas describe representations, not the full SAID derivation and
verification process.
