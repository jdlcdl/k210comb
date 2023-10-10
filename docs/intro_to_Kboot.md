# An introduction to Kboot

### ktool.py is a flexible tool for flashing k210 devices

Krux assumes that devices are flashed using Kboot.  In a nutshell, devices using KBoot have the following 4096-byte aligned sectors:
* `Kboot stage0` located at 0x0 to 0xfff (4096 bytes), just enough to get the device started and to load...
* `Kboot stage1` located at 0x1000 to 0x3fff (12288 bytes) which gets the device running just enough to read a flexible...
* `main configuration` located at 0x4000 to 0x4fff (4096 bytes) which has up to 8 configurations with pointers for up to 8 different firmwares.
* `backup configuration` located at 0x5000 to 0x5fff (4096 bytes) in case the main configuration were to get corrupted.
* `primary firmware` located at 0x80000 which Kboot loads into sram and uses to boot the device.

Krux could actually run without Kboot if we were to flash the primary firmware to address 0x0... but it would lose all of the
capabilities of a flexible multi-firmware boot that Kboot offers.  Since krux allows for air-gapped upgrades and does so by
adding another firmware slot for the upgrade, it is imperative that devices use Kboot -- and that developers respect the Kboot
layout, else there will be temporary `bricks` out in the wild.

Kboot/ktool/ktool.py/ktool.exe -- they're all the same thing.  If you've cloned the krux repo locally
as `~/krux` and built firmware at least once, then this tool will be available as `~/krux/firmware/Kboot/build/ktool.py`,
else the repository can be found [here](https://github.com/loboris/Kboot).

---

Note: for the below commands, they assume you're in a local krux repo like `~/krux` and you've already done a `./krux build maixpy_device_name` so that `./build/firmware.bin` and `./build/kboot.kfpkg` exist.  If this is the case, your environment is either already setup, or you prefix python commands w/ `poetry run python`; however you do it, do it below as well.

All commands below assume that $BOARD is set:
```
export BOARD=dan    # for maixpy_dock
export BOARD=goE    # for other boards
```

---

### To save a flash_dump from a k210 device to a computer
If you want a flash dump into `/tmp/k210.flash_dump`, (for a brick, or new install, or just for analyzing SPI Flash):
```
./firmware/Kboot/build/ktool.py -B $BOARD -R -a 0x0 -L 0x1000000 /tmp/k210.flash_dump
```
note: default baud rate is slow, this will take ~30m; faster baud rates are problematic in my experience.

---

### To completely erase SPI Flash on a k210 device (creating a temporary brick)
To erase the entire 16MB of SPI Flash, efficiently setting all bytes to `0xff`, for a clean slate:
```
./firmware/Kboot/build/ktool.py -B $BOARD -b 1500000 -E
```

---

### To completely install Kboot and firmware onto a k210 device
To install everything (Kboot stages 0 and 1, main and backup config, and firmware into slot1):
```
./firmware/Kboot/build/ktool.py -B $BOARD -b 1500000 ./build/kboot.kfpkg
```

---

### To install ONLY firmware to a particular slot on a k210 device
To install ONLY firmware.bin into slot1, without touching the `main config` which might be pointing to slot2:
```
./firmware/Kboot/build/ktool.py -B $BOARD -b 1500000 -a 0x80000 ./build/firmware.bin
```
or into slot2:
```
./firmware/Kboot/build/ktool.py -B $BOARD -b 1500000 -a 0x280000 ./build/firmware.bin
```

---

### To boot firmware w/o touching SPI Flash on a k210 device
To boot a new firmware w/o modifying SPI Flash (given settings are not changed, else SPIFFS will be touched), so that you can temporarily test a new firmware on your device (until reset or power-off):
```
./firmware/Kboot/build/ktool.py -B $BOARD -b 1500000 -s ./build/firmware.bin
```

