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

normative:  

informative:  
  KERI:
    title: Key Event Receipt Infrastructure (KERI)
    author:
        ins: S. Smith
        name: Samuel M. Smith
        org: ProSapien LLC
    date: 2019,2020,2021


tags: IETF, SAID, ACDC

--- abstract 

A SAID (Self-Addressing IDentifier) is a special type of content addressable identifier based on encoded cryptographic digest that is self-referential. The SAID derivation protocol defined herein enables verification that a given SAID is uniquely cryptographically bound to a serialization that includes the SAID as a field in that serialization. Embedding a SAID as a field in the associated serialization indicates a preferred content addressable identifier for that serialization that facilitates greater interoperability, reduced ambiguity, and enhanced security when reasoning about the serialization. Moreover given sufficient cryptographic strength, a cryptographic commitment such as a signature, digest, or another SAID, to a given SAID is essentially equivalent to a commitment to its associated serialization. Any change to the serialization invalidates its SAID thereby ensuring secure immutability evident reasoning with SAIDS about serializations or equivalently their SAIDs. Thus SAIDs better facilitate immutably referenced data serializations for applications such as Verifiable Credentials or Ricardian Contracts. 

SAIDs are encoded with CESR (Composable Event Streaming Representation) which includes a pre-pended derivation code that encodes the cryptographic suite or algorithm used to generate the digest. CESR primitives alone or in combination primary expression is textual using Base64 URL Safe characters but may be round-tripped alone or in combination to a more compact binary representation without loss. The CESR derivation code enables cryptographic digest algorithm agility in systems that use SAIDs as content addresses. Each serialization may use a different cryptographic digest algorithm as indicated by its derivation code. This provides interoperable future proofing.



--- middle 

# Introduction

The primary advantage of a content-addressable identifier is that it is cryptographically bound to the content (expressed as a serialization), thus providing a secure root-of-trust for reasoning about that content. Any sufficiently strong cryptographic commitment to a content-addressable identifier is functionally equivalent to a cryptographic commitment to the content itself. 

A `self-addressing identifier (SAID)` is a special class of content-addressable identifier that is also self-referential. This requires a special derivation protocol that generates the `SAID` and embeds it in the serialized content.  The reason for a special derivation protocol is that a naive cryptographic content-addressable identifier must not be self-referential, i.e. the identifier must not appear within the content that it is identifying. This is because the naive cryptographic derivation process of a content-addressable identifier is a cryptographic digest of the serialized content. Changing one bit of the serialization content will result in a different digest. Therefore, self-referential content-addressable identifiers require a special derivation protocol. 

To elaborate, this approach of deriving self-referential identifiers from the contents they identify, is called `self-addressing`. It allows any validator to verify or re-derive the self-referential, self-addressing identifier given the contents it identifies. To clarify, a `SAID` is different from a standard content address or content-addressable identifier in that a standard content-addressable identifier may not be included inside the contents it addresses. Moreover, a standard content-addressable identifier is computed on the finished immutable contents, and therefore is not self-referential. In addition a `self-addressing identifier (SAID)` includes a pre-pended derivation code that specifies the cryptographic algorithm used to generate the digest.  

An authenticatable data serialization is defined to be a serialization that is digitally signed with a non-repudiable asymmetric key-pair based signing scheme. A verifier, given the public key, may verify the signature on the serialization and thereby securely attribute the serialization to the signer. Many use cases of authenticatable data serializations or statements include a self-referential identifier embedded in the authenticatible serialization. These serializations may also embed references to other self-referential identifiers to other serializations. The purpose of a self-referential identifier is enable reasoning in software or otherwise about that serialization.  Typically these self-referential identifiers are not cryptographically bound to their encompassing serializations such as would be the case for a content-addressable identifier of that serialization. This poses a security problem because there now may be more that one identifer for the same content. The first is self-referential, included in the serialization, but not cryptographically bound to its encompassing serialization and the second is cryptographically bound but not self-referential, not included in the serialization. 

When reasoning about a given content serialization, the existence of a non-cryptographically bound but self-referential identifier is a security vulnerability. Certainly this identifier can not be used by itself to securely reason about the content because it is not bound to the content. Anyone can place such an identifier inside a some other serialization and claim that the other serialization is the correct serialization for that self-referential identifier.  Unfortunately, a standard content addressable identifier for a serialization which is bound to the serialization can not be included in the serialization itself, i.e. can not be self-referential nor self-containe. It must be tracked independently. In contrast, a _self-addressing_ identifier is included in the serialization to which it is cryptographically bound making it self-referential and self-contained. Reasoning about *self-addressing identifiers* (SAIDs)is secure because the SAID will only verify if and only if its encompassing serialization has not been mutated (i.e. is immutable). Self-addressing identifiers used as references to serializations in other serialization enable tamper evident reasoning about the referenced serializations. This enables a more compact representation of an authenticatable data serialization that includes other serializations by reference to their SAIDs instead of by embedded containment.

# Generation and Verification Protocols

The *self-addressing identifier* (SAID) generation protocol is as follows:

- Insert a dummy string of the same length as the eventually derived and CESR encoded SAID into the SAID field of a serialization. The dummy character is `#`, that is, ASCII 35 decimal (23 hex).
- Compute the digest of the serialization with the dummy value in the SAID field.
- Encode the computed digest with CESR (text fully qualified Base64) to create the final derived and encoded SAID of the same total length as the dummy string. This includes the derivation code for the digest algorithm used to compute the digest.
- Replace the dummy string in the serialization with the encoded SAID string.

The *self-addressing identifier* (SAID) verification protocol is as follows:

- Make a copy of the embedded CESR encoded SAID string included in the serialization.
- replace the SAID field value in the serialization with a dummy string of the same length. The dummy character is `#`, that is, ASCII 35 decimal (23 hex).
- Compute the digest of the serialization that includes the dummy value for the SAID field. Use the digest algorithm specified by the CESR derivation code of the copied SAID.
- Encode the computed digest with CESR (text fully qualified Base64) to create the final derived and encoded SAID of the same total length as the dummy string and the copied embedded SAID.
- Compare the copied SAID with the recomputed SAID. If they are identical then the verification is successful; otherwise unsuccessful.


## Example Computation




## Serialization Generation

Insertion Order Preserving

The `SAID` derivation protocol assumes that the fields in a JSON serialization are ordered in stable, round-trippable, reproducible order, i.e., canonical. The natural canonical ordering for JSON is called `property creation order` or `field insertion order`. This logical ordering has been supported by the `stringify()` method in JavaScript with a custom reordering function using Reflect.ownPropertyKeys() since ES6, and natively without a reordering function by `stringify()` since ES11 (2020). Property creation order is a natural canonicalization, as it supports any predefined logical ordering that one chooses by creating or inserting the properties (fields) in that predefined order. Other languages have long supported ordered dictionaries or mappings that support insertion order of the fields when serializing the mapping to/from JSON. ***The canonical serialization problem for JSON is now a solved problem.***  

As long as any verifier recognizes the derivation code, the `SAID` is a cryptographically secure commitment to the contents in which it is embedded; it is a cryptographically verifiable, self-referential, content-addressable identifier. Because an `SAID` is both self-referential and cryptographically bound to the contents it identifies, anyone can validate this binding if they follow the _derivation protocol_ outlined above.


To elaborate, this approach of deriving self-referential identifiers from the contents they identify, is called `self-addressing`. It allows any validator to verify or re-derive the self-referential, self-addressing identifier given the contents it identifies. To clarify, a `SAID` is different from a standard content address or content-addressable identifier in that a standard content-addressable identifier may not be included inside the contents it addresses. Moreover, a standard content-addressable identifier is computed on the finished immutable contents, and therefore is not self-referential.  


# Conventions and Definitions

{::boilerplate bcp14-tagged}


# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
