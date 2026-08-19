SIM ?= icarus

TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = project.v

VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

VERILOG_SOURCES += $(PWD)/tb.v

COMPILE_ARGS += -I$(SRC_DIR)

TOPLEVEL = tb

MODULE = test

include $(shell cocotb-config --makefiles)/Makefile.sim
