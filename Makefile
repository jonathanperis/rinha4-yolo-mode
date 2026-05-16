AS ?= as
LD ?= ld
BUILD_DIR := build
ASFLAGS ?= --64
LDFLAGS ?= -nostdlib -static

API_SRC := src/api/main.S

.PHONY: all api test smoke smoke-api corpus-replay clean

CORPUS_JSON ?= ../rinha-de-backend-2026/test/test-data.json

all: api

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

api: $(BUILD_DIR)/api

$(BUILD_DIR)/api.o: $(API_SRC) | $(BUILD_DIR)
	$(AS) $(ASFLAGS) $< -o $@

$(BUILD_DIR)/api: $(BUILD_DIR)/api.o
	$(LD) $(LDFLAGS) $< -o $@

smoke: smoke-api

smoke-api: api
	python3 tests/smoke_api.py ./$(BUILD_DIR)/api

test: all smoke
	python3 tests/check_purity.py

corpus-replay: api
	python3 tests/corpus_replay.py ./$(BUILD_DIR)/api $(CORPUS_JSON)

clean:
	rm -rf $(BUILD_DIR)
