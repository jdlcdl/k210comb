# Running the analyze_spi_flash() function

...from inside the k210 device console
```
minicom -D /dev/ttyUSB1 -b 115200
```

The goal of the analyze_spi_flash() function is to analyze every byte of SPI Flash on a k210 device.  It is still
a work in progress, and can only hint where there might be suspicious sections to further inspect -- via hex dump.

We'll connect to the k210 device console over usb, interrupt krux with `<ctrl>-c`, then we'll get ready to copy/paste.

We need to stop the watchdog timer and import utils from the Maix package.
```
from machine import WDT
WDT().stop()
from Maix import utils
```

We need to copy/paste the contents of the files below.
* decremented_bool.py: because the tools use this to reduce verbosity as functions call deeper functions.
* hash_flash.py: because some of the tools need to hash bytes from SPI Flash.
* all_bytes_are.py: because some of the tools need to verify that entire sectors are wiped clean.
* validate_aes_size_app_sha_nulpad.py: because Kboot sectors have a particular format in SPI Flash.
* analyze_spi_flash.py: because this is the function we're about to run for our SPI Flash report.

<details>
<summary>copy/paste this python code</summary>

```python
def decremented_bool(value):
    '''
    returns value as a bool, or as value-1 when value >0

    used to decrement verbosity as functions call other functions.
    '''

    if type(value) == int:
        if value > 0:
            return value - 1

        elif value == 0:
            return False

        else:
            raise TypeError('if value is <int>, must be >= 0: found %d' % value)

    elif type(value) == bool:
        return value

    else:
        raise TypeError('value must be <int> >= 0 or <bool> found %s' % value)

def hash_flash(begin=0x00, length=2**24, block_size=2**12, verbose=False):
    '''
    SHA256 Hash of the entirety, or from begin to begin+length, of SPI Flash memory

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

    from math import ceil
    from hashlib import sha256
    from binascii import hexlify

    assert block_size % block_size == 0, 'block_size must be divisible by 4096'
    _hash = sha256()

    if verbose:
        print('Hashing %s bytes of flash at %s...' % (length, hex(begin)), end='')

    bytes_read = 0
    while bytes_read < length:
        if bytes_read + block_size < length:
            _hash.update(utils.flash_read(begin+bytes_read, block_size))
            bytes_read += block_size
        else:
            _hash.update(utils.flash_read(begin+bytes_read, length-bytes_read))
            bytes_read += length - bytes_read

        if verbose:
            print('.', end='')

    answer = _hash.digest()

    if verbose:
        print('\nsha256 of %s bytes at %s:\n%s' % (bytes_read, hex(begin), hexlify(answer).decode()
        ))

    return answer

def all_bytes_are(byte, begin, length, block_size=2**12, verbose=False):
    '''
    returns True if all bytes in SPI Flash, between begin and begin+length,
    are the same as byte, otherwise False.

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

    from binascii import hexlify

    answer = True

    if verbose:
        print("Checking if %s bytes of flash at %s are all 0x%s..." % (
            length, hex(begin), hexlify(byte).decode()), end='')

    bytes_read = 0
    while bytes_read < length:
        if bytes_read + block_size < length:
            if utils.flash_read(begin+bytes_read, block_size) != byte * block_size:
                answer = False
                break
            bytes_read += block_size
        else:
            if utils.flash_read(begin+bytes_read, length-bytes_read) != byte * (length - bytes_read):
                answer = False
                break
            bytes_read += length - bytes_read

        if verbose:
            print('.', end='')

    if verbose:
        print("\nthe %s bytes at %s are %s 0x%s." % (
            length, hex(begin), 'ALL' if answer else 'NOT all', hexlify(byte).decode()))

    return answer

def validate_aes_size_app_sha_nulpad(begin, verbose=False):
    '''
    Verify that a ktool "sector" is valid for standard sectors.

    When valid, this function returns: tuple(True, number of bytes read),
    else when invalid or something suspicious: tuple(None, number of bytes read).
    
    A valid standard kboot/ktool "sector" appears as follows:
    * It has a 5 byte header: 0x00 aes byte, 4 Byte little-endian size of application data,
    * followed by the application data for as many bytes as described in the header,
    * followed by the 32 byte big-endian sha256 hash of the header and the application data,
    * and then the rest of the bytes to pad a 4096 or 65536 block-size are 0x00 filled,
      these nul bytes are not part of the kboot/ktool specificiation, but if they are not
      all zero-filled here, then this function will return (None, number of bytes read),
      because it implies that something unknown/unexplained has been written to this empty 
      space, which is suspicious.

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

    from binascii import hexlify

    sectors = {
        # address, block_size, sector_name
        0x0: (0x1000, 'Kboot stage-0'),
        0x1000: (0x1000, 'Kboot stage-1'),
        0x80000: (0x10000, 'firmware slot1'),
        0x280000: (0x10000, 'firmware slot2'),
    }
    bytes_read = 0

    if verbose:
        print('Validating sector format (aes+size+app+sha+nulpad) at %s...' % hex(begin))

    if begin not in sectors:
        if verbose:
            print('%s not in %s.' % (begin, sectors))
        return None, bytes_read
    block_size, sector_name = sectors[begin]
    if verbose:
        print('sector known as "%s", will use blocks_size %s,' % (sector_name, block_size))

    header = utils.flash_read(begin, 5)
    bytes_read += 5
    if not header[0] == 0x00:
        if verbose:
            print('first (aes) byte of header 0x%s is not 0x00.' % (hexlify(header).decode()))
        return None, bytes_read
    length = int.from_bytes(header[1:5], 'little')
    bytes_read += length
    if verbose:
        print('header indicates %s bytes of data,' % length)

    hash_suffix = utils.flash_read(begin+5+length, 32)
    bytes_read += 32
    _hash = hash_flash(begin, length=5+length, block_size=block_size, verbose=decremented_bool(verbose))
    if _hash != hash_suffix:
        if verbose:
            print('hash of %s bytes of header+data does not match suffix:\n  suffix: %s\n   found: %s' % (
                 5+length, hexlify(hash_suffix).decode(), hexlify(_hash).decode()))
            hash_flash(begin + 5, length, block_size=block_size, verbose=1)
        return None, bytes_read
    if verbose:
        print('sha256(header + data) == suffix, is expected format for this sector,')

    partial = (5 + length + 32) % block_size
    if partial:
        padding = block_size - partial
        if not all_bytes_are(b'\x00', begin+5+length+32, block_size-partial, verbose=decremented_bool(verbose)):
            if verbose:
                print('%s bytes to pad rest of sector are not all 0x00 bytes.' % padding)
            return None, bytes_read
        bytes_read += padding
        if verbose:
            print('%s bytes to pad rest of sector are ALL 0x00 bytes.' % padding)

    return True, bytes_read

def analyze_spi_flash(verbose=False):
    '''
    Analyze the entirety of SPI flash

    assumes that utils.flash_read() behaves as if imported from Maix
    '''

    from binascii import hexlify
    from os import listdir

    def ktool_app_size(address):
        size = int.from_bytes(utils.flash_read(address+1, 4), 'little')
        if size > 2**24 - address: return 0
        else: return size

    def be_verbose(msg='', *args):
        messages = {
            'ktool_sector': '\nChecking "%s" from %s to %s-1', # 3 args: name, start, end+1
            'validated': 'SPI flash from %s to %s-1 is %s.', # 3 args: start, end+1, 'valid'|'invalid'
            'hashed': 'sha256 hash of SPI flash from %s to %s-1 is:\n%s', # 3 args: start, end+1, hash
            'filesizehash': 'sha256 hash of "%s" having %s bytes is:\n%s', # 3 args: name, size, hash
        }
        if msg in messages and len(args):
            print(messages[msg] % args)
        else:
            print(msg)

    spi_flash_size = 2**24
    cursor = 0x0

    # 4096 bytes at 0x0 are of aes_size_app_sha format
    be_verbose('ktool_sector', 'Kboot stage-0', hex(cursor), hex(cursor+4096))
    valid, bytes_read = validate_aes_size_app_sha_nulpad(cursor, verbose=decremented_bool(verbose))
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'valid' if valid else 'INVALID')
    assert valid and bytes_read, 'checking "Kboot stage-0"'
    _size = ktool_app_size(cursor)
    _hash = hash_flash(cursor+5, _size, verbose=decremented_bool(verbose))
    be_verbose('filesizehash', 'bootloader_lo.bin', _size, hexlify(_hash).decode())
    cursor += bytes_read

    # 8192 bytes at 0x1000 are of aes_size_app_sha format and the next 4096 are 0xff
    be_verbose('ktool_sector', 'Kboot stage-1', hex(cursor), hex(cursor+12288))
    valid, bytes_read = validate_aes_size_app_sha_nulpad(cursor, verbose=decremented_bool(verbose))
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'valid' if valid else 'INVALID')
    assert valid and bytes_read, 'checking "Kboot stage-1"'
    _size = ktool_app_size(cursor)
    _hash = hash_flash(cursor+5, _size, verbose=decremented_bool(verbose))
    be_verbose('filesizehash', 'bootloader_hi.bin', _size, hexlify(_hash).decode())
    cursor += bytes_read

    valid = all_bytes_are(b'\xff', cursor, 4096, verbose=decremented_bool(verbose))
    if type(valid) == bool:
        bytes_read = 4096
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'all 0xff' if valid else 'NOT all 0xff!')
    assert valid and bytes_read, 'checking last third of "Kboot stage-1"'
    cursor += bytes_read

    # 4096 bytes at 0x4000 are main config
    be_verbose('ktool_sector', 'main config', hex(cursor), hex(cursor+4096))
    _hash = hash_flash(cursor, 4096, verbose=decremented_bool(verbose))
    if len(_hash) == 32:
        valid, bytes_read = True, 4096
    be_verbose('filesizehash', 'config.bin', 4096, hexlify(_hash).decode())
    assert valid and bytes_read, 'hashing "main config"'
    cursor += bytes_read

    # 4096 bytes at 0x5000 are config backup
    be_verbose('ktool_sector', 'backup config', hex(cursor), hex(cursor+4096))
    _other_hash = hash_flash(cursor, 4096, verbose=decremented_bool(verbose))
    if len(_hash) == 32:
        valid, bytes_read = True, 4096
    be_verbose('hashed', hex(cursor), hex(cursor+bytes_read), hexlify(_other_hash).decode())
    assert valid and bytes_read, 'hashing "backup config"'
    cursor += bytes_read

    # 40960 bytes at 0x6000 are reserved
    be_verbose('ktool_sector', 'reserved', hex(cursor), hex(cursor+40960))
    valid = all_bytes_are(b'\xff', cursor, 40960, verbose=decremented_bool(verbose))
    if type(valid) == bool:
        bytes_read = 40960
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'all 0xff' if valid else 'NOT all 0xff!')
    assert valid and bytes_read, 'checking that "reserved" is unused'
    cursor += bytes_read

    # the first 0x70000 bytes are unused
    be_verbose('ktool_sector', 'unused app/user', hex(cursor), hex(cursor+0x70000))
    valid = all_bytes_are(b'\xff', cursor, 0x70000, verbose=decremented_bool(verbose))
    if type(valid) == bool:
        bytes_read = 0x70000
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'all 0xff' if valid else 'NOT all 0xff!')
    assert valid and bytes_read, 'checking that "app/user" is unused'
    cursor += bytes_read

    # variable bytes at firmware slot1 0x80000 are firmware
    valid, bytes_read = validate_aes_size_app_sha_nulpad(cursor, verbose=decremented_bool(verbose))
    be_verbose('ktool_sector', 'firmware_slot1', hex(cursor), hex(cursor+bytes_read))
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'valid' if valid else 'INVALID')
    _size = ktool_app_size(cursor)
    _hash = hash_flash(cursor+5, _size, verbose=decremented_bool(verbose))
    be_verbose('filesizehash', 'firmware.bin', _size, hexlify(_hash).decode())
    assert valid and bytes_read, 'checking firmware slot1'
    cursor += bytes_read

    # variable bytes up to firmware slot2 are unused
    _size = 0x280000 - cursor
    be_verbose('ktool_sector', 'unused app/user', hex(cursor), hex(cursor+_size))
    valid = all_bytes_are(b'\xff', cursor, _size, verbose=decremented_bool(verbose))
    if type(valid) == bool:
        bytes_read = _size
    be_verbose('validated', hex(cursor), hex(cursor+_size), 'all 0xff' if valid else 'NOT all 0xff!')
    assert valid and bytes_read, 'checking that "app/user" is unused'
    cursor += bytes_read

    # variable bytes at firmware slot2 0x280000 are firmware
    valid, bytes_read = validate_aes_size_app_sha_nulpad(cursor, verbose=decremented_bool(verbose))
    be_verbose('ktool_sector', 'firmware_slot2', hex(cursor), hex(cursor+bytes_read))
    be_verbose('validated', hex(cursor), hex(cursor+bytes_read), 'valid' if valid else 'INVALID')
    if valid:
        _size = ktool_app_size(cursor)
        _hash = hash_flash(cursor+5, _size, verbose=decremented_bool(verbose))
        be_verbose('filesizehash', 'firmware.bin', _size, hexlify(_hash).decode())
        cursor += bytes_read

    # bytes between firmware and spiffs are unused
    _size = 0xd00000 - cursor
    be_verbose('ktool_sector', 'unused app/user', hex(cursor), hex(cursor+_size))
    valid = all_bytes_are(b'\xff', cursor, _size, verbose=decremented_bool(verbose))
    if type(valid) == bool:
        bytes_read = _size
    be_verbose('validated', hex(cursor), hex(cursor+_size), 'all 0xff' if valid else 'NOT all 0xff!')
    assert valid and bytes_read, 'checking that "app/user" is unused'
    cursor += bytes_read

    # 0x300000 spiffs bytes at 0xD00000
    _size = 0x300000
    be_verbose('ktool_sector', 'SPI Flash File System', hex(cursor), hex(cursor+_size))
    be_verbose('listdir("/flash"): {}'.format(listdir('/flash')))
    _hash = hash_flash(cursor, _size, verbose=decremented_bool(verbose))
    if len(_hash) == 32:
        valid, bytes_read = True, _size
    be_verbose('filesizehash', 'SPI Flash File System', _size, hexlify(_hash).decode())
    assert valid and bytes_read, 'hashing SPIFFS'
    cursor += bytes_read

    # hash entirety of SPI flash
    be_verbose('ktool_sector', 'SPI flash', hex(0x0), hex(spi_flash_size))
    _hash = hash_flash(0x0, spi_flash_size, verbose=decremented_bool(verbose))
    be_verbose('filesizehash', '16MB SPI flash', spi_flash_size, hexlify(_hash).decode())

```
</details>

If it went well, we didn't see any syntax errors after hitting `<CTRL>-d`, otherwise, we need to redo any failed copy/paste.

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

Back inside the k210 console, after interrupting krux, stopping the watchdog, importing utils, and copying/pasting these tools:
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

