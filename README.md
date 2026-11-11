# Updating the Corsair K83 over USB Without the Dongle

My Corsair K83 Wireless still had its USB cable, but the little 2.4 GHz receiver was gone. It connected to my iPad over Bluetooth, yet the trackpad buttons didn't work properly. A firmware update looked promising. The keyboard was on **3.13**, and iCUE offered **3.26**.

Then iCUE asked me to plug in the missing dongle. The keyboard was already plugged into the PC, so I tried the updater that ships with iCUE 3.38.88, `CorsairFWUpd.exe`, directly.

The first attempt failed because the updater compared the USB device path case-sensitively. Windows printed uppercase letters where the updater expected lowercase. Fixing that got me one step further: the updater read HID protocol `P05` and then stopped with `No device found for report: 0`. I had passed only the output channel. The keyboard also exposed a separate input channel on the same USB device.

I passed both lowercase HID paths as separate `--path` arguments. The original updater flashed **NXP first, then Nordic**, in separate runs. Both exited with code `0` and printed `Finished: success`. Windows reported USB revision `0326` afterward. Back on the iPad, **the trackpad buttons and gestures worked**.

| HID channel | Interface | Usage Page | Usage |
|---|---|---|---:|
| Input | `MI_00&Col05` | `0xFFC2` | 3 |
| Output | `MI_01` | `0xFFC2` | 4 |

The keyboard was `1B1C:1B42` with bootloader 3.3. The two keyboard images were `Sunder_D_1_App_v3.26.52.bin` (NXP) and `Sunder_D_2_App_v3.26.52.bin` (Nordic). The receiver, `1B1C:1B6D`, was absent throughout.

- [How to reproduce the update](docs/reproduction.md)
- [Technical report and updater offsets](docs/technical-report.md)
- [Firmware file hashes and provenance](firmware/README.md)
- [Sanitized logs from all four attempts](evidence/)
- [Results](docs/results.md) and [sources](docs/sources.md)

An interrupted write can leave the keyboard unusable. I accepted that risk without a complete 3.13 backup or a verified recovery procedure. This is one successful K83 update. The iPad model and iPadOS version were not recorded, and the Nordic version was not independently read back after flashing.
