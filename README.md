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

## Running the analyze_spi_flash() function

...from inside the k210 device console

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

On a Maix Amigo, after starting with a clean slate, flashing `Kboot.kfpkg` from last-year's 
[krux release v22.08.2](https://github.com/selfcustody/krux/releases/tag/v22.08.2), we'd see:
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
file for krux release v22.08.2, we'd find that `bootloader_lo.bin`, `bootloader_hi.bin`, 
`config.bin` and `firmware.bin` all have the same file sizes and hashes as they do in
SPI Flash.  All other expected "gaps" in SPI Flash are set to 0xff, so nothing has been hidden 
there.  Further, nothing appears to be saved in the SPI Flash File System.  The only "INVALID" note
indicates that there is nothing stored in firmware_slot2 and the report picks up from that point to verify
that the rest of that space is nothing but empty/0xff bytes.

For the previous release, krux never wrote to SPI Flash (except during an airgapped upgrade), so we should be
able to use this version forever, and that last line of the report where the entire SPI Flash is hashed, 
would NEVER change.  This might seem ideal to some... but, if you never looked -- if nobody ever looked, 
then how would anybody really know for sure?

### That was then, this is now (krux release v23.09.0)

Since we CAN look, as we just did, let's consider the convenience of using SPI Flash in a safe manner, and 
then check from time to time, to verify that no unexplained bytes have been hidden in permanent storage.

As of [krux release v23.09.0](https://github.com/selfcustody/krux/releases/tag/v23.09.0),
krux does store `settings.json` in the SPI Flash File System.  As well, it can optionally
store encrypted mnemonics there too.

Next, We'll perform an airgapped-upgrade to krux release v23.09.0, change some settings, store one encrypted 
mnemonic in flash, then we'll take another look -- repeating all of the console steps above.  Additionally, we'll
dig into a few sections of SPI Flash which changed using the hex_dump tool, so that we can explain those changes.

An airgapped upgrade involves dropping `firmware.bin` and `firmware.bin.sig` on a vfat-formatted microsd card, 
inserting it into the k210 device, booting and selecting to upgrade, then removing the microsd card before rebooting.  
See [the docs](https://selfcustody.github.io/krux/getting-started/installing/from-pre-built-release/#upgrade-via-microsd-card)
for more information.

Now that the k210 device has been airgap-upgraded, we'll be expecting the main configuration to have changed so that it
points to the new firmware in the firmware_slot2.  As well, we'll be expecting to see `settings.json` in SPIFFS since that's
a feature of krux release v23.09.0.  To reinforce a good habit whenever messing around like we are, we'll make one Settings 
change for the "network", from "main" to "test".

To add to this exercise, I'll create a 12 word seed and store it encrypted in "/flash", so that we can see what it looks like later.
While we can change the number of pbkdf2 iterations used, I'll stick to the default 100,000 iterations, and I'll also keep
the default encryption mode as AES-ECB.  I've created a throw-away 12-word seed w/ mnemonic:
`acquire obvious bean still radar topple boss sting stock valid donkey melt` 
without a bip-39 passphrase, resulting in a bip-32 master fingerprint of "f91a61f7".  I've chosen to store it, 
encrypted in flash, using key "abc".

Back inside the k210 console, after interrupting krux, stopping the watchdog, importing utils, and cutting/pasting these tools:
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
7d454bbe28244529f4bca414883a208b60f860b00cdaf8ab50bc4fafa038819c

Checking "backup config" from 0x5000 to 0x6000-1
sha256 hash of SPI flash from 0x5000 to 0x6000-1 is:
c9b9c4adcabe9c353a907f44c101c3b29756b30762e4b282d87d2a92400e219

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

Checking "firmware_slot2" from 0x280000 to 0x460000-1
SPI flash from 0x280000 to 0x460000-1 is valid.
sha256 hash of "firmware.bin" having 1902592 bytes is:
2da65b95435eff19a10fb0d88479bd7a7a86134577a972ab9012790dcac7e3c9

Checking "unused app/user" from 0x460000 to 0xd00000-1
SPI flash from 0x460000 to 0xd00000-1 is all 0xff.

Checking "SPI Flash File System" from 0xd00000 to 0x1000000-1
listdir("/flash"): ['settings.json', 'seeds.json']
sha256 hash of "SPI Flash File System" having 3145728 bytes is:
a0846cdfae30d742a2fc52129a5b6d9c9192dbe4bf58af52b7302294240b31ff

Checking "SPI flash" from 0x0 to 0x1000000-1
sha256 hash of "16MB SPI flash" having 16777216 bytes is:
8f9910c0a1f858020de9332880f4ab294b488192f4e1695a0a823a2bd03fe10f
>>>
```

As a quick summary, much remains the same, but there are some new changes:
* Kboot stages 0 and 1 are exactly the same,
* main config has been changed, 
* backup config has NOT changed,
* primary firmware_slot1 has NOT changed, it still has krux release v22.08.2's `firmware.bin`,
* there is something new in firmware_slot2. It's valid and it has the hash of krux release v23.09.0's `firmware.bin`,
* there are two new files in the SPI Flash File System, `settings.json` and `seeds.json`.

We were expecting all of these changes.  Shall we trust? Or shall we verify?

---

## Digging into the k210 SPI Flash via hex_dump

While inside the k210 console, cut and paste the contents of `hex_dump.py`.
This assumes that you've previously stopped the watchdog and imported utils from Maix, if not, see above.

`HexDumpSPIFlash` is a class that must first be instantiated, then you can call the instance's `run()` method.
While it's running, you are limited to the following commands, which are submitted once you hit `<enter>`:
* `j <enter>`: moves one screen down
* `k <enter>`: moves one screen up (this will get stuck when "squeeze" is toggled on!)
* `l <enter>`: will prompt you for a number of lines, and then will adjust screen height
* `w <enter>`: will prompt you for a number of bytes, and then will adjust screen width
* `s <enter>`: will toggle "squeeze" on or off
* `/ <enter>`: will prompt you for an address (if entering a hex address, must prefix with "0x")
* `q <enter>`: to quit the run() method.


## The main configuration changed

let's take a hex dump, and try to explain it.

```
>>> hd = HexDumpSPIFlash(0x4000, width=16, lines=25)
>>> hd.run()
004000  5a a5 d0 cd  00 28 00 00  00 1d 08 00  24 c6 ab aa  |Z....(......$...|
004010  66 69 72 6d  77 61 72 65  00 00 00 00  00 00 00 00  |firmware........|
004020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 14 squeezed
004110  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
004120  5a a5 d0 cf  00 00 00 00  00 00 00 00  00 00 00 00  |Z...............|
004130  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 235 squeezed
004ff0  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
005000  5a a5 d0 c5  00 08 00 00  00 1a a0 00  24 c6 ab aa  |Z...........$...|
005010  66 69 72 6d  77 61 72 65  00 00 00 00  00 00 00 00  |firmware........|
005020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 14 squeezed
005110  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
005120  5a a5 d0 cf  00 00 00 00  00 00 00 00  00 00 00 00  |Z...............|
005130  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 235 squeezed
005ff0  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
006000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 31230 squeezed
07fff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
080000  00 40 30 1a  00 21 a8 ef  be ad de 01  00 01 00 00  |.@0..!..........|
080010  00 00 00 00  00 00 00 00  00 00 00 00  00 73 50 30  |.............sP0|
080020  30 73 50 20  30 73 50 40  30 73 50 40  34 97 02 00  |0sP 0sP@0sP@4...|
080030  00 93 82 82  0f 73 90 52  30 81 40 01  41 81 41 01  |.....s.R0.@.A.A.|
```

Since "squeeze" is on by default, we can see both the main configuration (at 0x4000) and the backup (at 0x5000).

To make it easier to read, I'll cut/paste the only line that changed in the main config, over the original line from the backup config.
```
004000  5a a5 d0 cd  00 28 00 00  00 1d 08 00  24 c6 ab aa  |Z....(......$...|
005000  5a a5 d0 c5  00 08 00 00  00 1a a0 00  24 c6 ab aa  |Z...........$...|
```

Docs are https://github.com/loboris/Kboot/blob/master/Kboot.md

Each config entry is 32 bytes, and Kboot supports 8 entries.

The first 4 bytes always start like "0x5aa5d0c*" and the last nible is a 4 bit mask called "Entry flags", they are
* 0001 = This is the ACTIVE flag, if set, this is the active configuration to use.
* 0010 = this is the CRC32 flag, if set, the app's calculated CRC32 value must match the configuration's CRC32 value.
* 0100 = This is the AES256 flag, if set, the app's calculated AES256 value must match after the application sha256 hash. 
* 1000 = this is the SIZE flag, if set, the app's size must match the configuration's size value.

We can see that main configuration has Entry flags of "D"=1101 (Check SIZE, Check AES256, Ignore CRC32, Is ACTIVE)
We can see its backup configuration had Entry flags of "5"=0101 (Ignore SIZE, Check AES256, Ignore CRC32, Is ACTIVE)

The next 4 bytes, as a big-endian int, are the location of the application in SPI Flash.
We can see that it was at 0x80000 in the backup config and that it is now at 0x280000 in main config.

The next 4 bytes, as a big-endian int, are the application size.  We can see that the backup config indicates the application size was 1744896 when up above we see that it was really 1716288, but because the configuration entry flag was "5"=0101, the highest SIZE flag was not set and there were no problems.  In the new configuration which uses "D"=1101, the highest SIZE flag is set and we have a matching size in configuration of 1902592 in slot 2.

The next 4 bytes are the application's CRC32 value, in both cases above they are 0x24c6abaa, but according to the configuration, they're not used and I don't know what they mean, just that they came from `config.bin` within the `kboot.kfpkg` archive.

The next 16 bytes are the application name or description, in our case, it's "firmware" follwed by 8 null bytes.


## The SPI Flash File System changed

Let's take a long hex dump, and try to explain it

If we're still in `hd.run()` we can hit `/ <enter>` to seek directly to SPIFFS at 0xd00000
```
...
080030  00 93 82 82  0f 73 90 52  30 81 40 01  41 81 41 01  |.....s.R0.@.A.A.|              /
Enter an address: 0xd00000
d00000  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|

d00010  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d00020  00 00 00 00  00 00 00 00  01 80 01 00  02 80 02 00  |................|
d00030  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 250 squeezed
d00fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d00ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  31 15 00 00  |............1...|
d01000  01 80 00 00  7e 00 00 00  2f 00 00 00  01 2f 73 65  |....~.../..../se|
d01010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d01020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d01070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d01080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 02 00  |................|
d01090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d01ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d02000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d02010  3a 20 7b 22  61 70 70 65  61 72 61 6e  63 65 22 3a  |: {"appearance":|
d02020  20 7b 22 74  68 65 6d 65  22 3a 20 22  44 61 72 6b  | {"theme": "Dark|
d02030  22 7d 7d 7d  ff ff ff ff  ff ff ff ff  ff ff ff ff  |"}}}............|
d02040  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 250 squeezed
d02ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d03000  01 80 00 00  7e 00 00 00  51 00 00 00  01 2f 73 65  |....~...Q..../se|
d03010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d03020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d03070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d03080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 04 00  |................|
d03090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d03ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d04000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d04010  3a 20 7b 22  74 6f 75 63  68 73 63 72  65 65 6e 22  |: {"touchscreen"|
d04020  3a 20 7b 22  74 68 72 65  73 68 6f 6c  64 22 3a 20  |: {"threshold": |
d04030  32 32 7d 2c  20 22 61 70  70 65 61 72  61 6e 63 65  |22}, "appearance|
d04040  22 3a 20 7b  22 74 68 65  6d 65 22 3a  20 22 44 61  |": {"theme": "Da|
d04050  72 6b 22 7d  7d 7d ff ff  ff ff ff ff  ff ff ff ff  |rk"}}}..........|
d04060  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 248 squeezed
d04ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d05000  01 80 00 00  7e 00 00 00  7b 00 00 00  01 2f 73 65  |....~...{..../se|
d05010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d05020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d05070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d05080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 06 00  |................|
d05090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d05ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d06000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d06010  3a 20 7b 22  61 70 70 65  61 72 61 6e  63 65 22 3a  |: {"appearance":|
d06020  20 7b 22 74  68 65 6d 65  22 3a 20 22  44 61 72 6b  | {"theme": "Dark|
d06030  22 7d 2c 20  22 6c 6f 67  22 3a 20 7b  22 70 61 74  |"}, "log": {"pat|
d06040  68 22 3a 20  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  |h": "/sd/.krux.l|
d06050  6f 67 22 2c  20 22 6c 65  76 65 6c 22  3a 20 39 39  |og", "level": 99|
d06060  7d 2c 20 22  69 31 38 6e  22 3a 20 7b  22 6c 6f 63  |}, "i18n": {"loc|
d06070  61 6c 65 22  3a 20 22 65  6e 2d 55 53  22 7d 7d 7d  |ale": "en-US"}}}|
d06080  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 246 squeezed
d06ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d07000  01 80 00 00  7e 00 00 00  9d 00 00 00  01 2f 73 65  |....~......../se|
d07010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d07020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d07070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d07080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 08 00  |................|
d07090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d07ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d08000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d08010  3a 20 7b 22  61 70 70 65  61 72 61 6e  63 65 22 3a  |: {"appearance":|
d08020  20 7b 22 74  68 65 6d 65  22 3a 20 22  44 61 72 6b  | {"theme": "Dark|
d08030  22 7d 2c 20  22 6c 6f 67  22 3a 20 7b  22 70 61 74  |"}, "log": {"pat|
d08040  68 22 3a 20  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  |h": "/sd/.krux.l|
d08050  6f 67 22 2c  20 22 6c 65  76 65 6c 22  3a 20 39 39  |og", "level": 99|
d08060  7d 2c 20 22  74 6f 75 63  68 73 63 72  65 65 6e 22  |}, "touchscreen"|
d08070  3a 20 7b 22  74 68 72 65  73 68 6f 6c  64 22 3a 20  |: {"threshold": |
d08080  32 32 7d 2c  20 22 69 31  38 6e 22 3a  20 7b 22 6c  |22}, "i18n": {"l|
d08090  6f 63 61 6c  65 22 3a 20  22 65 6e 2d  55 53 22 7d  |ocale": "en-US"}|
d080a0  7d 7d ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |}}..............|
d080b0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 243 squeezed
d08ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d09000  01 80 00 00  7e 00 00 00  bb 00 00 00  01 2f 73 65  |....~......../se|
d09010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d09020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d09070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d09080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 0a 00  |................|
d09090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d09ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0a000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d0a010  3a 20 7b 22  6c 6f 67 67  69 6e 67 22  3a 20 7b 22  |: {"logging": {"|
d0a020  6c 65 76 65  6c 22 3a 20  22 4e 4f 4e  45 22 7d 2c  |level": "NONE"},|
d0a030  20 22 74 6f  75 63 68 73  63 72 65 65  6e 22 3a 20  | "touchscreen": |
d0a040  7b 22 74 68  72 65 73 68  6f 6c 64 22  3a 20 32 32  |{"threshold": 22|
d0a050  7d 2c 20 22  61 70 70 65  61 72 61 6e  63 65 22 3a  |}, "appearance":|
d0a060  20 7b 22 74  68 65 6d 65  22 3a 20 22  44 61 72 6b  | {"theme": "Dark|
d0a070  22 7d 2c 20  22 6c 6f 67  22 3a 20 7b  22 70 61 74  |"}, "log": {"pat|
d0a080  68 22 3a 20  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  |h": "/sd/.krux.l|
d0a090  6f 67 22 2c  20 22 6c 65  76 65 6c 22  3a 20 39 39  |og", "level": 99|
d0a0a0  7d 2c 20 22  69 31 38 6e  22 3a 20 7b  22 6c 6f 63  |}, "i18n": {"loc|
d0a0b0  61 6c 65 22  3a 20 22 65  6e 2d 55 53  22 7d 7d 7d  |ale": "en-US"}}}|
d0a0c0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 242 squeezed
d0aff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0b000  01 80 00 00  7e 00 00 00  db 00 00 00  01 2f 73 65  |....~......../se|
d0b010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d0b020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d0b070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d0b080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 0c 00  |................|
d0b090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d0bff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0c000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d0c010  3a 20 7b 22  6c 6f 67 67  69 6e 67 22  3a 20 7b 22  |: {"logging": {"|
d0c020  6c 65 76 65  6c 22 3a 20  22 4e 4f 4e  45 22 7d 2c  |level": "NONE"},|
d0c030  20 22 62 69  74 63 6f 69  6e 22 3a 20  7b 22 6e 65  | "bitcoin": {"ne|
d0c040  74 77 6f 72  6b 22 3a 20  22 6d 61 69  6e 22 7d 2c  |twork": "main"},|
d0c050  20 22 74 6f  75 63 68 73  63 72 65 65  6e 22 3a 20  | "touchscreen": |
d0c060  7b 22 74 68  72 65 73 68  6f 6c 64 22  3a 20 32 32  |{"threshold": 22|
d0c070  7d 2c 20 22  61 70 70 65  61 72 61 6e  63 65 22 3a  |}, "appearance":|
d0c080  20 7b 22 74  68 65 6d 65  22 3a 20 22  44 61 72 6b  | {"theme": "Dark|
d0c090  22 7d 2c 20  22 6c 6f 67  22 3a 20 7b  22 70 61 74  |"}, "log": {"pat|
d0c0a0  68 22 3a 20  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  |h": "/sd/.krux.l|
d0c0b0  6f 67 22 2c  20 22 6c 65  76 65 6c 22  3a 20 39 39  |og", "level": 99|
d0c0c0  7d 2c 20 22  69 31 38 6e  22 3a 20 7b  22 6c 6f 63  |}, "i18n": {"loc|
d0c0d0  61 6c 65 22  3a 20 22 65  6e 2d 55 53  22 7d 7d 7d  |ale": "en-US"}}}|
d0c0e0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 240 squeezed
d0cff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0d000  01 80 00 00  7e 00 00 00  fd 00 00 00  01 2f 73 65  |....~......../se|
d0d010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d0d020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d0d070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d0d080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 0e 00  |................|
d0d090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d0dff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0e000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d0e010  3a 20 7b 22  62 69 74 63  6f 69 6e 22  3a 20 7b 22  |: {"bitcoin": {"|
d0e020  6e 65 74 77  6f 72 6b 22  3a 20 22 6d  61 69 6e 22  |network": "main"|
d0e030  7d 2c 20 22  6c 6f 67 22  3a 20 7b 22  70 61 74 68  |}, "log": {"path|
d0e040  22 3a 20 22  2f 73 64 2f  2e 6b 72 75  78 2e 6c 6f  |": "/sd/.krux.lo|
d0e050  67 22 2c 20  22 6c 65 76  65 6c 22 3a  20 39 39 7d  |g", "level": 99}|
d0e060  2c 20 22 61  70 70 65 61  72 61 6e 63  65 22 3a 20  |, "appearance": |
d0e070  7b 22 74 68  65 6d 65 22  3a 20 22 44  61 72 6b 22  |{"theme": "Dark"|
d0e080  7d 2c 20 22  74 6f 75 63  68 73 63 72  65 65 6e 22  |}, "touchscreen"|
d0e090  3a 20 7b 22  74 68 72 65  73 68 6f 6c  64 22 3a 20  |: {"threshold": |
d0e0a0  32 32 7d 2c  20 22 69 31  38 6e 22 3a  20 7b 22 6c  |22}, "i18n": {"l|
d0e0b0  6f 63 61 6c  65 22 3a 20  22 65 6e 2d  55 53 22 7d  |ocale": "en-US"}|
d0e0c0  2c 20 22 6c  6f 67 67 69  6e 67 22 3a  20 7b 22 6c  |, "logging": {"l|
d0e0d0  65 76 65 6c  22 3a 20 22  4e 4f 4e 45  22 7d 2c 20  |evel": "NONE"}, |
d0e0e0  22 70 65 72  73 69 73 74  22 3a 20 7b  22 6c 6f 63  |"persist": {"loc|
d0e0f0  61 74 69 6f  6e 22 3a 20  22 66 6c 61  73 68 22 7d  |ation": "flash"}|
d0e100  7d 7d ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |}}..............|
d0e110  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 237 squeezed
d0eff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d0f000  01 80 00 00  7e 00 00 00  2a 01 00 00  01 2f 73 65  |....~...*..../se|
d0f010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d0f020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d0f070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d0f080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 10 00  |................|
d0f090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d0fff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d10000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d10010  3a 20 7b 22  65 6e 63 72  79 70 74 69  6f 6e 22 3a  |: {"encryption":|
d10020  20 7b 22 70  62 6b 64 66  32 5f 69 74  65 72 61 74  | {"pbkdf2_iterat|
d10030  69 6f 6e 73  22 3a 20 31  30 30 30 30  30 7d 2c 20  |ions": 100000}, |
d10040  22 62 69 74  63 6f 69 6e  22 3a 20 7b  22 6e 65 74  |"bitcoin": {"net|
d10050  77 6f 72 6b  22 3a 20 22  6d 61 69 6e  22 7d 2c 20  |work": "main"}, |
d10060  22 6c 6f 67  22 3a 20 7b  22 70 61 74  68 22 3a 20  |"log": {"path": |
d10070  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  6f 67 22 2c  |"/sd/.krux.log",|
d10080  20 22 6c 65  76 65 6c 22  3a 20 39 39  7d 2c 20 22  | "level": 99}, "|
d10090  61 70 70 65  61 72 61 6e  63 65 22 3a  20 7b 22 74  |appearance": {"t|
d100a0  68 65 6d 65  22 3a 20 22  44 61 72 6b  22 7d 2c 20  |heme": "Dark"}, |
d100b0  22 74 6f 75  63 68 73 63  72 65 65 6e  22 3a 20 7b  |"touchscreen": {|
d100c0  22 74 68 72  65 73 68 6f  6c 64 22 3a  20 32 32 7d  |"threshold": 22}|
d100d0  2c 20 22 69  31 38 6e 22  3a 20 7b 22  6c 6f 63 61  |, "i18n": {"loca|
d100e0  6c 65 22 3a  20 22 65 6e  2d 55 53 22  7d 2c 20 22  |le": "en-US"}, "|
d100f0  6c 6f 67 67  69 6e 67 22  3a 20 7b 22  6c 65 76 65  |logging": {"leve|
d10100  6c 22 3a 20  22 4e 4f 4e  45 22 7d 2c  20 22 70 65  |l": "NONE"}, "pe|
d10110  72 73 69 73  74 22 3a 20  7b 22 6c 6f  63 61 74 69  |rsist": {"locati|
d10120  6f 6e 22 3a  20 22 66 6c  61 73 68 22  7d 7d 7d ff  |on": "flash"}}}.|
d10130  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 235 squeezed
d10ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d11000  01 80 00 00  7e 00 00 00  2a 01 00 00  01 2f 73 65  |....~...*..../se|
d11010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d11020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d11070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d11080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 12 00  |................|
d11090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d110a0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 244 squeezed
d11ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d12000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d12010  3a 20 7b 22  65 6e 63 72  79 70 74 69  6f 6e 22 3a  |: {"encryption":|
d12020  20 7b 22 70  62 6b 64 66  32 5f 69 74  65 72 61 74  | {"pbkdf2_iterat|
d12030  69 6f 6e 73  22 3a 20 31  30 30 30 30  30 7d 2c 20  |ions": 100000}, |
d12040  22 62 69 74  63 6f 69 6e  22 3a 20 7b  22 6e 65 74  |"bitcoin": {"net|
d12050  77 6f 72 6b  22 3a 20 22  6d 61 69 6e  22 7d 2c 20  |work": "main"}, |
d12060  22 6c 6f 67  22 3a 20 7b  22 70 61 74  68 22 3a 20  |"log": {"path": |
d12070  22 2f 73 64  2f 2e 6b 72  75 78 2e 6c  6f 67 22 2c  |"/sd/.krux.log",|
d12080  20 22 6c 65  76 65 6c 22  3a 20 39 39  7d 2c 20 22  | "level": 99}, "|
d12090  61 70 70 65  61 72 61 6e  63 65 22 3a  20 7b 22 74  |appearance": {"t|
d120a0  68 65 6d 65  22 3a 20 22  44 61 72 6b  22 7d 2c 20  |heme": "Dark"}, |
d120b0  22 74 6f 75  63 68 73 63  72 65 65 6e  22 3a 20 7b  |"touchscreen": {|
d120c0  22 74 68 72  65 73 68 6f  6c 64 22 3a  20 32 32 7d  |"threshold": 22}|
d120d0  2c 20 22 69  31 38 6e 22  3a 20 7b 22  6c 6f 63 61  |, "i18n": {"loca|
d120e0  6c 65 22 3a  20 22 65 6e  2d 55 53 22  7d 2c 20 22  |le": "en-US"}, "|
d120f0  6c 6f 67 67  69 6e 67 22  3a 20 7b 22  6c 65 76 65  |logging": {"leve|
d12100  6c 22 3a 20  22 4e 4f 4e  45 22 7d 2c  20 22 70 65  |l": "NONE"}, "pe|
d12110  72 73 69 73  74 22 3a 20  7b 22 6c 6f  63 61 74 69  |rsist": {"locati|
d12120  6f 6e 22 3a  20 22 66 6c  61 73 68 22  7d 7d 7d ff  |on": "flash"}}}.|
d12130  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 235 squeezed
d12ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d13000  01 80 00 00  7e 00 00 00  40 01 00 00  01 2f 73 65  |....~...@..../se|
d13010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d13020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d13070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d13080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 14 00  |................|
d13090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d13ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d14000  01 00 00 00  7e 7b 22 73  65 74 74 69  6e 67 73 22  |....~{"settings"|
d14010  3a 20 7b 22  65 6e 63 72  79 70 74 69  6f 6e 22 3a  |: {"encryption":|
d14020  20 7b 22 76  65 72 73 69  6f 6e 22 3a  20 22 41 45  | {"version": "AE|
d14030  53 2d 45 43  42 22 2c 20  22 70 62 6b  64 66 32 5f  |S-ECB", "pbkdf2_|
d14040  69 74 65 72  61 74 69 6f  6e 73 22 3a  20 31 30 30  |iterations": 100|
d14050  30 30 30 7d  2c 20 22 62  69 74 63 6f  69 6e 22 3a  |000}, "bitcoin":|
d14060  20 7b 22 6e  65 74 77 6f  72 6b 22 3a  20 22 6d 61  | {"network": "ma|
d14070  69 6e 22 7d  2c 20 22 6c  6f 67 22 3a  20 7b 22 70  |in"}, "log": {"p|
d14080  61 74 68 22  3a 20 22 2f  73 64 2f 2e  6b 72 75 78  |ath": "/sd/.krux|
d14090  2e 6c 6f 67  22 2c 20 22  6c 65 76 65  6c 22 3a 20  |.log", "level": |
d140a0  39 39 7d 2c  20 22 61 70  70 65 61 72  61 6e 63 65  |99}, "appearance|
d140b0  22 3a 20 7b  22 74 68 65  6d 65 22 3a  20 22 44 61  |": {"theme": "Da|
d140c0  72 6b 22 7d  2c 20 22 74  6f 75 63 68  73 63 72 65  |rk"}, "touchscre|
d140d0  65 6e 22 3a  20 7b 22 74  68 72 65 73  68 6f 6c 64  |en": {"threshold|
d140e0  22 3a 20 32  32 7d 2c 20  22 69 31 38  6e 22 3a 20  |": 22}, "i18n": |
d140f0  7b 22 6c 6f  63 61 6c 65  22 3a 20 22  65 6e 2d 55  |{"locale": "en-U|
d14100  53 22 7d 2c  20 22 6c 6f  67 67 69 6e  67 22 3a 20  |S"}, "logging": |
d14110  7b 22 6c 65  76 65 6c 22  3a 20 22 4e  4f 4e 45 22  |{"level": "NONE"|
d14120  7d 2c 20 22  70 65 72 73  69 73 74 22  3a 20 7b 22  |}, "persist": {"|
d14130  6c 6f 63 61  74 69 6f 6e  22 3a 20 22  66 6c 61 73  |location": "flas|
d14140  68 22 7d 7d  7d ff ff ff  ff ff ff ff  ff ff ff ff  |h"}}}...........|
d14150  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 233 squeezed
d14ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d15000  01 80 00 00  f8 00 00 00  40 01 00 00  01 2f 73 65  |........@..../se|
d15010  74 74 69 6e  67 73 2e 6a  73 6f 6e 00  00 00 00 00  |ttings.json.....|
d15020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d15070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d15080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 16 00  |................|
d15090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d15ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d16000  01 00 00 00  fc 7b 22 73  65 74 74 69  6e 67 73 22  |.....{"settings"|
d16010  3a 20 7b 22  65 6e 63 72  79 70 74 69  6f 6e 22 3a  |: {"encryption":|
d16020  20 7b 22 76  65 72 73 69  6f 6e 22 3a  20 22 41 45  | {"version": "AE|
d16030  53 2d 45 43  42 22 2c 20  22 70 62 6b  64 66 32 5f  |S-ECB", "pbkdf2_|
d16040  69 74 65 72  61 74 69 6f  6e 73 22 3a  20 31 30 30  |iterations": 100|
d16050  30 30 30 7d  2c 20 22 62  69 74 63 6f  69 6e 22 3a  |000}, "bitcoin":|
d16060  20 7b 22 6e  65 74 77 6f  72 6b 22 3a  20 22 74 65  | {"network": "te|
d16070  73 74 22 7d  2c 20 22 6c  6f 67 22 3a  20 7b 22 70  |st"}, "log": {"p|
d16080  61 74 68 22  3a 20 22 2f  73 64 2f 2e  6b 72 75 78  |ath": "/sd/.krux|
d16090  2e 6c 6f 67  22 2c 20 22  6c 65 76 65  6c 22 3a 20  |.log", "level": |
d160a0  39 39 7d 2c  20 22 61 70  70 65 61 72  61 6e 63 65  |99}, "appearance|
d160b0  22 3a 20 7b  22 74 68 65  6d 65 22 3a  20 22 44 61  |": {"theme": "Da|
d160c0  72 6b 22 7d  2c 20 22 74  6f 75 63 68  73 63 72 65  |rk"}, "touchscre|
d160d0  65 6e 22 3a  20 7b 22 74  68 72 65 73  68 6f 6c 64  |en": {"threshold|
d160e0  22 3a 20 32  32 7d 2c 20  22 69 31 38  6e 22 3a 20  |": 22}, "i18n": |
d160f0  7b 22 6c 6f  63 61 6c 65  22 3a 20 22  65 6e 2d 55  |{"locale": "en-U|
d16100  53 22 7d 2c  20 22 6c 6f  67 67 69 6e  67 22 3a 20  |S"}, "logging": |
d16110  7b 22 6c 65  76 65 6c 22  3a 20 22 4e  4f 4e 45 22  |{"level": "NONE"|
d16120  7d 2c 20 22  70 65 72 73  69 73 74 22  3a 20 7b 22  |}, "persist": {"|
d16130  6c 6f 63 61  74 69 6f 6e  22 3a 20 22  66 6c 61 73  |location": "flas|
d16140  68 22 7d 7d  7d ff ff ff  ff ff ff ff  ff ff ff ff  |h"}}}...........|
d16150  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 233 squeezed
d16ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d17000  02 80 00 00  f8 00 00 00  ae 00 00 00  01 2f 73 65  |............./se|
d17010  65 64 73 2e  6a 73 6f 6e  00 00 00 00  00 00 00 00  |eds.json........|
d17020  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
... 4 squeezed
d17070  00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00  |................|
d17080  00 00 00 00  00 00 00 00  00 00 00 00  00 00 18 00  |................|
d17090  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 245 squeezed
d17ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d18000  02 00 00 00  fc 7b 22 66  39 31 61 36  31 66 37 22  |.....{"f91a61f7"|
d18010  3a 20 7b 22  6b 65 79 5f  69 74 65 72  61 74 69 6f  |: {"key_iteratio|
d18020  6e 73 22 3a  20 31 30 30  30 30 30 2c  20 22 64 61  |ns": 100000, "da|
d18030  74 61 22 3a  20 22 79 48  4c 55 72 4d  76 65 37 55  |ta": "yHLUrMve7U|
d18040  4d 56 6e 58  37 6b 59 6d  36 73 64 63  74 39 69 6e  |MVnX7kYm6sdct9in|
d18050  51 56 53 75  62 6b 5a 69  30 61 33 30  59 32 57 4d  |QVSubkZi0a30Y2WM|
d18060  38 41 65 64  56 72 33 75  6a 67 37 47  49 59 57 77  |8AedVr3ujg7GIYWw|
d18070  37 30 4c 4e  50 4d 4b 2f  6d 57 79 35  74 74 69 65  |70LNPMK/mWy5ttie|
d18080  48 70 2f 49  61 68 71 55  39 6c 50 6f  39 32 36 65  |Hp/IahqU9lPo926e|
d18090  62 74 72 38  6a 4d 6e 53  77 44 4a 4d  70 5a 39 68  |btr8jMnSwDJMpZ9h|
d180a0  34 3d 22 2c  20 22 76 65  72 73 69 6f  6e 22 3a 20  |4=", "version": |
d180b0  30 7d 7d ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |0}}.............|
d180c0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 2289 squeezed
d20fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d20ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3e 15 00 00  |............>...|
d21000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
d40fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d40ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3f 15 00 00  |............?...|
d41000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
d60fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d60ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3c 15 00 00  |............<...|
d61000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
d80fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
d80ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3d 15 00 00  |............=...|
d81000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
da0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
da0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3a 15 00 00  |............:...|
da1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
dc0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
dc0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  3b 15 00 00  |............;...|
dc1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
de0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
de0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  38 15 00 00  |............8...|
de1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
e00fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e00ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  39 15 00 00  |............9...|
e01000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
e20fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e20ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  26 15 00 00  |............&...|
e21000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
e40fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e40ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  27 15 00 00  |............'...|
e41000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e41010  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8188 squeezed
e60fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e60ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  24 15 00 00  |............$...|
e61000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
e80fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
e80ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  25 15 00 00  |............%...|
e81000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
ea0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
ea0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  22 15 00 00  |............"...|
ea1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
ec0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
ec0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  23 15 00 00  |............#...|
ec1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
ee0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
ee0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  20 15 00 00  |............ ...|
ee1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
f00fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f00ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  21 15 00 00  |............!...|
f01000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f01010  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8188 squeezed
f20fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f20ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2e 15 00 00  |................|
f21000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
f40fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f40ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2f 15 00 00  |............/...|
f41000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
f60fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f60ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2c 15 00 00  |............,...|
f61000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
f80fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
f80ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2d 15 00 00  |............-...|
f81000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
fa0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
fa0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2a 15 00 00  |............*...|
fa1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8189 squeezed
fc0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
fc0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  2b 15 00 00  |............+...|
fc1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
fc1010  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 8188 squeezed
fe0fe0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
fe0ff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  28 15 00 00  |............(...|
fe1000  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
... 7934 squeezed
fffff0  ff ff ff ff  ff ff ff ff  ff ff ff ff  ff ff ff ff  |................|
```

Todo: Knowing the key is 'abc' and having iterations and encryption mode, decrypt the mnemonic.  Perhaps another day?
