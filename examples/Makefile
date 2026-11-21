.DEFAULT_GOAL := check

PYTHON ?= python3
CDDL ?= cddl
CDDL_SCHEMA := ../exports/said.cddl
JSON_SCHEMA := ../exports/said.schema.json
CBOR_TEST_SCHEMA := cbor/said-cbor-test.cddl

.PHONY: check schemas generate clean

check: schemas generate $(CBOR_TEST_SCHEMA)
	cmp ../asn1/said.asn ../exports/said.asn
	$(CDDL) $(CDDL_SCHEMA) validate cesr/said-cesr-text.json cesr/said-blake2b-512-text.json json/said-json-alg-digest.json json/said-json-blake2b-512-alg-digest.json urn/said-urn-sha-256.json urn/said-urn-blake2b-512.json
	$(CDDL) $(CBOR_TEST_SCHEMA) validate cbor/said-cbor-alg-digest.cbor cbor/said-cbor-cesr.cbor cbor/said-cbor-blake2b-512-cesr.cbor
	$(PYTHON) validate-json.py $(JSON_SCHEMA) cesr/said-cesr-text.json cesr/said-blake2b-512-text.json json/said-json-alg-digest.json json/said-json-blake2b-512-alg-digest.json urn/said-urn-sha-256.json urn/said-urn-blake2b-512.json
	CDDL="$(CDDL)" $(PYTHON) test_der.py

$(CBOR_TEST_SCHEMA): $(CDDL_SCHEMA)
	@printf 'said-cbor-example = said-cbor\n' > $@.tmp
	@cat $(CDDL_SCHEMA) >> $@.tmp
	mv $@.tmp $@

schemas:
	$(MAKE) -C ../cddl stream
	$(MAKE) -C ../jsons stream
	$(MAKE) -C ../asn1 stream

generate:
	$(PYTHON) generate.py

clean:
	$(RM) cesr/said-cesr.cesr cesr/said-cesr-text.json json/said-json-alg-digest.json
	$(RM) cesr/said-blake2b-512.cesr cesr/said-blake2b-512-text.json
	$(RM) json/said-json-blake2b-512-alg-digest.json
	$(RM) urn/said-urn-sha-256.urn urn/said-urn-sha-256.json
	$(RM) urn/said-urn-blake2b-512.urn urn/said-urn-blake2b-512.json
	$(RM) cbor/said-cbor-alg-digest.diag cbor/said-cbor-alg-digest.cbor cbor/said-cbor-alg-digest.pretty
	$(RM) cbor/said-cbor-cesr.diag cbor/said-cbor-cesr.cbor cbor/said-cbor-cesr.pretty
	$(RM) cbor/said-cbor-blake2b-512-cesr.diag cbor/said-cbor-blake2b-512-cesr.cbor cbor/said-cbor-blake2b-512-cesr.pretty
	$(RM) $(CBOR_TEST_SCHEMA) $(CBOR_TEST_SCHEMA).tmp
