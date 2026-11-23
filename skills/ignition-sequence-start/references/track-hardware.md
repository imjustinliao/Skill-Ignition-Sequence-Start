# Track: hardware, firmware and electronics

For physical things: a sensor gadget, a robot, a wearable, a custom board. Guide like an embedded and electrical engineer who cares about safety: prototype on a breadboard, simulate what can be simulated, and be precise about what only the owner's hands can verify.

## Questions

Ask only those you cannot infer, alongside the drafted direction (`intake.md` › 3).

1. **What does it sense or drive, and how is it powered?** Sensors, motors, displays; USB (default), battery, or mains.
2. **Which board or parts do you already have, and does it need wireless?** Default: the board recommended below; Wi-Fi only if needed.
3. **Breadboard prototype or a custom PCB?** Default: breadboard first.

## The draft

`docs/architecture.md` gets: block diagram (Shape), board and parts with a bill of materials (part numbers, prices, links), power budget, pin map and buses (Data), toolchain, what will be simulated, and safety notes. The message summarizes it, with what the owner must buy and its cost on their own lines.

## Defaults

- **Boards**: ESP32 for Wi-Fi or Bluetooth; Raspberry Pi Pico (RP2040) for low-cost general use; Arduino Uno for absolute beginners and shields. A Raspberry Pi (Linux) only when it needs a full OS, camera processing or heavy compute.
- **Toolchain**: PlatformIO in VS Code (default); ESP-IDF for low-level ESP32 control; the Arduino IDE for the simplest start.
- **Simulation**: Wokwi for ESP32, Pico and Arduino circuits, in the browser, VS Code or CI. Keep its API token in CI secrets, never in the repo.
- **PCB**: KiCad, with electrical-rule and design-rule checks clean before ordering. Keep the BOM as a CSV in the repo.

## Safety rules (non-negotiable)

- **Mains voltage**: never advise wiring it. Use a certified, enclosed power module, or a qualified electrician.
- **Lithium batteries**: protected cells and a proper charger only; never short them; don't leave them charging unattended.
- Check logic levels (3.3 V vs 5 V), current limits per pin and per regulator, and a common ground before powering anything.

## Build and verify

- **The agent can**: compile, run unit tests on logic, simulate in Wokwi, check pin conflicts against the datasheet, run KiCad checks and validate the BOM.
- **Only the owner can**: wire it, power it up, read real sensors, judge heat and mechanics. Give numbered steps with a wiring diagram, the exact upload command, the expected serial output, and what to photograph or paste back. Treat their report as the test result.
- Power up in stages: board alone, then one peripheral at a time.

## Ship

A short demo video, the schematic (PDF), the BOM, wiring photos or a diagram, the firmware in the repo, and a README that lets someone else build it.

## Pitfalls

ESP32 strapping pins and ADC2 pins used while Wi-Fi is on · missing common ground · power-hungry parts on USB power · trusting a part without reading its datasheet · ordering a PCB before the breadboard works · secrets (Wi-Fi passwords, API keys) hard-coded in firmware: keep them in `secrets.h` (gitignored) with a committed `secrets.example.h`.
