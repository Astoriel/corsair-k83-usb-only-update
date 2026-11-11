# Sources

The primary evidence is the [experiment logs](../evidence/) and [firmware manifest](../firmware/manifest.json).

- Corsair's K83 setup guide calls for both keyboard and receiver in the normal update workflow. [Connect and Configure Your K83 Wireless](https://forum.corsair.com/blog/how-tos-and-diy/k83wireless/)
- Corsair recommends a direct USB connection during firmware updates. [Updating device firmware](https://help.corsair.com/hc/en-us/articles/360025278572-Updating-device-firmware)
- The K83 manual explains charging indicators. Solid green means charged, and pulsing green means charging. It does not specify a minimum charge for this flashing procedure. [K83 Quick Start Guide](https://assets.corsair.com/image/upload/corsairmedia/sys_master/productcontent/K83_Wireless_QSG.pdf)
- Windows HID references cover opening a collection and reading indexed strings. [Opening HID collections](https://learn.microsoft.com/en-us/windows-hardware/drivers/hid/opening-hid-collections), [HidD_GetIndexedString](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/hidsdi/nf-hidsdi-hidd_getindexedstring)
- NXP describes USB ISP and flash read protection for certain LPC devices. Applying that procedure to this K83 remains unverified. [NXP AN11305](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/lpc/50946/1/AN11305v.1.pdf)
- The author of a 2020 forum thread reported that updating to 3.25 resolved similar click failures after iPadOS 13.4. That is a separate user's report. [K83 iPad clicking issue](https://forum.corsair.com/forums/topic/159317-corsair-k83-ios134-ipad-clicking-issue/)

The iCUE index identified K83WIRELESS.zip as application 3.26, released on 2020-05-14 at 15:30 UTC, with bootloader >=3.3 and dependency K83WIRELESS-isp-3.26. The local copies matched the index's SHA-512 integrity field. All four archive entries passed CRC verification, and the extracted keyboard images matched iCUE's cached copies.
