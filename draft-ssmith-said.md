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


--- abstract

TODO Abstract


--- middle

# Introduction

The advantage of a content-addressable identifier is that it is cryptographically bound to the contents, providing a secure root of trust. Any cryptographic commitment to a content-addressable identifier is functionally equivalent (given comparable cryptographic strength) to a cryptographic commitment to the content itself. 

A `self-addressing identifier (SAID)` is a special class of content-addressable identifier that is also self-referential. The special class is distinguished by a special derivation method or process to generate the `SAID`. This derivation method is determined by the combination of both a derivation code prefix included in the identifier and the context in which the identifier appears. The reason for a special derivation method is that a naive cryptographic content-addressable identifier must not be self-referential, i.e. the identifier must not appear within the content that it is identifying. This is because the naive cryptographic derivation process of a content-addressable identifier is a cryptographic digest of the serialized content. Changing one bit of the serialization content will result in a different digest. Therefore, self-referential content-addressable identifiers require a special derivation protocol, method, or process. 

The `SAID` derivation protocol assumes that the fields in a JSON serialization are ordered in stable, round-trippable, reproducible order, i.e., canonical. The natural canonical ordering for JSON is called `property creation order` or `field insertion order`. This logical ordering has been supported by the `stringify()` method in JavaScript with a custom reordering function using Reflect.ownPropertyKeys() since ES6, and natively without a reordering function by `stringify()` since ES11 (2020). Property creation order is a natural canonicalization, as it supports any predefined logical ordering that one chooses by creating or inserting the properties (fields) in that predefined order. Other languages have long supported ordered dictionaries or mappings that support insertion order of the fields when serializing the mapping to/from JSON. ***The canonical serialization problem for JSON is now a solved problem.***  

The self-addressing identifier derivation process is as follows:

- replace the value of the `id` field in the content that will hold the self-addressing identifier with a dummy string of the same length as the eventually derived self-addressing identifier
- compute the digest of the content with the dummy value for the `id` field
- prepend the derivation code to the digest and encode appropriately to create the final derived self-addressing identifier of the same total length including the prepended code as the dummy.
- replace the dummy with the self-addressing identifier

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
