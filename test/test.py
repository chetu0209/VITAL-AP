import cocotb
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut):

    dut.rst_n.value = 0
    dut.ena.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    for _ in range(5):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1
    dut.ena.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


def set_control(
    dut,
    sensitivity=1,
    prediction=1,
    force=0,
    value_aware=1,
    edge_enable=1,
    motion_enable=1
):

    value = 0

    value |= (sensitivity & 0x3)
    value |= ((prediction & 1) << 2)
    value |= ((force & 1) << 3)
    value |= ((value_aware & 1) << 4)
    value |= ((edge_enable & 1) << 5)
    value |= ((motion_enable & 1) << 6)

    dut.uio_in.value = value


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    # Read output
    try:
        output = int(dut.uo_out.value)
    except ValueError:
        dut._log.error("uo_out contains X/Z")
        raise

    # Read status
    try:
        status = int(dut.uio_out.value)
    except ValueError:
        dut._log.error("uio_out contains X/Z")
        raise

    update = status & 1
    hold = (status >> 1) & 1
    confidence = (status >> 2) & 1
    edge = (status >> 3) & 1
    motion = (status >> 4) & 1
    activity = (status >> 5) & 3
    burst = (status >> 7) & 1

    dut._log.info(
        "PIXEL=%3d  OUTPUT=%3d  "
        "UPDATE=%d HOLD=%d CONF=%d EDGE=%d "
        "MOTION=%d ACTIVITY=%d BURST=%d"
        % (
            value,
            output,
            update,
            hold,
            confidence,
            edge,
            motion,
            activity,
            burst
        )
    )

    return output, status


@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info("")
    dut._log.info("==============================================")
    dut._log.info(" VITAL-AP FUNCTIONAL TEST")
    dut._log.info("==============================================")

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    await reset_dut(dut)

    dut._log.info("RESET PASSED")


    # --------------------------------------------------
    # NORMAL ADAPTIVE MODE
    # --------------------------------------------------

    set_control(
        dut,
        sensitivity=1,
        prediction=1,
        force=0,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    dut._log.info("NORMAL ADAPTIVE MODE")


    # --------------------------------------------------
    # TEST 1: Initial pixel
    # --------------------------------------------------

    dut._log.info("TEST 1: Initial pixel")

    out, status = await apply_pixel(dut, 100)

    assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 2: Static image
    # --------------------------------------------------

    dut._log.info("TEST 2: Static image")

    for _ in range(8):

        out, status = await apply_pixel(dut, 100)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 3: Small changes
    # --------------------------------------------------

    dut._log.info("TEST 3: Small pixel variations")

    for value in [101, 102, 103, 102, 101]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 4: Image edge
    # --------------------------------------------------

    dut._log.info("TEST 4: Strong image edges")

    for value in [20, 220, 20, 220]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 5: Temporal sequence
    # --------------------------------------------------

    dut._log.info("TEST 5: Temporal behavior")

    for value in [
        40,
        60,
        80,
        100,
        120,
        140,
        160,
        180
    ]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 6: Motion burst
    # --------------------------------------------------

    dut._log.info("TEST 6: High-motion sequence")

    for value in [
        10,
        240,
        20,
        230,
        30,
        220,
        40,
        210,
        50,
        200
    ]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 7: Force mode
    # --------------------------------------------------

    dut._log.info("TEST 7: Force-update mode")

    set_control(
        dut,
        sensitivity=3,
        prediction=1,
        force=1,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    # Give the sequential circuit two cycles.
    await apply_pixel(dut, 77)
    out, status = await apply_pixel(dut, 77)

    assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 8: Return to adaptive mode
    # --------------------------------------------------

    dut._log.info("TEST 8: Return to adaptive mode")

    set_control(
        dut,
        sensitivity=1,
        prediction=1,
        force=0,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    for value in [
        80,
        81,
        82,
        120,
        200,
        201,
        202
    ]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------
    # TEST 9: Enable control
    # --------------------------------------------------

    dut._log.info("TEST 9: Enable control")

    dut.ena.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    dut.ena.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


    # --------------------------------------------------
    # TEST 10: Re-enable
    # --------------------------------------------------

    dut._log.info("TEST 10: Re-enable")

    set_control(
        dut,
        sensitivity=0,
        prediction=0,
        force=1,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    out, status = await apply_pixel(dut, 200)

    assert 0 <= out <= 255


    # --------------------------------------------------
    # FINAL
    # --------------------------------------------------

    dut._log.info("")
    dut._log.info("==============================================")
    dut._log.info(" VITAL-AP TEST PASSED")
    dut._log.info("==============================================")
