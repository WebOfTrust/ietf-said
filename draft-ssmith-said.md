---
title: "Self-Addressing IDentifier (SAID)"
abbrev: "SAID"
docname: draft-ssmith-said-latest
category: info

ipr: trust200902
area: TODO
workgroup: TODO Working Group
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
  RFC9995:
    target: https://www.rfc-editor.org/rfc/rfc9995
    title: "CBOR Object Signing and Encryption (COSE) Hash Envelope"
    author:
      ins: O. Steele, S. Lasker, and H. Birkholz
    date: 2026-07
    seriesinfo: RFC 9995
  CESR:
    target: https://datatracker.ietf.org/doc/draft-ssmith-cesr/
    title: Composable Event Streaming Representation (CESR)
    author:
      ins: S. Smith
      name: Samuel M. Smith
      org: ProSapien LLC
    date: 2021

informative:
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

tags: IETF, SAID, CESR, SAD, ACDC, KERI, COSE, JOSE, CBOR

--- abstract

A `SAID` (Self-Addressing IDentifier) is a self-referential, content-addressable identifier cryptographically bound to a deterministic serialization that contains the identifier as a field. Derivation replaces that field with a same-length placeholder, computes a digest over the resulting serialization, and encodes the digest as the `SAID`. Verification repeats the process; a mutation causes verification to fail, assuming the digest algorithm remains collision-resistant. Embedding a preferred content address in the serialization reduces ambiguity and supports interoperable, tamper-evident reasoning.

Given sufficient cryptographic strength and successful verification under the same derivation and serialization profile, a signature, digest, or other `SAID` that commits to a `SAID` also commits to the serialization it identifies. `SAIDs` therefore support compact references to immutable data, including Verifiable Credentials, Ricardian Contracts, schemas, and other authenticatable data structures.

`SAIDs` are encoded with `CESR` (Composable Event Streaming Representation) [CESR]. A `CESR` derivation code identifies the cryptographic suite or digest algorithm. A `CESR` primitive's primary expression is textual and uses Base64 URL-safe characters; primitives can also be round-tripped to a compact binary representation without loss. Because each serialization can indicate its own digest algorithm, `CESR` supports cryptographic agility. `CESR` was developed for the [KERI] protocol.

Reproducible derivation requires a deterministic wire-to-memory-to-wire round trip: decoding must preserve every distinction that affects serialization, and re-encoding under the same profile must reproduce the same bytes. Ordered mappings, deterministic `CBOR`, and ASN.1 `DER` are examples of ways to achieve this.

This document describes the native, self-referential `CESR` realization and profiles related content-addressing and cryptographic-commitment properties for `COSE`/`CBOR` and `JOSE`/`JSON`. The `COSE` profile uses the [RFC9995] hash envelope with a digest of deterministic `CBOR`. The `JOSE` profile omits the `JWS` payload and carries the digest in a critical protected-header parameter; its JSON examples use the JSON Canonicalization Scheme [RFC8785]. These `SAID`-like constructions are not natively self-referential: additional embedding and derivation rules are needed to obtain that property.

--- middle

# Introduction

A content-addressable identifier is derived from a serialization and is cryptographically bound to its bytes. This binding provides a root of trust for reasoning about the content: a sufficiently strong cryptographic commitment to the identifier is functionally equivalent to a commitment to the serialization.

A `self-addressing identifier (SAID)` is a content-addressable identifier that is also self-referential: it is included in the serialization it identifies. Directly hashing a serialization that contains its own digest creates a circular dependency, and changing any part of the serialized content changes its digest. `SAID` derivation resolves this by replacing the identifier field with a same-length placeholder, hashing the resulting serialization, and replacing the placeholder with the encoded digest. A verifier can repeat these steps to verify or re-derive the identifier.

This derivation of an identifier from the content it identifies is called `self-addressing`. A conventional content address is computed over completed content and is normally maintained outside that content; it cannot simply be embedded in the content it identifies. A `SAID`, by contrast, is both embedded in and cryptographically bound to its serialization. Its `CESR` derivation code identifies the digest algorithm used to create it.

An authenticatable data serialization is digitally signed using a non-repudiable asymmetric-key signature scheme. A verifier with the corresponding public key can validate the signature and attribute the serialization to its signer. Such serializations may contain self-referential identifiers and references to other serializations. An unbound identifier is only a label: anyone can copy it into different content and claim that content is the one it identifies. This can leave the same data with two identifiers—a self-referential but unbound label and an externally tracked content address.

A `SAID` binds the embedded identifier to the serialization that contains it, resolving that ambiguity: successful verification shows that the serialization has not been changed, subject to the digest algorithm's security. References to other serializations by `SAID` provide compact, tamper-evident composition without embedding each referenced serialization in full.

Reproducible verification depends on a deterministic serialization profile. Decoding and re-encoding must preserve every distinction that affects the bytes being hashed, including field order and value representation. The same profile must be used for derivation and verification.

The urn said is now a registered namespace at IANA [URNSAID].
The urn said namespace uses the SAID protocol.

# Generation and Verification Protocols

The self-addressing identifier (`SAID`) verification procedure follows these steps:

- Copy the embedded `CESR` [CESR] encoded `SAID` from the serialization.

- Replace the `SAID` field value with a placeholder of the same length. The placeholder character is # (ASCII 35 decimal, 23 hexadecimal).

- Compute the digest over the serialization containing the placeholder, using the digest algorithm identified by the copied `SAID`’s `CESR` derivation code.

- Encode the computed digest with `CESR` to produce a `SAID` having the same total length as the placeholder and copied `SAID`.

- Compare the copied `SAID` with the recomputed `SAID`. Matching values indicate successful verification.

## Example Computation

The `CESR` encoding of a `Blake3-256` 32-byte digest contains 44 Base64 URL-safe characters. The first character, E, identifies `Blake3-256`. A fixed-field serialization using that algorithm therefore reserves 44 characters for the `SAID`. Consider this initial serialization:

```
field0______field1______________________________________field2______
```

Replace field1 with 44 placeholder characters:

```
field0______############################################field2______
```

Computing `Blake3-256` over the placeholder serialization and encoding the digest with `CESR` produces:

```
E8wYuBjhslETYaLZcxMkWrhVbMcA8RS1pKYl7nJ77ntA
```

Replacing the placeholder with that `SAID` produces the final serialization:

```
field0______E8wYuBjhslETYaLZcxMkWrhVbMcA8RS1pKYl7nJ77ntA______
```

Verification reverses these steps.

## Serialization Generation

### Deterministic In-Memory Representations

The crucial consideration in `SAID` generation is reproducibility across the wire-to-memory-to-wire round trip. The digest input is a byte sequence received from, or prepared for, a deterministic wire format. Decoding those bytes produces an in-memory representation that retains every distinction needed to reconstruct the same serialization.

A deterministic in-memory representation preserves field order when it affects the wire format, exact value types, numeric representation rules, string contents, optional-field presence, tags, and application normalization choices. Re-encoding under the same deterministic profile produces identical bytes. The digest covers those reproduced wire bytes, not an implementation-specific memory layout.

Suitable realizations include an insertion-ordered mapping such as a Python 3.7 or later dictionary paired with a fixed `JSON` serialization profile, deterministic `CBOR` as described by [RFC8949], and ASN.1 values encoded with `DER` under ITU-T [X690]. These are examples rather than prerequisites. Any representation works when decoding preserves the information needed for deterministic re-encoding and independent implementations reproduce the same bytes.

When mapping order affects the wire format, the in-memory representation preserves that order. A profile can retain application-defined insertion order, sort keys, or apply schema-defined component ordering. Encoders and decoders apply the selected rule consistently.

Programming-language mappings have not always preserved insertion order. If a native mapping lacks a stable ordering contract, an ordered mapping, schema-defined record, or explicit canonical sorting step establishes reproducibility.

## Example Python dict to JSON Serialization with SAID

Suppose the initial value of a Python `dict` is as follows:

```python
{
    "said": "",
    "first": "Sue",
    "last": "Smith",
    "role": "Founder"
}
```

As before, the `SAID` will be a 44-character CESR-encoded Blake3-256 digest. The serialization will be `JSON`. The `said` field value in the `dict` is to be populated with the resulting `SAID`. First the value of the `said` field is replaced with a 44-character dummy string:

```python
{
    "said": "############################################",
    "first": "Sue",
    "last": "Smith",
    "role": "Founder"
}
```

The `dict` is then serialized into JSON with no extra whitespace:

```json
{"said":"############################################","first":"Sue","last":"Smith","role":"Founder"}
```

The Blake3-256 digest is computed on that serialization and encoded in `CESR` to provide the `SAID`:

```
EnKa0ALimLL8eQdZGzglJG_SxvncxkmvwFDhIyLFchUk
```

The value of the `said` field is replaced with the computed and encoded `SAID`:

```json
{"said":"EnKa0ALimLL8eQdZGzglJG_SxvncxkmvwFDhIyLFchUk","first":"Sue","last":"Smith","role":"Founder"}
```

The final serialization may be converted to a Python `dict` by deserializing the JSON:

```python
{
    "said": "EnKa0ALimLL8eQdZGzglJG_SxvncxkmvwFDhIyLFchUk",
    "first": "Sue",
    "last": "Smith",
    "role": "Founder"
}
```

The generation steps may be reversed to verify the embedded `SAID`. The protocol for mappings assumes the fields in the serialization are ordered in stable, round-trippable, reproducible order, i.e., canonical. The natural canonical ordering is called `field insertion order`.

## Example Ordered Mapping to JSON Serialization with SAID

The following example shows the serialized `JSON` form of the deterministic, insertion-ordered Python `dict` above. The same derivation applies to any in-memory representation that preserves the specified field order and value types.

```json
{"said":"","first":"Sue","last":"Smith","role":"Founder"}
```

Replace "said" with a 44-character placeholder and serialize without extra whitespace:

```json
{"said":"############################################","first":"Sue","last":"Smith","role":"Founder"}
```

`Blake3-256` over those `JSON` bytes, encoded with `CESR`, produces EnKa0ALimLL8eQdZGzglJG_SxvncxkmvwFDhIyLFchUk. Replacing the placeholder produces:

```json
{"said":"EnKa0ALimLL8eQdZGzglJG_SxvncxkmvwFDhIyLFchUk","first":"Sue","last":"Smith","role":"Founder"}
```

Verification restores the placeholder, reproduces the same `JSON` bytes, and recomputes the `SAID`.

## Example Schema Immutability Using JSON Schema with SAIDs

A `JSON` Schema can use the same derivation procedure to give its "$id" field a self-referential, cryptographically bound identifier. The placeholder serialization is:

```json
{"$id":"############################################","$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"full_name":{"type":"string"}}}
```

Digesting that serialization produces EZT9Idj7zLA0Ek6o8oevixdX20607CljNg4zrf_NQINY. Replacing the placeholder yields:

```json
{"$id":"EZT9Idj7zLA0Ek6o8oevixdX20607CljNg4zrf_NQINY","$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"full_name":{"type":"string"}}}
```

Data structures using embedded `SAIDs` in this way are referred to as self-addressing data (SAD).

## Discussion

A recognized derivation code identifies how to verify the binding between a `SAID` and its serialization. A valid `SAID` confirms that the serialization reproduces the bytes used during derivation; a mutation produces a different identifier. References to other serializations by `SAID` support compact, tamper-evident composition without embedding the referenced content in full.

# Realizing SAID-Like Properties with CESR, COSE, and JOSE

The properties provided by a `SAID` can be realized through multiple representation and security frameworks. Each realization requires a deterministic mapping from an application data model to bytes, an unambiguous indication of the digest algorithm and digest value, and verification rules that bind those bytes to the identifier. The following subsections distinguish the native `CESR` construction from profiles based on `COSE`/`CBOR` and `JOSE`/`JSON`.

## CESR Realization

The `CESR` realization defined by this document embeds the encoded digest in the serialization itself. Its derivation code identifies the digest algorithm and encoding, while the dummy-value procedure resolves the otherwise circular dependency created by hashing content that contains its own identifier. This construction is both content-addressing and self-referential: the identifier is a field of the exact serialization to which it is cryptographically bound.

The primary expression of a `CESR` primitive is textual and uses Base64 URL-safe characters. CESR primitives can be round-tripped to a compact binary representation without loss. The derivation code enables digest algorithm agility by identifying the algorithm used for each `SAID`. `CESR` was developed for the [KERI] protocol.

## COSE/CBOR Realization

[RFC9995] defines `COSE` hash envelopes by adding protected-header parameters that identify the payload hash algorithm, the media type or content format of the preimage, and optionally a location from which the preimage can be retrieved. A `SAID`-like profile can use these parameters as follows:

1. Encode the application data using a specified deterministic `CBOR` profile consistent with Section 4.2 of [RFC8949]. The application profile needs to resolve every representation choice that could otherwise produce different byte strings for equivalent data.

2. Compute the selected cryptographic digest over those deterministic `CBOR` bytes. The digest functions as the content-addressable identifier for that byte representation.

3. Construct an [RFC9995] hash envelope whose payload is the digest and whose protected header identifies the payload hash algorithm. The preimage content type and location parameters can be supplied when needed for interpretation or discovery.

4. Apply a `COSE` signature or MAC to the hash envelope. A verifier can validate the `COSE` protection over the envelope and its digest without access to the detached preimage. When the application data is available, the verifier deterministically encodes it under the same application profile, recomputes the digest, and compares the result with the envelope payload.

This construction provides deterministic content addressing and a cryptographic commitment to detached content. Unlike the `CESR` construction, it does not by itself make the digest a field of the hashed application structure. It is therefore `SAID`-like rather than natively self-referential unless an application profile additionally defines an embedded digest field and a deterministic placeholder or exclusion rule.

### CDDL Example

The ordered-mapping example in Section 2.3 can be represented as a deterministic `CBOR` map. The following `CDDL` describes the application data before derivation, with the `SAID` field represented by the digest bytes that identify the deterministic encoding of the placeholder form:

```cddl
said-example = {
"said"  => bstr .size 32,
"first" => "Sue",
"last"  => "Smith",
"role"  => "Founder"
}
```

For derivation, the value of "said" is replaced by a 32-byte placeholder, and the resulting map is encoded using the selected deterministic `CBOR` profile. `SHA-256` over those bytes yields a 32-byte digest. The digest can then be carried as the [RFC9995] hash-envelope payload:

```cddl
said-hash-envelope = #6.18([
protected   : bstr .cbor {
1   => int,
258 => int,
259 => "application/cbor"
},
unprotected : {},
payload     : bstr .size 32,
signature   : bstr
])
```

Header parameter 1 identifies the `COSE` signature algorithm, parameter 258 identifies the hash algorithm used to produce the payload, and parameter 259 identifies the preimage content type. The payload is the digest of the deterministic `CBOR` encoding of the placeholder form of said-example. Verification obtains the application data, restores the placeholder, deterministically re-encodes the map, recomputes the digest, and compares it with the envelope payload before or in conjunction with validating the `COSE` protection.

## JOSE/JSON Realization

`JOSE` provides `JSON`-based signature and MAC containers through `JWS` as defined by [RFC7515]. Because `JSON` permits multiple textual representations of the same data model, a `SAID`-like `JOSE` profile first specifies an invariant byte representation. [RFC8785] `JSON` Canonicalization Scheme (`JCS`) is one suitable profile: it constrains input to `I-JSON`, serializes primitives consistently, sorts object properties deterministically, and emits UTF-8.

A `JOSE` realization can proceed as follows:

1. Canonicalize the application `JSON` using `JCS` or another explicitly identified deterministic `JSON` profile.

2. Compute a cryptographic digest over the resulting canonical UTF-8 bytes and encode the digest using an unambiguous base64url representation. The digest algorithm and canonicalization profile are fixed by the application profile or carried in protected parameters that verifiers are required to understand.

3. Place the base64url-encoded digest in a profiled protected-header parameter and list that parameter in "crit" so that a verifier recognizes the hash-envelope processing rules. Omit the `JWS` payload from the `JSON` serialization. The signature covers the protected header containing the digest; the detached application data is used only to recompute and compare that digest.

4. A verifier validates the `JWS` protected header and signature, obtains the application data separately, restores any defined placeholder, canonicalizes the `JSON` under the identified profile, recomputes the digest, and compares it with the digest carried in the protected header.

`JOSE` does not currently register a general-purpose hash-envelope digest header equivalent to [RFC9995]. The example below therefore uses illustrative profiled parameter names. A closed profile can define private names, while interoperable deployment calls for registered or collision-resistant names and explicit critical-parameter processing. As with the `COSE` profile, the result provides deterministic content addressing and cryptographic commitment but becomes natively self-referential only when the application profile defines an embedded identifier field and placeholder or exclusion rule.

### JSON Example

The application data is the same structure used in Section 2.3:

```json
{
"said": "",
"first": "Sue",
"last": "Smith",
"role": "Founder"
}
```

After replacing "said" with the profile-defined placeholder, the structure is canonicalized with `JCS` and hashed with `SHA-256`. The digest is base64url encoded and placed in the protected header. The following flattened `JWS` `JSON` serialization illustrates the envelope before base64url encoding of the protected header:

```json
{
"protected": {
"alg": "ES256",
"crit": ["payload-digest", "payload-digest-alg",
"payload-canonicalization"],
"payload-digest": "<base64url(SHA-256(JCS(placeholder-form)))>",
"payload-digest-alg": "sha-256",
"payload-canonicalization": "jcs",
"cty": "application/json"
},
"signature": "<base64url(signature)>"
}
```

In an actual `JWS` `JSON` serialization, "protected" is the base64url encoding of the UTF-8 `JSON` protected-header object, not the object shown inline above. The top-level "payload" member is absent. A verifier decodes and validates the protected header, obtains the application data out of band, reconstructs the placeholder form, applies `JCS`, recomputes `SHA-256`, and compares the result with "payload-digest". The names beginning with "payload-" are illustrative profile parameters and are not registered `JOSE` header parameters.

## Common Requirements and Distinctions

All three realizations depend on collision-resistant digests, deterministic serialization, explicit algorithm identification, and exact verification rules. `CESR` integrates these elements into an identifier designed for self-reference. `COSE` with [RFC9995] standardizes a signed or MAC-protected hash envelope for `CBOR`-oriented systems. `JOSE` can provide analogous behavior for `JSON`-oriented systems when combined with deterministic `JSON` canonicalization and a defined digest-envelope profile. Implementations do not treat semantic equivalence after parsing as sufficient; verification is performed over the exact deterministic byte representation prescribed by the applicable profile.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Security Considerations

Security depends on the collision resistance and second-preimage resistance of the selected digest algorithm and on consistent implementation of the applicable deterministic serialization profile. A verifier that uses different field ordering, type conversion, normalization, placeholder, or exclusion rules can compute a different digest from the producer. Profiles therefore need to identify the digest algorithm, deterministic encoding rules, placeholder or exclusion procedure, and protected metadata needed to interpret the digest. Implementations should reject unsupported algorithms and profiles, malformed or ambiguous serializations, duplicate map keys or object member names, and protected parameters they do not understand. A valid digest demonstrates integrity of the identified bytes; it does not by itself establish authorship, authorization, freshness, confidentiality, or trustworthiness. Those properties require the surrounding signature, MAC, key-management, and application trust model.

# IANA Considerations

This document has no IANA actions.

# Appendix: Embedding SAIDs in URLs

A `SAID` can serve as a stable content identifier while discovery information is maintained separately. An application can include the compact `SAID` in a protocol message or data structure, then use DNS-based discovery to locate a URI for a service or server from which the detached payload can be retrieved. After retrieval, the application verifies the payload against the `SAID`.

Separating integrity from discovery reduces message and data-structure size while retaining a cryptographic commitment to the referenced content. The `SAID` identifies the content; DNS and the resolved URI identify a current retrieval location. A change to that location for administrative reasons, such as a company domain-name change or service migration, does not alter the content bytes and therefore does not invalidate existing commitments to the `SAID`.

The KERI community refers to this discovery pattern as an Out-of-Band Introduction (`OOBI`). An `OOBI` associates a stable identifier with information that helps a client discover the current endpoint or resources needed to interact with the identified entity or retrieve identified content.

# Appendix: JSON Schema with SAIDs

This appendix will define normative rules for using `SAIDs` to make JSON Schema immutable and prevent schema malleability attacks.

--- back

# Acknowledgments
{:numbered="false"}

Members of the KERIpy development team and the ToIP ACDC Working Group.
