# Obtaining the Original Files

The original package URL comes from the server and filename in the iCUE index.

https://www3.corsair.com/software/CUE_V3/K83WIRELESS.zip

Availability and contents may change. If the link fails, request the original K83 3.26 package from Corsair. Use [manifest.json](manifest.json) and [verify-package.ps1](../scripts/verify-package.ps1) to check the ZIP and extracted files. The updater used in the experiment was CorsairFWUpd.exe 3.38.88.0 with a valid Corsair signature. Its SHA-256 is in the manifest.

| File | Role | Bytes |
|---|---|---:|
| K83WIRELESS.zip | Original package | 208624 |
| Sunder_D_1_App_v3.26.52.bin | Keyboard NXP, stage 1 | 83184 |
| Sunder_D_2_App_v3.26.52.bin | Keyboard Nordic, stage 2 | 181104 |
| Sunder_U_1_App_v3.26.52.bin | Receiver image | 24684 |
| Sunder_U_2_App_v3.26.52.bin | Receiver image | 24108 |

Only D_1 and D_2 were flashed. The APP images are for the original updater. Their suitability as replacements for firmware.bin on a ROM ISP volume has not been established.
