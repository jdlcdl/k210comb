# k210comb
---

Krux [the open-source-software project](https://github.com/selfcustody/krux) 
currently runs on various Kendryte K210 based devices, which all have 16MB of SPI Flash permanent storage.

The documentation and tools here are the result of curiosity to analyze this internal SPI Flash storage.
The tools can be run directly on a k210 device via usb-console, or they can be run against a flash_dump
that has been saved on another computer.

---

## Getting familiar with krux via the K210 usb console

You may find [this gist](https://gist.github.com/jdlcdl/a8a750500e6715772c395f78c870c109), a work in progess,
interesting for getting familiar with the k210 device console and krux.

---

## Tools in this repository

The following tools may be cut/pasted into the K210 console w/`<CTRL>-e`, or they may be run on another computer
against `/tmp/k210.flash_dump` assuming that file was previously saved from a k210 device.

* [wdt_pause.py](./wdt_pause.py): 
stops both watchdog timers (even if they are not running) so the device doesn't auto-reboot.

* [mocked_Maix_utils.py](./mocked_Maix_utils.py):
ensures that `utils.flash_read()` is available, because tools here need it.

* [decremented_bool.py](./decremented_bool.py):
used to decrement verbosity for functions that call other functions.

* [hash_flash.py](./hash_flash.py):
returns the sha256 hash of bytes in flash.

* [all_bytes_are.py](./all_bytes_are.py):
returns true if bytes in flash are the same as the one passed in.

* [validate_aes_size_app_sha_nulpad.py](./validate_aes_size_app_sha_nulpad.py):
used to validate a kboot/ktool sector.

* [analyze_spi_flash.py](./analyze_spi_flash.py):
using above tools, analyzes the entirety of SPI Flash, verbosely printing its findings.

* [hex_dump.py](./hex_dump.py):
a kludgy-yet-versatile implementation of hex_dump for visually inspecting bytes in flash.

