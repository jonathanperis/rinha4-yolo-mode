AS ?= as
LD ?= ld
BUILD_DIR := build
ASFLAGS ?= --64
LDFLAGS ?= -nostdlib -static

API_SRC := src/api/main.S
.PHONY: all api test smoke smoke-api smoke-fdpass clean


all: api

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

api: $(BUILD_DIR)/api

$(BUILD_DIR)/api.o: $(API_SRC) | $(BUILD_DIR)
	$(AS) $(ASFLAGS) $< -o $@

$(BUILD_DIR)/api: $(BUILD_DIR)/api.o
	$(LD) $(LDFLAGS) $< -o $@

smoke: smoke-api smoke-fdpass

smoke-api: api
	python3 tests/smoke_api.py ./$(BUILD_DIR)/api
	python3 tests/official_correctness_sample.py ./$(BUILD_DIR)/api

smoke-fdpass: api
	python3 tests/fdpass_keepalive.py ./$(BUILD_DIR)/api

test: smoke
	python3 tests/check_purity.py


clean:
	rm -rf $(BUILD_DIR)
