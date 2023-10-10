# Running the analyze_spi_flash() function

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
See [hex_dump example](./hex_dump_example.md)

