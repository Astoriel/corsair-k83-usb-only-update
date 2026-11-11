# Reproducing the Update

This procedure was tested on one Corsair K83 Wireless. A failed write can leave the keyboard unusable. A full backup and recovery procedure for both controllers remain unverified.

## Files and Device Checks

Use Windows, PowerShell 7, Python 3, and the original signed CorsairFWUpd.exe from iCUE 3.38.88. See the [firmware notes](../firmware/README.md) for the package and checksums. Extract all four BIN files alongside the ZIP in a local directory.

~~~powershell
pwsh -File .\scripts\verify-package.ps1 -FirmwareDirectory 'C:\K83-files'
~~~

Connect the K83 directly to the PC with a USB data cable and keep power stable. Close iCUE, including its background GUI, and check that no other updater is running.

~~~powershell
python -I -B .\scripts\inspect-hid.py
~~~

The probe reads collection metadata and indexed string 4. It should find exactly two collections sharing a USB parent with VID/PID `1B1C:1B42`.

- `MI_00&Col05` has Usage Page `FFC2`, Usage 3, and a 64-byte input report.
- `MI_01` has Usage Page `FFC2`, Usage 4, a 65-byte output report, and protocol `P05`.
- Both should report revision `0313` before NXP and `0326` before Nordic.

The probe's JSON includes local device identifiers. Sanitize it before sharing.

## Stage 1: NXP

Set the paths to your installed updater and extracted firmware directory. The first invocation performs preflight checks and prints the command.

~~~powershell
$updater = 'C:\Program Files\Corsair\CORSAIR iCUE Software\CorsairFWUpd.exe'
$firmware = 'C:\K83-files'
.\scripts\update-stage.ps1 -Stage NXP -Updater $updater -FirmwareDirectory $firmware
~~~

Review the result. The script checks file hashes, the updater signature, the shared USB parent, both HID collections, and protocol P05. It lowercases both HID paths before passing them separately to the updater.

~~~powershell
# Starts the NXP write.
.\scripts\update-stage.ps1 -Stage NXP -Updater $updater -FirmwareDirectory $firmware -Confirmation 'FLASH NXP'
~~~

Keep the USB cable connected and iCUE closed during the operation. The private `runs/` directory contains stdout, stderr, and exit status. After code 0 and `Finished: success`, run `inspect-hid.py` again. Both channels should return with revision `0326` and the output channel should still report `P05`. Test keyboard input and the trackpad.

## Stage 2: Nordic

Proceed only after NXP succeeds and the keyboard passes those checks. Run the Nordic preflight separately.

~~~powershell
.\scripts\update-stage.ps1 -Stage Nordic -Updater $updater -FirmwareDirectory $firmware
~~~

~~~powershell
# Starts the Nordic write.
.\scripts\update-stage.ps1 -Stage Nordic -Updater $updater -FirmwareDirectory $firmware -Confirmation 'FLASH NORDIC'
~~~

The updater receives only D_2. The recorded Nordic operation took about 115 seconds. After success, recheck both HID channels, the USB revision, and keyboard input. Then test the iPad over Bluetooth. iCUE can check for available firmware, but its separate Nordic version query did not work in this experiment.

## If an Attempt Fails

Save the exit code, stdout, stderr, and the current USB device state. Stop before any next stage. Determine whether the updater logged `started NXP` or `started nordic` and whether it reported write progress. Both failed attempts in this experiment exited with code 4 during HID setup, before writing.

If the process takes longer than expected, inspect its PID, CPU use, logs, and USB state. Output can be buffered. The launcher waits for the updater to exit without a timeout. If only an ISP volume appears or the device vanishes, recovery requires a verified image and procedure for that hardware revision.

The published launch scripts were assembled after the successful experiment. Their syntax, package verification, and confirmation guard were checked. The original flashing commands and results are in the [operation logs](../evidence/).
