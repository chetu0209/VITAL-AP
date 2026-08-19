# Tiny Tapeout / cocotb test Makefile

SIM ?= icarus

TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = project.v

ifneq ($(GATES),yes)

# RTL simulation
SIM_BUILD = sim_build/rtl

VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

COMPILE_ARGS += -I$(SRC_DIR)

else

# Gate-level simulation
SIM_BUILD = sim_build/gl

COMPILE_ARGS += -DGL_TEST
COMPILE_ARGS += -DFUNCTIONAL
COMPILE_ARGS += -DSIM

VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v

# Verilog testbench top module
TOPLEVEL = tb

# Python test file
MODULE = test

# Cocotb
include $(shell cocotb-config --makefiles)/Makefile.sim
