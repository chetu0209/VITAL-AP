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


def set_control(dut, sensitivity=1, reset_n=1):

    value = 0

    # uio[1:0] = sensitivity
    value |= sensitivity & 0x3

    # uio[2] = reset_n
    value |= (reset_n & 0x1) << 2

    dut.uio_in.value = value


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await clock_cycle(dut)

    output = int(dut.uo_out.value)

    status = int(dut.uio_out.value)

    update = (status >> 3) & 1
    hold = (status >> 4) & 1
    activity = (status >> 5) & 3

    print(
        f"INPUT={value:3d} "
        f"OUTPUT={output:3d} "
        f"UPDATE={update} "
        f"HOLD={hold} "
        f"ACTIVITY={activity:02b}"
    )

    return output, update, hold, activity


@cocotb.test()
async def test_vital_ap(dut):

    print("========================================")
    print("        VITAL-AP TEST START")
    print("========================================")


    # ---------------------------------------------------------
    # INITIAL VALUES
    # ---------------------------------------------------------

    dut.clk.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0

    set_control(
        dut,
        sensitivity=1,
        reset_n=0
    )


    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    print("Applying reset...")

    await run_cycles(dut, 3)


    # ---------------------------------------------------------
    # RELEASE RESET
    # ---------------------------------------------------------

    set_control(
        dut,
        sensitivity=1,
        reset_n=1
    )

    await run_cycles(dut, 1)

    print("Reset released")


    # ---------------------------------------------------------
    # TEST 1
    # FIRST PIXEL
    # ---------------------------------------------------------

    print("TEST 1: First pixel")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"First pixel failed: expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 2
    # STATIC IMAGE
    # ---------------------------------------------------------

    print("TEST 2: Static image")

    output, update, hold, activity = \
        await apply_pixel(dut, 100)

    assert output == 100, \
        f"Static pixel failed: expected 100, got {output}"


    # ---------------------------------------------------------
    # TEST 3
    # LARGE TRANSITION
    # ---------------------------------------------------------

    print("TEST 3: Large transition")

    output, update, hold, activity = \
        await apply_pixel(dut, 200)

    assert output == 200, \
        f"Large transition failed: expected 200, got {output}"


    # ---------------------------------------------------------
    # TEST 4
    # REVERSE TRANSITION
    # ---------------------------------------------------------

    print("TEST 4: Reverse transition")

    output, update, hold, activity = \
        await apply_pixel(dut, 20)

    assert output == 20, \
        f"Reverse transition failed: expected 20, got {output}"


    # ---------------------------------------------------------
    # TEST 5
    # SMALL CHANGE
    # ---------------------------------------------------------

    print("TEST 5: Small change")

    output, update, hold, activity = \
        await apply_pixel(dut, 21)

    print(
        f"Small change output = {output}"
    )


    # ---------------------------------------------------------
    # TEST 6
    # DISABLE
    # ---------------------------------------------------------

    print("TEST 6: Disable")

    dut.ena.value = 0

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    assert output != 250, \
        "Pixel changed while VITAL-AP was disabled"


    # ---------------------------------------------------------
    # TEST 7
    # RE-ENABLE
    # ---------------------------------------------------------

    print("TEST 7: Re-enable")

    dut.ena.value = 1

    output, update, hold, activity = \
        await apply_pixel(dut, 250)

    print(
        f"Re-enabled output = {output}"
    )


    # ---------------------------------------------------------
    # FINISH
    # ---------------------------------------------------------

    print("========================================")
    print("        VITAL-AP TEST PASSED")
    print("========================================")
