.DEFAULT_GOAL := stream

include frags.mk

SAID_AUTOGEN := said-autogen.cddl
SAID_EXPORT := ../exports/said.cddl

.PHONY: stream clean

stream: $(SAID_AUTOGEN) $(SAID_EXPORT)

$(SAID_AUTOGEN): frags.mk $(SAID_FRAGS)
	@cat $(SAID_FRAGS) > $@.tmp
	mv $@.tmp $@

$(SAID_EXPORT): $(SAID_AUTOGEN)
	mkdir -p ../exports
	cp $(SAID_AUTOGEN) $(SAID_EXPORT)

clean:
	$(RM) $(SAID_AUTOGEN) $(SAID_AUTOGEN).tmp
