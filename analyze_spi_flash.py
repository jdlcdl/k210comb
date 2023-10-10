def analyze_spi_flash(verbose=False):
    '''
    Analyze the entirety of SPI flash

    assumes that utils.flash_read() behaves as if imported from Maix
    '''

    from binascii import hexlify

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
    be_verbose('ktool_sector', 'SPI Flash Filing System', hex(cursor), hex(cursor+_size))
    _hash = hash_flash(cursor, _size, verbose=decremented_bool(verbose))
    if len(_hash) == 32:
         valid, bytes_read = True, _size
    be_verbose('filesizehash', 'SPI Flash Filing System', _size, hexlify(_hash).decode())
    assert valid and bytes_read, 'hashing SPIFFS'
    cursor += bytes_read

    # hash entirety of SPI flash
    be_verbose('ktool_sector', 'SPI flash', hex(0x0), hex(spi_flash_size))
    _hash = hash_flash(0x0, spi_flash_size, verbose=decremented_bool(verbose))
    be_verbose('filesizehash', '16MB SPI flash', spi_flash_size, hexlify(_hash).decode())

