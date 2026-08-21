![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# VITAL-AP — Value-, Transition-, and Temporal-Aware Adaptive Register

**Tiny Tapeout submission, SkyWater 130nm, TTSKY26C shuttle**

- [Read the full project documentation](docs/info.md)

## What is this?

VITAL-AP is an adaptive register architecture designed for **low-power image and video processing**. The design analyzes incoming 8-bit pixel data and determines whether the register needs to update or can retain its previous value.

The architecture combines **value awareness, transition awareness, and temporal awareness** to identify unnecessary data transitions. Small or insignificant changes can be suppressed, while significant changes such as image edges and motion-related transitions can be allowed to update normally.

The design also provides configurable sensitivity and control mechanisms, including a force-update mode when an immediate register update is required.

The main objective is to reduce unnecessary switching activity in pixel-processing datapaths while maintaining correct functional behavior.

**Research contribution:** VITAL-AP combines value-based, transition-based, and temporal activity awareness in a compact adaptive register architecture targeted specifically at image and video processing. The design explores how intelligent update suppression can reduce unnecessary switching activity while remaining suitable for a small Tiny Tapeout implementation.

## Design summary

- **Top module:** `tt_um_vital_ap`
- **Tile size:** 1×1
- **Technology:** SkyWater 130nm
- **HDL:** Verilog
- **Pixel input:** 8-bit `ui_in`
- **Pixel output:** 8-bit `uo_out`
- **Control input:** 8-bit `uio_in`
- **Status output:** 8-bit `uio_out`
- **Clock:** `clk`
- **Reset:** Active-low `rst_n`
- **Enable:** `ena`
- **Application:** Low-power image and video processing
- **Main technique:** Adaptive register update suppression
- **Awareness mechanisms:** Value, transition, temporal, edge, and motion activity
- **Verification:** Verilog and Cocotb-based functional verification

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more, visit https://tinytapeout.com.

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## Credits

We gratefully acknowledge the **Center of Excellence (CoE) in Integrated Circuits and Systems (ICAS)** and the **Department of Electronics and Communication Engineering (ECE), RV College of Engineering, Bengaluru**, for providing the necessary resources and guidance.

Special thanks to **Dr. H V Ravish Aradhya (HoD-ECE), Dr. K R Usha Rani (Associate Dean-PG), Dr. K. S. Geetha (Vice Principal), and Dr. K. N. Subramanya (Principal)** for their constant encouragement and support in facilitating this Tiny Tapeout SKY25A submission.
