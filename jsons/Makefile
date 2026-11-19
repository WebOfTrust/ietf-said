.DEFAULT_GOAL := stream

include frags.mk

SAID_JSON_AUTOGEN := said-autogen.schema.json
SAID_JSON_EXPORT := ../exports/said.schema.json
PYTHON ?= python3

.PHONY: stream clean

stream: $(SAID_JSON_AUTOGEN) $(SAID_JSON_EXPORT)

$(SAID_JSON_AUTOGEN): frags.mk $(SAID_JSON_FRAGS) stream.py
	$(PYTHON) stream.py $@ $(SAID_JSON_FRAGS)

$(SAID_JSON_EXPORT): $(SAID_JSON_AUTOGEN)
	mkdir -p ../exports
	cp $(SAID_JSON_AUTOGEN) $(SAID_JSON_EXPORT)

clean:
	$(RM) $(SAID_JSON_AUTOGEN) $(SAID_JSON_AUTOGEN).tmp
