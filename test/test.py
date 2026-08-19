import cocotb

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


# ============================================================
# Configure VITAL-AP
# ============================================================

def set_control(
    dut,
    enable=1,
    sensitivity=1,
    reset_n=1
):

    # uio_in[0]   = ENABLE
    # uio_in[2:1] = SENSITIVITY
    # uio_in[7]   = RESET_N

    value = 0

    value |= (enable & 0x1)

    value |= ((sensitivity & 0x3) << 1)

    value |= ((reset_n & 0x1) << 7)

    dut.uio_in.value = value


# ============================================================
# Apply pixel
# ============================================================

async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await ClockCycles(
        dut.clk,
        1
    )

    output = int(
        dut.uo_out.value
    )

    status = int(
        dut.uio_out.value
    )

    update = status & 0x1

    hold = (status >> 1) & 0x1

    activity = (status >> 2) & 0x3

    dut._log.info(
        f"PIXEL={value:3d} | "
        f"OUTPUT={output:3d} | "
        f"UPDATE={update} | "
        f"HOLD={hold} | "
        f"ACTIVITY={activity:02b}"
    )

    return output, update, hold, activity


# ============================================================
# Main test
# ============================================================

@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info(
        "========================================"
    )

    dut._log.info(
        "       VITAL-AP TEST START"
    )

    dut._log.info(
        "========================================"
    )


    # ========================================================
    # Start clock
    # 10 ns period = 100 MHz simulation clock
    # ========================================================

    cocotb.start_soon(
        Clock(
            dut.clk,
            10,
            unit="ns"
        ).start()
    )


    # ========================================================
    # Initial state
    # ========================================================

    dut.ena.value = 1

    dut.ui_in.value = 0

    dut.uio_in.value = 0


    # ========================================================
    # Reset
    # ========================================================

    set_control(
        dut,
        enable=0,
        sensitivity=1,
        reset_n=0
    )

    await ClockCycles(
        dut.clk,
        3
    )


    # Release reset
    set_control(
        dut,
        enable=1,
        sensitivity=1,
        reset_n=1
    )


    # ========================================================
    # TEST 1
    # First pixel
    # ========================================================

    dut._log.info(
        "TEST 1: FIRST PIXEL"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            100
        )

    assert output == 100, \
        "First large pixel should be stored"

    assert update == 1, \
        "First large pixel should generate UPDATE"


    # ========================================================
    # TEST 2
    # Static image
    # ========================================================

    dut._log.info(
        "TEST 2: STATIC IMAGE"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            100
        )

    assert output == 100, \
        "Static pixel should remain unchanged"

    assert hold == 1, \
        "Static pixel should generate HOLD"


    output, update, hold, activity = \
        await apply_pixel(
            dut,
            100
        )

    assert output == 100, \
        "Static pixel should remain unchanged"


    # ========================================================
    # TEST 3
    # Small change
    # ========================================================

    dut._log.info(
        "TEST 3: SMALL PIXEL CHANGE"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            101
        )

    assert output == 100, \
        "Small change should be suppressed"


    # ========================================================
    # TEST 4
    # Medium change
    # ========================================================

    dut._log.info(
        "TEST 4: MEDIUM PIXEL CHANGE"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            105
        )

    assert output == 105, \
        "Medium change should update"


    assert update == 1, \
        "Medium change should generate UPDATE"


    # ========================================================
    # TEST 5
    # Large video transition
    # ========================================================

    dut._log.info(
        "TEST 5: LARGE VIDEO TRANSITION"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            200
        )

    assert output == 200, \
        "Large transition should update"


    output, update, hold, activity = \
        await apply_pixel(
            dut,
            20
        )

    assert output == 20, \
        "Large reverse transition should update"


    # ========================================================
    # TEST 6
    # Temporal fluctuation
    # ========================================================

    dut._log.info(
        "TEST 6: TEMPORAL FLUCTUATION"
    )

    await apply_pixel(
        dut,
        21
    )

    await apply_pixel(
        dut,
        20
    )

    await apply_pixel(
        dut,
        21
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            20
        )

    assert output == 20, \
        "Temporal fluctuation must not corrupt output"


    # ========================================================
    # TEST 7
    # High activity video
    # ========================================================

    dut._log.info(
        "TEST 7: HIGH ACTIVITY VIDEO"
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            200
        )

    assert output == 200


    output, update, hold, activity = \
        await apply_pixel(
            dut,
            30
        )

    assert output == 30


    output, update, hold, activity = \
        await apply_pixel(
            dut,
            220
        )

    assert output == 220


    # ========================================================
    # TEST 8
    # Disable
    # ========================================================

    dut._log.info(
        "TEST 8: DISABLE"
    )

    set_control(
        dut,
        enable=0,
        sensitivity=1,
        reset_n=1
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            255
        )

    assert output == 220, \
        "Output must hold while disabled"


    # ========================================================
    # TEST 9
    # Re-enable
    # ========================================================

    dut._log.info(
        "TEST 9: RE-ENABLE"
    )

    set_control(
        dut,
        enable=1,
        sensitivity=0,
        reset_n=1
    )

    output, update, hold, activity = \
        await apply_pixel(
            dut,
            255
        )

    assert output == 255, \
        "Large change should update after re-enable"


    # ========================================================
    # PASS
    # ========================================================

    dut._log.info(
        "========================================"
    )

    dut._log.info(
        "       VITAL-AP TEST PASSED"
    )

    dut._log.info(
        "========================================"
    )
