# Experiment Logs

| Directory | Attempt |
|---|---|
| 01-path-case | One MI_01 path in the displayed case, exit 4 |
| 02-single-channel | Lowercase MI_01, P05, report 0 missing, exit 4 |
| 03-nxp-success | Two paths, NXP write, exit 0, and USB/HID checks |
| 04-nordic-success | Two paths, Nordic write, exit 0, and USB/HID checks |

The stdout and stderr files retain the original messages, progress lines, and completion status. Local paths and device identifiers were replaced. VID/PID, interface numbers, usages, revisions, timestamps, and exit codes remain visible.

The public logs use placeholders such as `C:\Users\<USER>\<LOCAL-PROJECT>`, `<CORSAIR-INSTALL>`, `<K83-SERIAL>`, `<K83-BLE>`, and `<HID00>`. Use the HID paths discovered on your own machine for an actual run.

`icue-selected.log` contains selected K83 entries with their original line-number prefixes. Full source logs remain local.
