import cocotb

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def set_control(dut, sensitivity=1, reset_n=1):

    value = 0

    # uio[1:0] = sensitivity
    value |= sensitivity & 0x3

    # uio[2] = reset_n
    value |= (reset_n & 0x1) << 2

    dut.uio_in.value = value


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await ClockCycles(dut.clk, 1)

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
        f"ACTIVITY={activity}"
    )

    return output, update, hold, activity


@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info("VITAL-AP TEST START")


    # ---------------------------------------------------------
    # Clock
    # ---------------------------------------------------------

    cocotb.start_soon(
        Clock(
            dut.clk,
            10,
            unit="ns"
        ).start()
    )


    dut.ena.value = 1

    dut.ui_in.value = 0

    set_control(
        dut,
        sensitivity=1,
        reset_n=0
    )

    await ClockCycles(dut.clk, 3)


    # ---------------------------------------------------------
    # Release reset
    # ---------------------------------------------------------

    set_control(
        dut,
        sensitivity=1,
        reset_n=1
    )

    await ClockCycles(dut.clk, 1)


    # ---------------------------------------------------------
    # TEST 1
    # First pixel
    # ---------------------------------------------------------

    dut._log.info("TEST 1: FIRST PIXEL")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"Expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 2
    # Static pixel
    # ---------------------------------------------------------

    dut._log.info("TEST 2: STATIC PIXEL")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"Expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 3
    # Large transition
    # ---------------------------------------------------------

    dut._log.info("TEST 3: LARGE TRANSITION")

    output, update, hold, activity = \
        await apply_pixel(dut, 200)

    assert output == 200, \
        f"Expected 200, got {output}"


    # ---------------------------------------------------------
    # TEST 4
    # Reverse transition
    # ---------------------------------------------------------

    dut._log.info("TEST 4: REVERSE TRANSITION")

    output, update, hold, activity = \
        await apply_pixel(dut, 20)

    assert output == 20, \
        f"Expected 20, got {output}"


    # ---------------------------------------------------------
    # TEST 5
    # Small change
    # ---------------------------------------------------------

    dut._log.info("TEST 5: SMALL CHANGE")

    output, update, hold, activity = \
        await apply_pixel(dut, 21)

    dut._log.info(
        f"Small change result = {output}"
    )


    # ---------------------------------------------------------
    # TEST 6
    # Disable
    # ---------------------------------------------------------

    dut._log.info("TEST 6: DISABLE")

    dut.ena.value = 0

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    assert output == 21 or output == 20, \
        f"Output changed while disabled: {output}"


    # ---------------------------------------------------------
    # TEST 7
    # Re-enable
    # ---------------------------------------------------------

    dut._log.info("TEST 7: RE-ENABLE")

    dut.ena.value = 1

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    dut._log.info(
        f"Re-enabled output = {output}"
    )


    dut._log.info("================================")
    dut._log.info("VITAL-AP TEST PASSED")
    dut._log.info("================================")
