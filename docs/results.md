# Recorded Results

The experiment took place on November 10, 2026. Times retain the logs' UTC+01:00 offset.

| Time | Configuration | Result |
|---|---|---|
| 00:15:51–00:15:53 | One MI_01 path in the case displayed by pnputil | Exit 4. The path filter rejected the interface before flashing. |
| 00:18:03–00:18:04 | One lowercase MI_01 path | P05 read successfully. Input report 0 was missing. Exit 4 before flashing. |
| 00:24:56–00:25:41 | Two paths, NXP D_1 | Exit 0, Finished: success, USB REV_0326. |
| 00:28:22–00:30:16 | Two paths, Nordic D_2 | Exit 0, Finished: success. Both HID channels and P05 returned. |

Windows detected the same VID/PID and both expected HID collections after each successful stage. After Nordic, the keyboard and touchpad drivers showed Started. iCUE detected the K83 and reported that no newer firmware was available. Its secondary chip version query returned Unknown command, so the Nordic version was not independently confirmed.

The owner confirmed on November 11 that the physical trackpad buttons and gestures worked on the iPad after the update. The iPad model, iPadOS version, and individual gestures were not recorded.

A complete 3.13 backup, recovery after a partial write, compatibility with other hardware revisions, and the behavior of the absent receiver remain unverified. The firmware was validated through the updater's success status and subsequent device checks. No separate memory dump was made.
