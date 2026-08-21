![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# VITAL-AP -- Value-, Transition-, and Temporal-Aware Adaptive Register

Tiny Tapeout submission for low-power image and video processing using the SkyWater 130nm technology.

- **Project documentation:** See `info.md`
- **Source code:** See `src/project.v`
- **Testbench:** See `test/`

## What is this?

VITAL-AP is a compact adaptive register designed for low-power image and video processing. It receives an 8-bit pixel value and compares it with previously stored pixel information. The design uses value changes, transition magnitude, and temporal behavior to determine whether the new pixel should be stored or whether the previous value can be retained.

For relatively static image regions, where consecutive pixel values change only slightly, VITAL-AP can suppress unnecessary register updates. When a significant change such as an image edge or motion is detected, the register can update normally. The design also provides configurable sensitivity, activity controls, and a force-update mode.

The main objective is to reduce unnecessary switching activity in image and video processing hardware while maintaining useful pixel information.

## Design Summary

VITAL-AP is a 1×1 Tiny Tapeout digital design implemented in Verilog for SkyWater 130 nm technology.

Top module: tt_um_vital_ap
Tile size: 1×1
Technology: SkyWater 130 nm
HDL: Verilog
Clock: clk
Reset: Active-low rst_n
Enable: ena
Pixel input: 8-bit ui_in
Pixel output: 8-bit uo_out
Control input: 8-bit uio_in
Status output: 8-bit uio_out
Application: Low-power image and video processing
Main feature: Adaptive suppression of unnecessary register transitions using pixel value, transition, and temporal information
Additional features: Configurable sensitivity, edge/motion activity detection, and force-update control


## What is Tiny Tapeout?

Tiny Tapeout is an educational project that makes it easier and more affordable to manufacture small digital and analog designs on a real chip.

For more information, visit https://tinytapeout.com/.

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
  - Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)
