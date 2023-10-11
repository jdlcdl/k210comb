# k210comb

#### SPI Flash inspection tools for Kendryte k210 based devices
---

Krux [the open-source-software project](https://github.com/selfcustody/krux) currently runs on various Kendryte K210 based devices, which all have 16MB of SPI Flash permanent storage.

The documentation and tools here are the result of curiosity to analyze this internal SPI Flash storage.
The tools can be run directly on a k210 device via usb-console, or they can be run against a flash_dump
that has been saved on another computer.

---

## Tools in this repository

The following tools may be copy/pasted into the k210 console w/`<CTRL>-e`, or they may be run on another computer
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

---

## Starting with a clean slate

We could just get started inspecting our device as it is, but assuming we've been using it,
or that it was already setup when it was acquired, there is no telling what might be installed in SPI Flash.
In order to have realistic expectations of what is installed, and assuming that there is nothing important
like encrypted mnemonics that we don't have backed-up elsewhere, we can start with a clean slate.

See [An introduction to Kboot](./docs/intro_to_Kboot.md) if you are interested in erasing the entire SPI Flash.
This same document also explains how to get a flash_dump of your device, which is a good idea in case you are
hesitant about destroying information that might not be saved elsewhere.

---

## Getting familiar with krux via the k210 usb console

See [Intro to krux on k210 based Amigo](./docs/intro_to_krux_on_amigo.md)

---

## Running the analyze_spi_flash() function

See [analyze_spi_flash example](./docs/analyze_spi_flash_example.md)

---

## Using the hex_dump tool

See [hex_dump example](./docs/hex_dump_example.md)

