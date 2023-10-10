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

