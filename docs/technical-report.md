# Technical Report

## Setup and Update Blocker

The tested K83 Wireless had wired VID/PID `1B1C:1B42`, application 3.13, bootloader 3.3, and HID protocol `P05`. The receiver, `1B1C:1B6D`, was absent. The experiment used iCUE 3.38.88 and the original signed `CorsairFWUpd.exe` version 3.38.88.0.

iCUE offered application 3.26 from `K83WIRELESS.zip`. Its index required bootloader >=3.3 and listed `K83WIRELESS-isp-3.26` as a dependency. The regular update flow waited for the missing secondary device. This successful keyboard-only update does not establish where every iCUE version enforces that requirement. The secondary USB device and the Nordic controller inside the keyboard are distinct in this experiment.

## Read-Only HID Inspection

`CreateFileW` opened each target collection with desired access 0, `OPEN_EXISTING`, and read/write sharing. `HidD_GetAttributes`, `HidD_GetPreparsedData`, and `HidP_GetCaps` supplied metadata. `HidD_GetIndexedString(handle, 4, ...)` returned `P05` on the wired `FFC2:0004` collection. That string denotes protocol 5. The read-only probe sent no Output Reports, Feature Reports, or reset commands.

An initial diagnostic run received access denied from the sandbox. Outside that sandbox the same read succeeded.

| Collection | Page | Usage | Input bytes | Output bytes | Feature bytes |
|---|---|---:|---:|---:|---:|
| MI_00&Col05 | FFC2 | 3 | 64 | 0 | 0 |
| MI_01 | FFC2 | 4 | 65 | 65 | 65 |

Both collections belong to the same composite USB parent. The Bluetooth device is a separate branch in Windows. For protocol >3, the native updater associates its internal input channel type 0 with Usage 3 and the other relevant channels with Usage 4. The message `No device found for report: 0` refers to that internal channel lookup.

## Command-Line Behavior

| Option | Behavior |
|---|---|
| --usb-vid, --usb-pid, --hid-up | Hexadecimal VID, PID, and Usage Page |
| --path | Case-sensitive HID path filter. Repeat once per collection. |
| --image | One BIN per process. The last nonempty value wins. |
| --test-storage=true | Storage status checks during update operations |
| --delays-nxp, --delays-nordic | Short, medium, and long delays in milliseconds |

The successful runs left delays at their defaults. The logs report 5/10/750 ms for NXP and 6/10/950 ms for Nordic. `--test-storage` is not a read-only diagnostic or evidence of a full memory comparison.

`CorsairFwUpdMc.exe` is a wrapper that can accept multiple image arguments and launch the native updater in sequence. The experiment used two separate native invocations and checked the device between them.

## Images and File Offsets

The archive contains D_1 and D_2 for the keyboard, and U_1 and U_2 for the receiver. D_1 is NXP. Its `@@` marker at file offset `0x100` begins `40 40 1C 1B 42 1B 26 03` and is followed by `P05`. Its USB descriptor at `0x140B4` has VID/PID `1B1C:1B42` and `bcdDevice 0x0326`. D_2 is Nordic. Its `##` marker at `0x1B100` begins `23 23 1C 1B 42 1B 26 03`.

The native updater selects storage `0xF0` for NXP or `0x06` for Nordic. Its logs identify the branch as `started NXP pid=1b42` or `started nordic pid=1b42`. The table lists file offsets, rather than RVAs, for the binaries identified by [manifest.json](../firmware/manifest.json).

| Binary | File offset | Observation |
|---|---|---|
| CorsairFWUpd.exe | 0x33DEC–0x33EB8 | CLI option strings |
| CorsairFWUpd.exe | 0x11F10 | Argument parsing loop |
| CorsairFWUpd.exe | 0x1277A–0x127BC | Append each --path to a list |
| CorsairFWUpd.exe | 0x1282E | Store one image path |
| CorsairFWUpd.exe | 0x11A4D–0x11A68, 0x10B90 | Case-sensitive path comparison |
| CorsairFWUpd.exe | 0x11B9D | Reject a different Usage Page |
| CorsairFWUpd.exe | 0x1971A–0x1971D, 0x19789, 0x19805–0x1982C | Indexed string 4, P prefix check, decimal parse |
| CorsairFWUpd.exe | 0x1B13C–0x1B150 | Protocol 3–5 branch |
| CorsairFWUpd.exe | 0x18032–0x1804D, 0x188CA–0x18A15 | Map Usage 3 and 4 to channels, using report lengths |
| CorsairFWUpd.exe | 0x18370 | Look up a channel handle |
| CorsairFWUpd.exe | 0x29C22, 0x29C2C | Validate image VID and PID |
| CorsairFWUpd.exe | 0x1A040, 0x1A0A6–0x1A0BF | APP update and NXP/Nordic storage selection |
| CorsairFWUpd.exe | 0x18FA0, 0x1A549, 0x1AA27 | StorageStatus and its call sites |
| CorsairFWUpd.exe | 0x1A796–0x1A855 | Try reopening the interface during writing |
| CorsairFWUpd.exe | 0x1AB4A–0x1ABAC | Send final reset |
| CorsairFWUpd.exe | 0x12C3B–0x12C44 | Exit code 4 condition |
| CorsairFwUpdMc.exe | 0x5DCE–0x62D0, 0x639A, 0x784C–0x7897 | Register options, read image list, launch updater |
| iCUE.dll | 0x19F0FF0, 0x19F17FD | Filter on FFC2 and generate --hid-up=ffc2 |

The offsets are observations from the binaries, whose original source code was unavailable.

## Failure and Success

The first run closed MI_01 during path filtering. Lowercasing that path let the next run read protocol 5, but MI_00&Col05 was still excluded. Both attempts returned code 4 before flashing.

With both paths, the updater briefly logged a missing report 1 while only the input collection had been added. It then found the output collection, began writing, reached 100%, and returned success. Read that early message in the context of the full run.

NXP changed the USB revision to `0326`. Both channels and P05 returned before the separate Nordic run. Nordic also returned success. The final HID checks and the working iPad trackpad are documented in [results](results.md).

## Recovery Limits

The iCUE binary has a separate ISP workflow that looks for a `CRP DISABLD` volume and `firmware.bin`. It was not used. The experiment did not establish a K83-specific recovery entry method, a matching ISP file, or a backup of both controllers. Generic LPC USB ISP documentation does not establish a Nordic backup path. An interrupted write can leave this keyboard unusable.
