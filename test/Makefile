SIM ?= icarus

TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = project.v

# ------------------------------------------------------------
# RTL source
# ------------------------------------------------------------

VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

COMPILE_ARGS += -I$(SRC_DIR)

# ------------------------------------------------------------
# Testbench
# ------------------------------------------------------------

VERILOG_SOURCES += $(PWD)/tb.v

TOPLEVEL = tb

MODULE = test

# ------------------------------------------------------------
# Cocotb
# ------------------------------------------------------------

include $(shell cocotb-config --makefiles)/Makefile.sim
