import cocotb
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut):

    dut.rst_n.value = 0
    dut.ena.value = 0

    dut.ui_in.value = 0
    dut.uio_in.value = 0

    for _ in range(4):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1
    dut.ena.value = 1

    await RisingEdge(dut.clk)


def set_control(
    dut,
    sensitivity=1,
    prediction=1,
    force=0,
    value_aware=1,
    edge_enable=1,
    motion_enable=1
):

    control = 0

    control |= sensitivity & 0x3
    control |= prediction << 2
    control |= force << 3
    control |= value_aware << 4
    control |= edge_enable << 5
    control |= motion_enable << 6

    dut.uio_in.value = control


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    output = int(dut.uo_out.value)
    status = int(dut.uio_out.value)

    update = status & 0x01
    hold = (status >> 1) & 0x01
    confidence = (status >> 2) & 0x01
    edge = (status >> 3) & 0x01
    motion = (status >> 4) & 0x01
    activity = (status >> 5) & 0x03
    motion_burst = (status >> 7) & 0x01

    dut._log.info(
        "PIXEL=%3d OUT=%3d "
        "UPDATE=%d HOLD=%d CONF=%d "
        "EDGE=%d MOTION=%d ACT=%d BURST=%d"
        % (
            value,
            output,
            update,
            hold,
            confidence,
            edge,
            motion,
            activity,
            motion_burst,
        )
    )

    return (
        output,
        update,
        hold,
        confidence,
        edge,
        motion,
        activity,
        motion_burst,
    )


@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info("")
    dut._log.info("======================================")
    dut._log.info("       VITAL-APEX TEST")
    dut._log.info("======================================")

    await reset_dut(dut)

    set_control(
        dut,
        sensitivity=1,
        prediction=1,
        force=0,
        value_aware=1,
        edge_enable=1,
        motion_enable=1,
    )


    # ========================================================
    # TEST 1 - INITIAL PIXEL
    # ========================================================

    dut._log.info("TEST 1: Initial pixel")

    result = await apply_pixel(dut, 100)

    assert result[0] == 100


    # ========================================================
    # TEST 2 - STATIC REGION
    # ========================================================

    dut._log.info("TEST 2: Static region")

    old_output = result[0]

    for _ in range(4):

        result = await apply_pixel(dut, 100)

        assert result[0] == old_output


    # ========================================================
    # TEST 3 - SMALL CHANGE
    # ========================================================

    dut._log.info("TEST 3: Small change")

    result = await apply_pixel(dut, 101)

    dut._log.info(
        "Small transition handled"
    )


    # ========================================================
    # TEST 4 - STRONG EDGE
    # ========================================================

    dut._log.info("TEST 4: Strong image edge")

    result = await apply_pixel(dut, 220)

    assert result[0] == 220


    # ========================================================
    # TEST 5 - OPPOSITE EDGE
    # ========================================================

    dut._log.info("TEST 5: Opposite edge")

    result = await apply_pixel(dut, 20)

    assert result[0] == 20


    # ========================================================
    # TEST 6 - TEMPORAL SEQUENCE
    # ========================================================

    dut._log.info("TEST 6: Temporal prediction")

    await apply_pixel(dut, 40)
    await apply_pixel(dut, 60)
    await apply_pixel(dut, 80)

    result = await apply_pixel(dut, 100)

    dut._log.info(
        "Temporal predictor exercised"
    )


    # ========================================================
    # TEST 7 - MOTION BURST
    # ========================================================

    dut._log.info("TEST 7: Motion burst")

    motion_values = [
        10,
        220,
        20,
        230,
        30,
        240,
        40,
        250,
    ]

    for value in motion_values:

        result = await apply_pixel(dut, value)

    assert result[0] == 250


    # ========================================================
    # TEST 8 - FORCE UPDATE
    # ========================================================

    dut._log.info("TEST 8: Force update")

    set_control(
        dut,
        sensitivity=3,
        prediction=1,
        force=1,
        value_aware=1,
        edge_enable=1,
        motion_enable=1,
    )

    result = await apply_pixel(dut, 77)

    assert result[0] == 77


    # ========================================================
    # TEST 9 - DISABLE
    # ========================================================

    dut._log.info("TEST 9: Disable")

    dut.ena.value = 0

    old_output = int(dut.uo_out.value)

    result = await apply_pixel(dut, 200)

    assert result[0] == old_output


    # ========================================================
    # TEST 10 - RE-ENABLE
    # ========================================================

    dut._log.info("TEST 10: Re-enable")

    dut.ena.value = 1

    set_control(
        dut,
        sensitivity=0,
        prediction=0,
        force=1,
        value_aware=1,
        edge_enable=1,
        motion_enable=1,
    )

    result = await apply_pixel(dut, 200)

    assert result[0] == 200


    # ========================================================
    # FINISH
    # ========================================================

    dut._log.info("")
    dut._log.info("======================================")
    dut._log.info("       VITAL-APEX TEST PASSED")
    dut._log.info("======================================")
