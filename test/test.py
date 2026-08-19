import cocotb
from cocotb.triggers import Timer


async def clock_cycle(dut):

    dut.clk.value = 0
    await Timer(5, units="ns")

    dut.clk.value = 1
    await Timer(5, units="ns")


async def run_cycles(dut, count):

    for _ in range(count):
        await clock_cycle(dut)


def set_sensitivity(dut, sensitivity):

    dut.uio_in.value = sensitivity & 0x3


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await clock_cycle(dut)

    output = int(dut.uo_out.value)

    status = int(dut.uio_out.value)

    update = (status >> 3) & 1
    hold = (status >> 4) & 1
    activity = (status >> 5) & 3

    dut._log.info(
        f"INPUT={value} "
        f"OUTPUT={output} "
        f"UPDATE={update} "
        f"HOLD={hold} "
        f"ACTIVITY={activity:02b}"
    )

    return output, update, hold, activity


@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info("================================")
    dut._log.info("      VITAL-AP TEST START")
    dut._log.info("================================")


    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    dut.clk.value = 0
    dut.rst_n.value = 0
    dut.ena.value = 0
    dut.ui_in.value = 0

    set_sensitivity(dut, 1)


    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    dut._log.info("Applying reset")

    await run_cycles(dut, 3)


    # ---------------------------------------------------------
    # RELEASE RESET
    # ---------------------------------------------------------

    dut.rst_n.value = 1
    dut.ena.value = 1

    await run_cycles(dut, 1)

    dut._log.info("Reset released")


    # ---------------------------------------------------------
    # TEST 1
    # ---------------------------------------------------------

    dut._log.info("TEST 1: First pixel")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"Expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 2
    # ---------------------------------------------------------

    dut._log.info("TEST 2: Static pixel")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"Expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 3
    # ---------------------------------------------------------

    dut._log.info("TEST 3: Large transition")

    output, update, hold, activity = \
        await apply_pixel(dut, 200)

    assert output == 200, \
        f"Expected 200, got {output}"


    # ---------------------------------------------------------
    # TEST 4
    # ---------------------------------------------------------

    dut._log.info("TEST 4: Reverse transition")

    output, update, hold, activity = \
        await apply_pixel(dut, 20)

    assert output == 20, \
        f"Expected 20, got {output}"


    # ---------------------------------------------------------
    # TEST 5
    # ---------------------------------------------------------

    dut._log.info("TEST 5: Small change")

    output, update, hold, activity = \
        await apply_pixel(dut, 21)

    dut._log.info(
        f"Small change output = {output}"
    )


    # ---------------------------------------------------------
    # TEST 6
    # ---------------------------------------------------------

    dut._log.info("TEST 6: Disable")

    dut.ena.value = 0

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    assert output != 250, \
        "Output changed while disabled"


    # ---------------------------------------------------------
    # TEST 7
    # ---------------------------------------------------------

    dut._log.info("TEST 7: Re-enable")

    dut.ena.value = 1

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    dut._log.info(
        f"Re-enabled output = {output}"
    )


    dut._log.info("================================")
    dut._log.info("      VITAL-AP TEST PASSED")
    dut._log.info("================================")
