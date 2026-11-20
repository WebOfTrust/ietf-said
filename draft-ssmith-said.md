---
title: "Self-Addressing IDentifier (SAID)"
abbrev: "SAID"
docname: draft-ssmith-said-latest
category: std

ipr: trust200902
keyword: Internet-Draft

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
 -
    name: S. Smith
    organization: ProSapien LLC
    email: sam@prosapien.com
 -
    name: N. Smith
    organization: EntropyWorks LLC
    email: entropyworks@outlook.com

normative:
  X690:
    target: https://www.itu.int/rec/T-REC-X.690
    title: "ASN.1 encoding rules: Specification of Basic Encoding Rules (BER), Canonical Encoding Rules (CER) and Distinguished Encoding Rules (DER)"
    author:
      ins: ITU-T
    date: 2021-02
    seriesinfo: Recommendation X.690
  RFC7515:
    target: https://www.rfc-editor.org/rfc/rfc7515
    title: "JSON Web Signature (JWS)"
    author:
      ins: M. Jones, J. Bradley, and N. Sakimura
    date: 2015-05
    seriesinfo: RFC 7515
  RFC7797:
    target: https://www.rfc-editor.org/rfc/rfc7797
    title: "JSON Web Signature (JWS) Unencoded Payload Option"
    author:
      ins: M. Jones
    date: 2016-02
    seriesinfo: RFC 7797
  RFC8785:
    target: https://www.rfc-editor.org/rfc/rfc8785
    title: "JSON Canonicalization Scheme (JCS)"
    author:
      ins: A. Rundgren, B. Jordan, and S. Erdtman
    date: 2020-06
    seriesinfo: RFC 8785
  RFC8949:
    target: https://www.rfc-editor.org/rfc/rfc8949
    title: "Concise Binary Object Representation (CBOR)"
    author:
      ins: C. Bormann and P. Hoffman
    date: 2020-12
    seriesinfo: RFC 8949
  CESR:
    target: https://datatracker.ietf.org/doc/draft-ssmith-cesr/
    title: Composable Event Streaming Representation (CESR)
    author:
      ins: S. Smith
      name: Samuel M. Smith
      org: ProSapien LLC
    date: 2021

informative:
  RFC9995:
    target: https://www.rfc-editor.org/rfc/rfc9995
    title: "CBOR Object Signing and Encryption (COSE) Hash Envelope"
    author:
      ins: O. Steele, S. Lasker, and H. Birkholz
    date: 2026-07
    seriesinfo: RFC 9995
  KERI:
    target: https://arxiv.org/abs/1907.02143
    title: Key Event Receipt Infrastructure (KERI)
    author:
      ins: S. Smith
      name: Samuel M. Smith
      org: ProSapien LLC
    date: 2021
  URNSAID:
    target: https://www.iana.org/assignments/urn-namespaces/urn-formal/said
    title: urn said namespace registration
    author:
      ins: W. Chu
      name: Wenjing Chu
      org: Future Wei
    date: 2026
  VLEI:
    target: https://github.com/GLEIF-IT/vLEI-schema/blob/97850396f504bf8c4e19a42af3290e4b2618f50e/legal-entity-vLEI-credential.json
    title: "Legal Entity vLEI Credential Schema"
    author:
      ins: Global Legal Entity Identifier Foundation
    date: 2023-11

tags: IETF, SAID, CESR, SAD, ACDC, KERI, COSE, JOSE, CBOR

--- abstract

A `SAID` (Self-Addressing IDentifier) is a self-referential,
content-addressable identifier cryptographically bound to a deterministic serialization that contains the identifier as a field.
Derivation replaces that field with a same-length placeholder, computes a digest over the resulting serialization,
and encodes the digest as the `SAID`.
Verification repeats the process; a mutation causes verification to fail,
assuming the digest algorithm remains collision-resistant.
Embedding a preferred content address in the serialization reduces ambiguity and supports interoperable, tamper-evident reasoning.

Given sufficient cryptographic strength and successful verification under the same derivation and serialization profile,
a signature, digest, or other `SAID` that commits to a `SAID` also commits to the serialization it identifies.
`SAIDs` therefore support compact references to immutable data, including Verifiable Credentials, Ricardian Contracts, schemas,
and other authenticatable data structures.

Reproducible derivation requires a deterministic wire-to-memory-to-wire round trip.
Decoding must preserve every distinction that affects serialization.
Re-encoding under the same profile must reproduce the same bytes.
Ordered mappings, deterministic `CBOR`, and ASN.1 `DER` are examples of ways to achieve this.

This document describes a native, self-referential `CESR` encoding and related profiles for `COSE`/`CBOR` and `JOSE`/`JSON`.
The latter profiles require additional rules to provide self-reference.

--- middle

# Introduction

A content-addressable identifier is derived from a serialization and is cryptographically bound to its bytes.
This binding provides a root of trust for reasoning about the content.
A sufficiently strong cryptographic commitment to the identifier also commits to the serialization.

A `self-addressing identifier (SAID)` is a content-addressable identifier that is also self-referential.
It is included in the serialization it identifies.
This document describes the SAID derivation and verification process and the supported CESR, CBOR, JSON, and URN representations.

The urn said is now a registered namespace at IANA [URNSAID].
The urn said namespace uses the SAID protocol.

## Requirements Language

{::boilerplate bcp14-tagged}

# Architecture

An application profile defines the schema for the data object, identifies the SAID field and placeholder procedure,
and selects a deterministic serialization profile.
The serialization profile specifies how to encode and decode the data object so both endpoints reproduce the same bytes.

~~~
       Producer                       Consumer

+-----------------------+
| 1. Render             |
|    deterministic      |
|    data object        |
| 2. Derive SAID and    |
|    embed in object    |
| 3. Validate object    |
|    against schema     |
| 4. Encode object      |
|    in wire format     |      +-----------------------+
| 5. Send object        |wire->| 6. Receive data       |
+-----------------------+      |    object from wire   |
                               | 7. Decode object      |
                               |    using profile      |
                               | 8. Validate object    |
                               |    against schema     |
                               | 9. Verify object      |
                               |    integrity using    |
                               |    embedded SAID      |
                               | 10. Hand off object   |
                               |     to application    |
                               +-----------------------+
~~~

## Technology Scope

The architecture is independent of a particular programming language or in-memory data structure.
This document describes SAID representations for CESR, CBOR, JSON, and URN,
with CDDL and JSON Schema definitions where applicable.
Application profiles select the schema for the data object and the deterministic serialization profile.
The Python mappings and particular digest, serialization, or envelope choices in the examples illustrate possible realizations;
they are not prerequisites for implementing the architecture.

## Integrity Principle

An authenticatable data serialization is digitally signed using a non-repudiable asymmetric-key signature scheme.
A verifier with the corresponding public key can validate the signature and attribute the serialization to its signer.
Such serializations may contain self-referential identifiers and references to other serializations.
An unbound identifier is only a label: anyone can copy it into different content and claim that content is the one it identifies.
This can leave the same data with two identifiers—a self-referential but unbound label and an externally tracked content address.

## Schema Conformance

The application schema describes the permitted structure and constraints of the data object.
The producer checks the completed data object before sending it.
The consumer checks the decoded data object before handing it to the application.
These checks establish conformance to the application data model; they are distinct from SAID verification.
The schemas in this document define the allowed forms of a `SAID` value,
not the structure of the application data object that contains it.
An application profile defines that structure.

## SAID-Based Payload Integrity and Embedding

The embedded SAID binds the data object to its deterministic serialization.
Derivation replaces the SAID field with a same-length placeholder,
serializes the data object using the shared deterministic serialization profile,
computes the digest identified by the SAID, and places the encoded digest in the field.
Verification repeats the process and compares the recomputed value with the embedded SAID.
The serialization profile accounts for distinctions that affect the digest bytes, such as field order and value representation.

Some application profiles use a detached payload that contains its own SAID, for example vLEI [VLEI].
Such profiles are subject to the conditional requirements in Section 4.
Applications can carry such payloads in enclosing structures,
including signature or MAC envelopes when producer authentication is needed.
The enclosing structures and their authentication processing are outside the scope of this document.
A digest carried only in an envelope, and not embedded in the identified payload,
is a content address for that payload rather than a self-referential SAID.

## Protocol Flow

The producer derives and embeds the SAID in the data object,
validates the completed data object against the application schema, and encodes it in the wire format.
The consumer receives and decodes the data object from the wire,
validates the decoded data object against the application schema,
verifies its integrity using the embedded SAID and shared deterministic serialization profile,
and hands it off to the application.
Schema validation checks the data object's conformance to the application schema;
SAID verification checks the binding between the data object and the digest input.
Both checks are part of the end-to-end flow shown above.

# Example Digest Computation and Payload Embedding

These examples use Python's insertion-ordered `dict`, JSON, and selected digest algorithms only for illustration.
Implementations may use other in-memory structures; a profile may specify another wire format or supported digest,
as long as both endpoints reproduce the same digest input.

## Example Computation

The `CESR` encoding of a `Blake3-256` 32-byte digest contains 44 Base64 URL-safe characters.
The first character, E, identifies `Blake3-256`.
A fixed-field serialization using that algorithm therefore reserves 44 characters for the `SAID`.
Consider this initial serialization:

~~~
field0______field1______________________________________field2______
~~~

Replace field1 with 44 placeholder characters:

~~~
field0______############################################field2______
~~~

Computing `Blake3-256` over the placeholder serialization and encoding the digest with `CESR` produces:

~~~
E8wYuBjhslETYaLZcxMkWrhVbMcA8RS1pKYl7nJ77ntA
~~~

Replacing the placeholder with that `SAID` produces the final serialization:

~~~
field0______E8wYuBjhslETYaLZcxMkWrhVbMcA8RS1pKYl7nJ77ntA______
~~~

Verification reverses these steps.

## Serialization Generation

### Deterministic In-Memory Representations

The crucial consideration in `SAID` generation is reproducibility across the wire-to-memory-to-wire round trip.
The digest input is a byte sequence received from, or prepared for, a deterministic wire format.
The resulting in-memory representation retains every distinction needed to reconstruct the same serialization.

A deterministic in-memory representation preserves field order when it affects the wire format, exact value types,
numeric representation rules, string contents, optional-field presence, tags, and application normalization choices.
Re-encoding under the same deterministic profile produces identical bytes.
The digest covers those reproduced wire bytes, not an implementation-specific memory layout.

Suitable realizations include:

- An insertion-ordered Python 3.7 or later dictionary paired with a fixed `JSON` serialization profile.
- Deterministic `CBOR` as described by [RFC8949].
- ASN.1 values encoded with `DER` under ITU-T [X690].

These are examples rather than prerequisites.
Any representation works if decoding preserves the information needed for deterministic re-encoding.
Independent implementations must then reproduce the same bytes.

When mapping order affects the wire format, the in-memory representation preserves that order.
A profile can retain application-defined insertion order, sort keys, or apply schema-defined component ordering.
Encoders and decoders apply the selected rule consistently.

Programming-language mappings have not always preserved insertion order.
If a native mapping lacks a stable ordering contract, an ordered mapping, schema-defined record,
or explicit canonical sorting step establishes reproducibility.

### Example Python dict to JSON Serialization with SAID

These examples include a `schema` field containing the `SAID` of the general-purpose schema for `SAID`-bearing objects shown below.
It lets a consumer identify a baseline schema for the embedded identifier fields;
an application profile can impose additional constraints on application-specific fields.
Including a `schema` field is a useful convention for schema discovery and validation, not a requirement of the `SAID` format.
The examples use the common field order `said`, `schema`, `first`, `last`, `role`;
the `schema` value remains fixed while the `said` value is replaced by a placeholder during derivation.

Suppose the initial value of a Python `dict` is as follows:

~~~ python
{
  "said": "",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

As before, the `SAID` will be a 44-character CESR-encoded Blake3-256 digest.
The serialization will be `JSON`.
The `said` field value in the `dict` is to be populated with the resulting `SAID`.
First the value of the `said` field is replaced with a 44-character dummy string:

~~~ python
{
  "said": "############################################",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

The `dict` is then serialized into JSON with no extra whitespace:

~~~ json
{
  "said":"############################################",
  "schema":"IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first":"Sue",
  "last":"Smith",
  "role":"Founder"
}
~~~

The Blake3-256 digest is computed on that serialization and encoded in `CESR` to provide the `SAID`:

~~~
E52Jj6MfPzQnAs6X3PdGybZlPjjr7_ZRbrwdxEyzLunU
~~~

The value of the `said` field is replaced with the computed and encoded `SAID`:

~~~ json
{
  "said":"E52Jj6MfPzQnAs6X3PdGybZlPjjr7_ZRbrwdxEyzLunU",
  "schema":"IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first":"Sue",
  "last":"Smith",
  "role":"Founder"
}
~~~

The final serialization may be converted to a Python `dict` by deserializing the JSON:

~~~ python
{
  "said": "E52Jj6MfPzQnAs6X3PdGybZlPjjr7_ZRbrwdxEyzLunU",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

The generation steps may be reversed to verify the embedded `SAID`.
The protocol for mappings assumes the fields in the serialization are ordered in stable, round-trippable, reproducible order,
i.e., canonical.
The natural canonical ordering is called `field insertion order`.

### Example Ordered Mapping to JSON Serialization with SAID

The following example shows the serialized `JSON` form of the deterministic, insertion-ordered Python `dict` above.
The same derivation applies to any in-memory representation that preserves the specified field order and value types.

~~~ json
{
  "said":"",
  "schema":"IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first":"Sue",
  "last":"Smith",
  "role":"Founder"
}
~~~

Replace "said" with a 44-character placeholder and serialize without extra whitespace:

~~~ json
{
  "said":"############################################",
  "schema":"IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first":"Sue",
  "last":"Smith",
  "role":"Founder"
}
~~~

`Blake3-256` over those `JSON` bytes, encoded with `CESR`, produces E52Jj6MfPzQnAs6X3PdGybZlPjjr7_ZRbrwdxEyzLunU.
Replacing the placeholder produces:

~~~ json
{
  "said":"E52Jj6MfPzQnAs6X3PdGybZlPjjr7_ZRbrwdxEyzLunU",
  "schema":"IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first":"Sue",
  "last":"Smith",
  "role":"Founder"
}
~~~

Verification restores the placeholder, reproduces the same `JSON` bytes, and recomputes the `SAID`.

### Example Schema Immutability Using JSON Schema with SAIDs

A `JSON` Schema can use the same derivation procedure to give its "$id" field a self-referential,
cryptographically bound identifier.
The following general-purpose schema for `SAID`-bearing objects requires CESR-encoded `SAIDs` in the `said` and `schema` fields
and permits additional application-defined properties.
Requiring a `schema` field is a useful application-profile convention; the `SAID` format itself does not require it.
The `schema` values in the examples identify this base schema.
The placeholder serialization is:

~~~ json
{
  "$id": "############################################",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "said": {
      "type": "string",
      "pattern": "^(?:(?:E|F|G|H|I)[A-Za-z0-9_-]{43}|0(?:D|E|F|G)[A-Za-z0-9_-]{86})$"
    },
    "schema": {
      "type": "string",
      "pattern": "^(?:(?:E|F|G|H|I)[A-Za-z0-9_-]{43}|0(?:D|E|F|G)[A-Za-z0-9_-]{86})$"
    }
  },
  "required": ["said", "schema"],
  "additionalProperties": true
}
~~~

Replacing the placeholder with 44 `#` characters, canonicalizing with `JCS`, and computing `SHA-256` produces
the CESR `SAID` IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY.
Replacing the placeholder yields:

~~~ json
{
  "$id": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "said": {
      "type": "string",
      "pattern": "^(?:(?:E|F|G|H|I)[A-Za-z0-9_-]{43}|0(?:D|E|F|G)[A-Za-z0-9_-]{86})$"
    },
    "schema": {
      "type": "string",
      "pattern": "^(?:(?:E|F|G|H|I)[A-Za-z0-9_-]{43}|0(?:D|E|F|G)[A-Za-z0-9_-]{86})$"
    }
  },
  "required": ["said", "schema"],
  "additionalProperties": true
}
~~~

Data structures using embedded `SAIDs` in this way are referred to as self-addressing data (SAD).

## Discussion

A recognized derivation code identifies how to verify the binding between a `SAID` and its serialization.
A valid `SAID` confirms that the serialization reproduces the bytes used during derivation;
a mutation produces a different identifier.
References to other serializations by `SAID` support compact,
tamper-evident composition without embedding the referenced content in full.

# SAID Schema Definitions

This section defines the syntax of the supported `SAID` values.
The CDDL fragments define the `said` type for CESR, CBOR, JSON, and URN representations.
The JSON Schema fragments define `SAID` values represented as JSON, including CESR strings and URNs.
CBOR representations rely exclusively on the CDDL schema expression.
These schemas define `SAID` values, not the application data objects that contain them.

An application profile that requires a detached payload to carry a self-referential `SAID` MUST specify the location and
representation of the embedded `SAID` field, the placeholder used during derivation,
and the deterministic serialization profile used to generate and verify the `SAID`.

## CDDL

The CDDL fragments below collectively define the top-level `said` type.
The root fragment declares the type and its representation alternatives;
the following fragments define those alternatives in the order used to assemble the schema.

### Root `said` Type

The root fragment defines `said` as an extensible choice over the supported representations.

~~~ cddl
{::include cddl/said-root.cddl}
~~~

### URN Representation

The URN representation prefixes a CESR value with `urn:cesr:said:`.

~~~ cddl
{::include cddl/said-urn.cddl}
~~~

### CBOR Representation

The CBOR representation is either a CESR value or an array containing an integer hash algorithm identifier
and a byte-string digest.

~~~ cddl
{::include cddl/said-cbor.cddl}
~~~

### JSON Representation

The JSON representation is either a CESR value or an object containing a textual hash algorithm identifier
and an unpadded base64url digest.

~~~ cddl
{::include cddl/said-json.cddl}
~~~

### CESR Representation

The CESR representation combines a derivation code with base64url-encoded digest text.
The schema defines codes and digest-text lengths for 256-bit and 512-bit digest values.

~~~ cddl
{::include cddl/said-cesr.cddl}
~~~

## JSON Schema

The JSON Schema fragments below collectively define a schema for JSON-encoded `SAID` values.
The root schema provides the `said` entry point;
the remaining fragments add definitions for URN, JSON, and CESR representations.
The fragments are combined by adding their `definitions` to the root schema's `definitions` object.

### Root `said` Schema

The root schema selects either a JSON representation or a URN representation.

~~~ json
{::include jsons/said-root.json}
~~~

### URN Schema

The URN schema restricts a string to the `urn:cesr:said:` prefix followed by a valid CESR value.

~~~ json
{::include jsons/said-urn.json}
~~~

### JSON Object Representation Schema

The JSON schema accepts a CESR string or an object containing a hash algorithm identifier
and a base64url digest string.

~~~ json
{::include jsons/said-json.json}
~~~

### CESR Schema

The CESR schema restricts strings to the supported derivation codes and digest-text lengths.

~~~ json
{::include jsons/said-cesr.json}
~~~

# Realizing SAID-Like Properties with CESR, COSE, and JOSE

The properties provided by a `SAID` can be realized through multiple representation and security frameworks.
Each realization requires a deterministic mapping from an application data model to bytes,
an unambiguous indication of the digest algorithm and digest value,
and verification rules that bind those bytes to the identifier.
The following subsections distinguish the native `CESR` construction from profiles based on `COSE`/`CBOR` and `JOSE`/`JSON`.

## CESR Realization

The `CESR` realization defined by this document embeds the encoded digest in the serialization itself.
Its derivation code identifies the digest algorithm and encoding.
The dummy-value procedure resolves the circularity of hashing content that contains its own identifier.
This construction provides both content addressing and self-reference.
The identifier is a field in the exact serialization to which it is cryptographically bound.

The primary expression of a `CESR` primitive is textual and uses Base64 URL-safe characters.
CESR primitives can be round-tripped to a compact binary representation without loss.
The derivation code enables digest algorithm agility by identifying the algorithm used for each `SAID`.
`CESR` was developed for the [KERI] protocol.

## COSE/CBOR Realization

[RFC9995] defines `COSE` hash envelopes by adding protected-header parameters that identify the payload hash algorithm,
the media type or content format of the preimage, and optionally a location from which the preimage can be retrieved.
A `SAID`-like profile can use these parameters as follows:

The following steps illustrate one possible `COSE` hash-envelope construction.
Applications that need producer authentication can place the hash envelope in an enclosing signature or MAC structure;
those structures and their authentication processing are outside the scope of this specification.

1. Encode the application data using a specified deterministic `CBOR` profile consistent with Section 4.2 of [RFC8949].
   The application profile must resolve choices that could produce different byte strings for equivalent data.

2. Compute the selected cryptographic digest over those deterministic `CBOR` bytes.
   The digest functions as the content-addressable identifier for that byte representation.

3. Construct an [RFC9995] hash envelope containing the digest.
   Its protected header identifies the payload hash algorithm.
   The preimage content type and location parameters can be supplied when needed for interpretation or discovery.

4. An application profile can protect the hash envelope with a `COSE` signature or MAC when producer authentication is needed.
   A verifier can validate that protection over the envelope and its digest without access to the detached preimage.
   When the application data is available, the verifier deterministically encodes it under the same application profile,
   recomputes the digest, and compares the result with the envelope payload.

This construction provides deterministic content addressing and a cryptographic commitment to detached content.
It does not by itself produce a self-referential `SAID`.
An application profile must embed the digest in the payload to make it self-referential.
It must also follow the detached-payload convention in Section 2.2.

The following examples show an application-specific data object and an illustrative `COSE_Sign1` envelope.

### CDDL and CBOR Data Object Example

The ordered-mapping example in Section 3.2.3 is represented here as a `CBOR` data object.
This example's deterministic serialization profile preserves the application-defined map order shown below;
it does not use the core deterministic map-key ordering rules in [RFC8949].
The inline `CDDL` defines the required `said` and `schema` fields and an extension point for application-defined fields.
The Sue Smith example extends it with `first`, `last`, and `role`.

~~~ cddl
said-example = {
  "said"   => said-cesr,
  "schema" => said-cesr,
  * $$said-example-map-extension
}

$$said-example-map-extension //= (
  "first" => tstr,
  "last"  => tstr,
  "role"  => tstr
)
~~~

The placeholder form used for derivation replaces the `said` value with 44 `#` characters.
This intermediate form is not a valid `said-example`, because the placeholder is not a CESR `SAID`.

~~~ cbor-diag
{
  "said": "############################################",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

Encoding this data object with the example's ordered-map `CBOR` profile and computing `SHA-256` produces:

~~~
0e83f2c5a0a41215979410a1e4d7981b8fc0b338d073190609c5f6c813496ab3
~~~

Encoding the digest with the `CESR` derivation code for `SHA-256` produces the embedded `SAID`:

~~~
IDoPyxaCkEhWXlBCh5NeYG4_AszjQcxkGCcX2yBNJarM
~~~

The final data object replaces the placeholder with that `SAID`:

~~~ cbor-diag
{
  "said": "IDoPyxaCkEhWXlBCh5NeYG4_AszjQcxkGCcX2yBNJarM",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

The final data object conforms to `said-example`, and its `said` value conforms to `said-cesr`.
To verify the `SAID`, validate the data object, replace its `said` value with the same 44-character placeholder,
encode the resulting map using the same ordered-map `CBOR` profile,
recompute the `SHA-256` digest, and compare the resulting CESR value with the embedded `SAID`.

### COSE_Sign1 Envelope Structure

The following illustrative `CDDL` describes a `COSE_Sign1` envelope whose byte-string payload contains a CBOR-encoded `SAID`.

~~~ cddl
COSE_Sign1 = #6.18([
  protected   : bstr .cbor protected-header,
  unprotected : {},
  payload     : bstr .cbor said,
  signature   : bstr
])

protected-header = {
  ; COSE signature algorithm identifier
  1   => int,
  ; Hash algorithm used to produce the payload SAID
  258 => int,
  ; Content type of the detached preimage
  259 => "application/cbor"
}
~~~

Protected-header parameter 1 identifies the `COSE` signature algorithm,
parameter 258 identifies the hash algorithm used to produce the payload `SAID`,
and parameter 259 identifies the preimage content type.
The envelope payload contains the `CBOR` encoding of the `SAID` for `said-example`.
That `SAID` is computed from the deterministic `CBOR` encoding of its placeholder form.
Any `COSE` protection is validated according to the application profile.

## JOSE/JSON Realization

`JOSE` provides `JSON`-based signature and MAC containers through `JWS` as defined by [RFC7515].
Because `JSON` permits multiple textual representations of the same data model,
a `SAID`-like `JOSE` profile first specifies an invariant byte representation.
[RFC8785] `JSON` Canonicalization Scheme (`JCS`) is one suitable profile: it constrains input to `I-JSON`,
serializes primitives consistently, sorts object properties deterministically, and emits UTF-8.

A `JOSE` realization can proceed as follows:

1. Canonicalize the application `JSON` using `JCS` or another explicitly identified deterministic `JSON` profile.

2. Compute a digest over the canonical UTF-8 bytes.
   Encode it using unambiguous base64url.
   The application profile fixes the digest algorithm and canonicalization profile.
   Protected parameters may identify them, but verifiers must understand those parameters.

3. Place the base64url-encoded digest in a profiled protected-header parameter.
   List that parameter in "crit" so that a verifier recognizes the hash-envelope processing rules.
   Omit the `JWS` payload from the `JSON` serialization.
   The signature covers the protected header containing the digest;
   the detached application data is used only to recompute and compare that digest.

4. A verifier validates the `JWS` protected header and signature, obtains the application data separately,
   restores any defined placeholder, canonicalizes the `JSON` under the identified profile, recomputes the digest,
   and compares it with the digest carried in the protected header.

`JOSE` does not currently register a general-purpose hash-envelope digest header equivalent to [RFC9995].
The example below therefore uses illustrative profiled parameter names.
A closed profile can define private names,
while interoperable deployment calls for registered or collision-resistant names and explicit critical-parameter processing.
As with the `COSE` profile, this provides deterministic content addressing and a cryptographic commitment.
The application profile must define an embedded identifier field and placeholder or exclusion rule for native self-reference.

### JSON Example

The application data is the same structure used in Section 3.2.2:

~~~ json
{
  "said": "",
  "schema": "IH3Nj8qCy--8DKS8e1h9sb69OTNYCKM1iRF3OvTzRimY",
  "first": "Sue",
  "last": "Smith",
  "role": "Founder"
}
~~~

After replacing "said" with the profile-defined placeholder, the structure is canonicalized with `JCS` and hashed with `SHA-256`.
The digest is base64url encoded and placed in the protected header.
The following flattened `JWS` `JSON` serialization illustrates the envelope before base64url encoding of the protected header:

~~~ json
{
  "protected": {
    "alg": "ES256",
    "crit":
      ["payload-digest",
      "payload-digest-alg",
      "payload-canonicalization"],
    "payload-digest": "<base64url(SHA-256(JCS(placeholder-form)))>",
    "payload-digest-alg": "sha-256",
    "payload-canonicalization": "jcs",
    "cty": "application/json"
  },
  "signature": "<base64url(signature)>"
}
~~~

In an actual `JWS` `JSON` serialization, "protected" is the base64url encoding of the UTF-8 `JSON` protected-header object,
not the object shown inline above.
The top-level "payload" member is absent.
A verifier decodes and validates the protected header, obtains the application data out of band,
reconstructs the placeholder form, applies `JCS`, recomputes `SHA-256`, and compares the result with "payload-digest".
The names beginning with "payload-" are illustrative profile parameters and are not registered `JOSE` header parameters.

## Common Requirements and Distinctions

All three realizations depend on collision-resistant digests, deterministic serialization, explicit algorithm identification,
and exact verification rules.
`CESR` integrates these elements into an identifier designed for self-reference.
`COSE` with [RFC9995] standardizes a signed or MAC-protected hash envelope for `CBOR`-oriented systems.
`JOSE` can provide analogous behavior for `JSON`-oriented systems.
Such a profile combines deterministic `JSON` canonicalization with a defined digest envelope.
Implementations do not treat semantic equivalence after parsing as sufficient;
verification is performed over the exact deterministic byte representation prescribed by the applicable profile.

# Security Considerations

Security depends on the selected digest algorithm's collision and second-preimage resistance.
It also depends on consistent implementation of the deterministic serialization profile.
A verifier that uses different field ordering, type conversion, normalization, placeholder,
or exclusion rules can compute a different digest from the producer.
Profiles therefore need to identify the digest algorithm, deterministic encoding rules, placeholder or exclusion procedure,
and protected metadata needed to interpret the digest.
Implementations should reject unsupported algorithms and profiles, malformed or ambiguous serializations,
duplicate map keys or object member names, and protected parameters they do not understand.

A valid `SAID` demonstrates integrity of the identified serialization; it does not by itself authenticate its producer,
establish authorization or trust, or provide freshness or confidentiality.
A protocol or application profile requiring authenticated origin must specify an authentication mechanism.
It must also define the key and trust rules and apply that mechanism.
Successful `SAID` verification alone does not provide evidence of the producer's identity or authorization.
The `COSE_Sign1` example in this document is illustrative and does not make use of `COSE` signing a requirement.

# IANA Considerations

This document has no IANA actions.

# Appendix: Embedding SAIDs in URLs

A `SAID` can serve as a stable content identifier while discovery information is maintained separately.
An application can include the compact `SAID` in a protocol message or data structure,
then use DNS-based discovery to locate a URI for a service or server from which the detached payload can be retrieved.
After retrieval, the application verifies the payload against the `SAID`.

Separating integrity from discovery reduces message and data-structure size.
The `SAID` still provides a cryptographic commitment to the referenced content.
The `SAID` identifies the content; DNS and the resolved URI identify a current retrieval location.
A change to that location for administrative reasons, such as a company domain-name change or service migration,
does not alter the content bytes and therefore does not invalidate existing commitments to the `SAID`.

The KERI community refers to this discovery pattern as an Out-of-Band Introduction (`OOBI`).
An `OOBI` associates a stable identifier with discovery information.
Clients use that information to find the entity's current endpoint or resources for interaction or content retrieval.

# Appendix: JSON Schema with SAIDs

This appendix will define normative rules for using `SAIDs` to make JSON Schema immutable and prevent schema malleability attacks.

--- back

# Acknowledgments
{:numbered="false"}

Members of the KERIpy development team and the ToIP ACDC Working Group.
