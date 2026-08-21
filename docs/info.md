## Credits

We gratefully acknowledge the Center of Excellence (CoE) in Integrated Circuits and Systems (ICAS) and the Department of Electronics and Communication Engineering (ECE) for providing the necessary resources and guidance.

Special thanks to Dr. H V Ravish Aradhya (HoD- ECE), Dr. K R Usha Rani (Associate Dean-PG), Dr. K. S. Geetha (Vice Principal) and Dr. K. N. Subramanya (Principal) for their constant encouragement and support in facilitating this Tiny Tapeout SKY26C submission.

## How it works

VITAL-AP (Value-, Transition-, and Temporal-Aware Adaptive Register) is a low-power adaptive register designed for image and video processing.

The design receives an 8-bit pixel value through `ui_in` and compares the incoming pixel with previously stored pixel information. It uses value, transition, and temporal information to decide whether the register should update or retain its previous value.

The basic operation is:

1. An 8-bit pixel is applied to `ui_in`.
2. The current pixel is compared with previously stored pixel information.
3. The transition between the current and previous values is evaluated.
4. Temporal and activity information is considered.
5. The adaptive logic determines whether the pixel represents a significant change.
6. If an update is required, the new pixel value is stored.
7. If the change is not significant, the previous value is retained.
8. The stored/processed pixel is provided through `uo_out`.

The design also provides configurable controls for sensitivity, prediction, force update, value awareness, edge awareness, and motion awareness through the user I/O interface.

The main idea is to avoid unnecessary register switching when the incoming image/video data changes only slightly, thereby reducing switching activity and potentially reducing dynamic power.

### Basic operation

```text
          8-bit Pixel
               |
               v
      +------------------+
      | Value Analysis   |
      +--------+---------+
               |
               v
      +------------------+
      | Transition       |
      | Analysis         |
      +--------+---------+
               |
               v
      +------------------+
      | Temporal /       |
      | Activity Analysis|
      +--------+---------+
               |
               v
      +------------------+
      | Adaptive Update  |
      | Decision         |
      +--------+---------+
               |
          +----+----+
          |         |
        UPDATE     HOLD
          |         |
          v         v
       New Pixel  Previous
          |         |
          +----+----+
               |
               v
          8-bit Output
```

For a static image region, consecutive pixels may have very similar values. VITAL-AP can therefore suppress unnecessary updates.

For large changes, such as image edges or motion, the adaptive logic can allow the register to update.

A force-update control is also provided when an application requires the incoming pixel to be stored regardless of the normal adaptive decision.

---

## How to test

The project can be tested using the provided Verilog testbench and Cocotb test.

The testbench applies different pixel sequences to the design and observes the resulting output and status signals.

### 1. Reset the design

Initially, `rst_n` is driven low and the design is disabled.

After several clock cycles:

```text
rst_n = 1
ena   = 1
```

The design begins normal operation.

### 2. Apply a static image

Apply the same pixel repeatedly:

```text
100 → 100 → 100 → 100
```

This represents a static image region.

### 3. Apply small pixel changes

Apply small variations:

```text
100 → 101 → 102 → 103 → 102
```

This tests the transition-aware and adaptive behavior.

### 4. Apply a large transition

Apply significantly different values:

```text
20 → 220 → 20 → 220
```

This represents a strong image edge or high-activity region.

### 5. Apply a temporal sequence

Apply a gradually changing sequence:

```text
40 → 60 → 80 → 100 → 120 → 140 → 160
```

This tests the temporal behavior of the adaptive register.

### 6. Apply a motion sequence

A rapidly changing sequence can be used to represent motion:

```text
10 → 240 → 20 → 230 → 30 → 220
```

### 7. Test force-update mode

Enable the force-update control and apply a pixel value.

The force-update mode allows the incoming pixel to be stored without relying on the normal adaptive suppression decision.

### 8. Observe the waveform

The simulation generates:

```text
tb.fst
```

The waveform can be opened using GTKWave.

Important signals to observe are:

- `clk`
- `rst_n`
- `ena`
- `ui_in`
- `uo_out`
- `uio_in`
- `uio_out`
- `uio_oe`

The provided `tb.gtkw` file can be used to load the relevant signals into GTKWave.

### Cocotb testing

The automated Cocotb test checks:

- Reset
- Initial pixel input
- Static image data
- Small pixel variations
- Strong image transitions
- Temporal sequences
- High-motion sequences
- Force-update mode
- Adaptive mode
- Enable/disable operation

A successful simulation should finish with:

```text
VITAL-AP TEST PASSED
```
