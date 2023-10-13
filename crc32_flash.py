def crc32_flash(begin=0x00, length=2**24, block_size=2**12, verbose=False):
    '''
    Calculate the CRC32 of the entirety, or from begin to begin+length, of SPI Flash memory

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

    from binascii import hexlify, crc32

    assert block_size % block_size == 0, 'block_size must be divisible by 4096'
    checksum = 0

    if verbose:
        print('Calculating CRC32 for %s bytes of flash at %s...' % (length, hex(begin)), end='')

    bytes_read = 0
    while bytes_read < length:
        if bytes_read + block_size < length:
            checksum = crc32(utils.flash_read(begin+bytes_read, block_size), checksum)
            bytes_read += block_size
        else:
            checksum = crc32(utils.flash_read(begin+bytes_read, length-bytes_read), checksum)
            bytes_read += length - bytes_read

        if verbose:
            print('.', end='')

    if verbose:
        print('\nCRC32 of %s bytes at %s:\n%s' % (bytes_read, hex(begin), checksum))

    return checksum

