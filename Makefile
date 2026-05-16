AS ?= as
LD ?= ld
BUILD_DIR := build
ASFLAGS ?= --64
LDFLAGS ?= -nostdlib -static

API_SRC := src/api/main.S
LB_SRC := src/lb/main.S

.PHONY: all api lb test smoke clean

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

smoke: api
	python3 tests/smoke_api.py ./$(BUILD_DIR)/api

test: all smoke
	python3 tests/check_purity.py

clean:
	rm -rf $(BUILD_DIR)
