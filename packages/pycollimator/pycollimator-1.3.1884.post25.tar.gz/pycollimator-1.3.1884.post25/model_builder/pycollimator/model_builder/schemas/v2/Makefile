# Makefile for generating JSON schemas from TypeScript interfaces
#
# Feel free to use a different scripting than Makefile, but this
# is more efficient than bash and bazel just does't work well for
# the purpose of generating files in repo.
# Maybe scons, ninja, meson, please, ...?
# Simplicity matters and nothing else.

# All TS files are source schemas
SOURCE_TS=$(wildcard *.ts)

TS_TO_SCHEMA=npx --yes typescript-json-schema@0.55.0 --yes --aliasRefs --required
SCHEMA_TO_GO=npx --yes quicktype@v23.0.19 -s schema -l go --no-maps --no-combine-classes
GO_PACKAGE=schemas

GITDIR=$(shell echo $${GITDIR:-`git rev-parse --show-toplevel`})

SCHEMAS_DIR=generated
GO_DIR=$(GITDIR)/src/services/goapi/pkg/schemas
GO_API_DIR=$(GITDIR)/src/services/goapi/api
GEN_DIRS=$(SCHEMAS_DIR) $(GO_DIR)

SCHEMAS=$(SOURCE_TS:%.ts=$(SCHEMAS_DIR)/%.schema.json)
GO_FILES=$(SOURCE_TS:%.ts=$(GO_DIR)/%.go)
GO_API_FILES=$(SOURCE_TS:%.ts=$(GO_API_DIR)/%.schema.json)

all: $(GEN_DIRS) $(SCHEMAS) $(GO_FILES) $(GO_API_FILES)

touch:
	@touch $(SOURCE_TS)

$(SCHEMAS_DIR):
	mkdir -p $@

$(GO_DIR):
	mkdir -p $@

$(SCHEMAS_DIR)/%.schema.json: %.ts
	$(eval TYPE_NAME := $(shell head -n1 $< | sed -e 's/\/\/ //'))
	@echo "  GEN   $(shell basename $@)"
	@echo "        ↳ $(TYPE_NAME)"
	@chmod +w $@ 2>> /dev/null || true
	@$(TS_TO_SCHEMA) $< $(TYPE_NAME) -o $@
	@$(GITDIR)/src/scripts/fix_eof.sh "$@"
	@chmod -w $@

$(GO_API_DIR)/%.schema.json: $(SCHEMAS_DIR)/%.schema.json %.ts
	@echo "  COPY  $(shell basename $@)"
	@chmod +w $@ 2>> /dev/null || true
	@cp -f $< $@
	@chmod -w $@

# Note: there is no way to generate the correct Go/XML definitions, since
# the TS definition just doesn't even have enough context to begin with.
# See: zipfmu.go
$(GO_DIR)/%.go: $(SCHEMAS_DIR)/%.schema.json
	$(eval TSFILE := $(shell basename $(patsubst %.schema.json,%.ts,$<)))
	$(eval TYPE_NAME := $(shell head -n1 $(TSFILE) | sed -e 's/\/\/ //'))
	@echo "  GEN   $(shell basename $@)"
	@echo "        ↳ $(TYPE_NAME)"
	@chmod +w $@ 2>> /dev/null || true
	@$(SCHEMA_TO_GO) --package $(GO_PACKAGE) --top-level $(TYPE_NAME) -o $@ $<
	@gofmt -w $@
	@chmod -w $@
