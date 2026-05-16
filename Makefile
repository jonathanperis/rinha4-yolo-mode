AS ?= as
LD ?= ld
BUILD_DIR := build
ASFLAGS ?= --64
LDFLAGS ?= -nostdlib -static

API_SRC := src/api/main.S
LB_SRC := src/lb/main.S

.PHONY: all api lb test smoke smoke-api smoke-lb smoke-stack corpus-replay clean

CORPUS_JSON ?= ../rinha-de-backend-2026/test/test-data.json

all: api lb

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

api: $(BUILD_DIR)/api
lb: $(BUILD_DIR)/lb

$(BUILD_DIR)/api.o: $(API_SRC) | $(BUILD_DIR)
	$(AS) $(ASFLAGS) $< -o $@

$(BUILD_DIR)/lb.o: $(LB_SRC) | $(BUILD_DIR)
	$(AS) $(ASFLAGS) $< -o $@

$(BUILD_DIR)/api: $(BUILD_DIR)/api.o
	$(LD) $(LDFLAGS) $< -o $@

$(BUILD_DIR)/lb: $(BUILD_DIR)/lb.o
	$(LD) $(LDFLAGS) $< -o $@

smoke: smoke-api smoke-lb smoke-stack

smoke-api: api
	python3 tests/smoke_api.py ./$(BUILD_DIR)/api

smoke-lb: lb
	python3 tests/smoke_lb_fdpass.py ./$(BUILD_DIR)/lb

smoke-stack: api lb
	python3 tests/smoke_full_fdpass_stack.py ./$(BUILD_DIR)/api ./$(BUILD_DIR)/lb

test: all smoke
	python3 tests/check_purity.py

corpus-replay: api
	python3 tests/corpus_replay.py ./$(BUILD_DIR)/api $(CORPUS_JSON)

clean:
	rm -rf $(BUILD_DIR)
