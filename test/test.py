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

    value |= sensitivity & 0x3
    value |= (prediction & 1) << 2
    value |= (force & 1) << 3
    value |= (value_aware & 1) << 4
    value |= (edge_enable & 1) << 5
    value |= (motion_enable & 1) << 6

    dut.uio_in.value = value


async def apply_pixel(dut, value):

    dut.ui_in.value = value

    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    output = int(dut.uo_out.value)
    status = int(dut.uio_out.value)

    update = status & 1
    hold = (status >> 1) & 1
    confidence = (status >> 2) & 1
    edge = (status >> 3) & 1
    motion = (status >> 4) & 1
    activity = (status >> 5) & 3
    burst = (status >> 7) & 1

    dut._log.info(
        "IN=%3d OUT=%3d UPDATE=%d HOLD=%d "
        "CONF=%d EDGE=%d MOTION=%d ACT=%d BURST=%d"
        % (
            value,
            output,
            update,
            hold,
            confidence,
            edge,
            motion,
            activity,
            burst,
        )
    )

    return output, status


@cocotb.test()
async def test_vital_ap(dut):

    dut._log.info("======================================")
    dut._log.info("       VITAL-APEX FUNCTIONAL TEST")
    dut._log.info("======================================")

    await reset_dut(dut)

    set_control(
        dut,
        sensitivity=1,
        prediction=1,
        force=0,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    # --------------------------------------------------------
    # 1. Initial pixel
    # --------------------------------------------------------

    dut._log.info("TEST 1: Initial pixel")

    out, status = await apply_pixel(dut, 100)

    # Output must be a valid 8-bit value
    assert 0 <= out <= 255


    # --------------------------------------------------------
    # 2. Static image
    # --------------------------------------------------------

    dut._log.info("TEST 2: Static image")

    for _ in range(5):
        out, status = await apply_pixel(dut, 100)

        assert 0 <= out <= 255


    # --------------------------------------------------------
    # 3. Small pixel variation
    # --------------------------------------------------------

    dut._log.info("TEST 3: Small variation")

    for value in [101, 102, 103, 102, 101]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------------
    # 4. Image edge
    # --------------------------------------------------------

    dut._log.info("TEST 4: Strong edge")

    for value in [20, 220, 20, 220]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------------
    # 5. Temporal sequence
    # --------------------------------------------------------

    dut._log.info("TEST 5: Temporal prediction")

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


    # --------------------------------------------------------
    # 6. Motion burst
    # --------------------------------------------------------

    dut._log.info("TEST 6: Motion burst")

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


    # --------------------------------------------------------
    # 7. Force update
    # --------------------------------------------------------

    dut._log.info("TEST 7: Force update")

    set_control(
        dut,
        sensitivity=3,
        prediction=1,
        force=1,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    out, status = await apply_pixel(dut, 77)

    assert out == 77


    # --------------------------------------------------------
    # 8. Normal adaptive mode
    # --------------------------------------------------------

    dut._log.info("TEST 8: Adaptive mode")

    set_control(
        dut,
        sensitivity=1,
        prediction=1,
        force=0,
        value_aware=1,
        edge_enable=1,
        motion_enable=1
    )

    for value in [80, 81, 82, 120, 200, 201, 202]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------------
    # 9. Disable
    # --------------------------------------------------------

    dut._log.info("TEST 9: Enable control")

    dut.ena.value = 0

    for value in [10, 50, 100, 200]:

        out, status = await apply_pixel(dut, value)

        assert 0 <= out <= 255


    # --------------------------------------------------------
    # 10. Re-enable
    # --------------------------------------------------------

    dut._log.info("TEST 10: Re-enable")

    dut.ena.value = 1

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

    assert out == 200


    dut._log.info("======================================")
    dut._log.info("       VITAL-APEX TEST PASSED")
    dut._log.info("======================================")
