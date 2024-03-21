# k210comb

#### SPI Flash inspection tools for Kendryte k210 based devices
---

Krux [the open-source-software project](https://github.com/selfcustody/krux) currently runs on various Kendryte K210 based devices, which all have 16MB of SPI Flash permanent storage.

The documentation and tools here are the result of curiosity to analyze this internal SPI Flash storage.
The tools can be run directly on a k210 device via usb-console, or they can be run against a flash_dump
that has been saved on another computer.

---

## Enabling the python REPL in krux

For security reasons, krux disables the python REPL so that if connected to a
computer (bad habit!!!) which has been compromised, that computer will NOT be able to access the device or secrets that might be loaded in memory.

To use the tools in this repo on a running krux device, you'll need to enable the following option in `krux/firmware/MaixPy/components/micropython/port/include/mpconfigport.h`, then rebuild the firmware.  You can then use the '-s' option with `ktool` to load the new firmware directly into sram and boot once -- without ever flashing the device.  Alternatively, developers may choose to flash the new firmware to their device -- to enable the REPL permanently.

"#define MICROPY_ENABLE_COMPILER     (1)"

---

## Tools in this repository

The following tools may be copy/pasted into the k210 console w/`<CTRL>-e`, or they may be run on another computer
against `/tmp/k210.flash_dump` assuming that file was previously saved from a k210 device.

* [wdt_pause.py](./wdt_pause.py): 
stops both watchdog timers (even if they are not running) so the k210 device doesn't auto-reboot.

* [mocked_Maix_utils.py](./mocked_Maix_utils.py):
ensures that `utils.flash_read()` is available, because tools here need it.

* [decremented_bool.py](./decremented_bool.py):
used to decrement verbosity for functions that call other functions.

* [hash_flash.py](./hash_flash.py):
returns the sha256 hash of bytes in flash.

* [crc32_flash.py](./crc32_flash.py):
returns the crc32 checksum of bytes in flash.

* [hashcrc_flash.py](./hashcrc_flash.py):
returns the sha256 hash and the crc32 checksum of bytes in flash.

* [all_bytes_are.py](./all_bytes_are.py):
returns true if bytes in flash are the same as the one passed in.

* [validate_aes_size_app_sha_nulpad.py](./validate_aes_size_app_sha_nulpad.py):
used to validate a kboot/ktool sector.

* [kboot_classes.py](./kboot_classes.py):
classes to model Kboot's bootloader, configuration and application sectors.

* [analyze_spi_flash.py](./analyze_spi_flash.py):
using above tools, analyzes the entirety of SPI Flash, verbosely printing its findings.

* [hex_dump.py](./hex_dump.py):
a kludgy-yet-versatile implementation of hex_dump for visually inspecting bytes in flash.

---

## Starting with a clean slate

We could just get started inspecting our device as it is, but assuming we've been using it,
or that it was already setup when it was acquired, there is no telling what might be installed in SPI Flash.
In order to have realistic expectations of what is installed, and assuming that there is nothing important
like encrypted mnemonics that we don't have backed-up elsewhere, we might consider starting with a clean slate.

See [An introduction to Kboot](./docs/intro_to_Kboot.md), a tool for flashing k210 devices, if you are 
interested in erasing the entire SPI Flash.  This same document also explains how to get a flash_dump of
your device, which is a good idea in case you are hesitant about destroying information that might not be 
saved elsewhere.

---

## Getting familiar with krux via the k210 usb console

Users connect to the k210 device via usb in order to flash the device, and then just use it.  But we can 
also connect to the k210 device via usb console in order to inspect it, to debug it while it is running, 
or even while it appears to be "bricked".  This may seem daunting at first, therefore the following document 
intends to demystify getting-to-know your k210 device and how krux uses it.

See [Intro to krux on k210 based Amigo](./docs/intro_to_krux_on_amigo.md)

---

## Running the analyze_spi_flash() function

This tool intends to inspect SPI Flash on a k210 device, with the assumption that it's setup for krux,
printing a report that might ease-our-minds, or to give pointers for where to perform further inspection.

See [analyze_spi_flash example](./docs/analyze_spi_flash_example.md)

---

## Using the hex_dump tool

This tool, just like it sounds, intends to allow visual inspection of all bytes in SPI Flash.  
Since 16MB of SPI Flash is a lot to check on a byte-by-byte basis, it's intended to be used when we 
have a good idea of where we want to inspect.

See [hex_dump example](./docs/hex_dump_example.md)

---

## Using the classes in kboot_classes.py

These classes are meant to model Kboot sectors (both bootloaders, both configurations, and firmwares).

see [kboot_classes_example](./docs/kboot_classes_example.md)

---

## Older and mostly-redundant informational links

Before this repo was created, my k210 SPI Flash explorations were documented in the following gists:

* [k210_flash](https://gist.github.com/jdlcdl/a01dbf21771516581b4ccfda49622293)
* [krux_under_the_hood](https://gist.github.com/jdlcdl/a8a750500e6715772c395f78c870c109)
* [krux_firmware_overflow](https://gist.github.com/jdlcdl/5d5202d5b010ad3cbf3bab1b209e1992)
* [krux_upgrade_v22_to_v23](https://gist.github.com/jdlcdl/f3c5225efa55d1d0b02bad6b46930cb1)

