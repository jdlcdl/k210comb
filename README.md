# k210comb

#### SPI Flash inspection tools for Kendryte k210 based devices
---

Krux [the open-source-software project](https://github.com/selfcustody/krux) currently runs on various Kendryte K210 based devices, which all have 16MB of SPI Flash permanent storage.

The documentation and tools here are the result of curiosity to analyze this internal SPI Flash storage.
The tools can be run directly on a k210 device via usb-console, or they can be run against a flash_dump
that has been saved on another computer.

---

## Tools in this repository

The following tools may be cut/pasted into the k210 console w/`<CTRL>-e`, or they may be run on another computer
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

See [An introduction to Kboot](./intro_to_Kboot.md) if you are interested in erasing the entire SPI Flash.
This same document also explains how to get a flash_dump of your device, which is a good idea in case you are
hesitant about destroying information that might not be saved elsewhere.

---

## Getting familiar with krux via the k210 usb console

You may find [this gist](https://gist.github.com/jdlcdl/a8a750500e6715772c395f78c870c109), a work in progess,
interesting for getting familiar with the k210 device console and krux.

---

## Running the analyze_spi_flash() function from inside the k210 device console

The goal of the analyze_spi_flash() function is analyze every byte of SPI Flash on a k210 device.  It is still
a work in progress, and can only hint where there might be suspicious sections to further inspect -- via hex dump.

We'll connect to the k210 device console over usb, then we'll get ready to cut/paste.

We need to stop the watchdog timer and import utils from the Maix package.
```
from machine import WDT
WDT().stop()
from Maix import utils
```

This is going to feel like a real pain-in-the-@$$, but I don't know a better way to do it.  If you do, please share.

We need to cut and paste the contents of the files below.  Because the first three are small, we can cut/paste them together.
The last two are often problematic so it's best to cut/paste them one at a time:
* decremented_bool.py: because the tools use this to reduce verbosity as functions call deeper functions.
* hash_flash.py: because some of the tools need to hash bytes from SPI Flash.
* all_bytes_are.py: because some of the tools need to verify that entire sectors are wiped clean.
* validate_aes_size_app_sha_nulpad.py: because Kboot sectors have a particular format in SPI Flash.
* analyze_spi_flash.py: because this is the function we're about to run for our SPI Flash report.

If it went well, we didn't see any syntax errors after hitting `<CTRL>-d`, otherwise, we need to redo the cut/paste.

Now, we can call the analyze_spi_flash function:
```
analyze_spi_flash()
```

On a Maix Amigo, after starting with a clean slate, flashing `Kboot.kfpkg` from last-year's krux-v22.08.2, we'd see:
```
>>> analyze_spi_flash()

Checking "Kboot stage-0" from 0x0 to 0x1000-1
SPI flash from 0x0 to 0x1000-1 is valid.
sha256 hash of "bootloader_lo.bin" having 608 bytes is:
2e050a92efdcb172cb5c6f7cb0b669ba654d2d20219f810fd9fc543f7ef05c3e

Checking "Kboot stage-1" from 0x1000 to 0x4000-1
SPI flash from 0x1000 to 0x3000-1 is valid.
sha256 hash of "bootloader_hi.bin" having 8112 bytes is:
f005f7c8b13aa2719cad58492a8432f14b68b2f845b58e5b5e81ed6309be6172
SPI flash from 0x3000 to 0x4000-1 is all 0xff.

Checking "main config" from 0x4000 to 0x5000-1
sha256 hash of "config.bin" having 4096 bytes is:
c9b9c4adcabe9c353a907f44c101c3b29756b30762e4b282d87d2a92400e2198

Checking "backup config" from 0x5000 to 0x6000-1
sha256 hash of SPI flash from 0x5000 to 0x6000-1 is:
c9b9c4adcabe9c353a907f44c101c3b29756b30762e4b282d87d2a92400e2198

Checking "reserved" from 0x6000 to 0x10000-1
SPI flash from 0x6000 to 0x10000-1 is all 0xff.

Checking "unused app/user" from 0x10000 to 0x80000-1
SPI flash from 0x10000 to 0x80000-1 is all 0xff.

Checking "firmware_slot1" from 0x80000 to 0x230000-1
SPI flash from 0x80000 to 0x230000-1 is valid.
sha256 hash of "firmware.bin" having 1716288 bytes is:
5067429beb16bd0eac55401ea673f55f9cc97585b1a0607d64f8e5f486d4988b

Checking "unused app/user" from 0x230000 to 0x280000-1
SPI flash from 0x230000 to 0x280000-1 is all 0xff.

Checking "firmware_slot2" from 0x280000 to 0x280005-1
SPI flash from 0x280000 to 0x280005-1 is INVALID.

Checking "unused app/user" from 0x280000 to 0xd00000-1
SPI flash from 0x280000 to 0xd00000-1 is all 0xff.

Checking "SPI Flash File System" from 0xd00000 to 0x1000000-1
listdir("/flash"): []
sha256 hash of "SPI Flash File System" having 3145728 bytes is:
e945c6bf2b3bdcf927b19a24e911f0cac73fb39a95a606cb6c043e335433b118

Checking "SPI flash" from 0x0 to 0x1000000-1
sha256 hash of "16MB SPI flash" having 16777216 bytes is:
ee874f63fbeab613db997a60408c332848f619c833e27ef1778e85f2fd23c6fb
>>> 
```

This report is what a clean/unused device would look like.  If we were to unzip the kboot.kfpkg
file for krux release v22.08.2, we'd find that bootloader_lo.bin, bootloader_hi.bin, 
config.bin and firmware.bin all have the same file sizes and hashes as they do in
SPI Flash.  All other expected "gaps" in SPI Flash are set to 0xff, so nothing has been hidden 
there.  Further, nothing appears to be saved in the SPI Flash File System.

For the previous release, krux never wrote to SPI Flash (except during an airgapped upgrade), so we should be
able to use this version forever, and that last line of the report, where the entire SPI Flash is hashed, 
would NEVER change.  This might seem ideal to some... but, if you never looked -- if nobody looked, then how would 
anyone really know for sure?


## That was then, this is now (krux release v23.09.0)

Since we CAN look, as we just did, let's consider the convenience of using SPI Flash in a safe manner, and 
then check from time to time, to verify that no unexplained bytes have been hidden in permanent storage.

As of release v23.09.0, krux does store settings.json in the SPI Flash File System.  As well, it can optionally
store encrypted mnemonics there too.

Next, We'll perform an airgapped-upgrade to krux release v23.09.0, change some settings, store one encrypted 
mnemonic in flash, then we'll take another look -- repeating the cut/paste steps above.

