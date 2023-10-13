def hashcrc_flash(begin=0x00, length=2**24, block_size=2**12, verbose=False):
    '''
    SHA256 Hash and CRC32 of the entirety, or from begin to begin+length, of SPI Flash memory

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

    from hashlib import sha256
    from binascii import hexlify, crc32

    assert block_size % block_size == 0, 'block_size must be divisible by 4096'
    _hash = sha256()
    checksum = 0

    if verbose:
        print('Hashing and CRCsumming %s bytes of flash at %s...' % (length, hex(begin)), end='')

    bytes_read = 0
    while bytes_read < length:
        if bytes_read + block_size < length:
            some_bytes = utils.flash_read(begin+bytes_read, block_size)
        else:
            some_bytes = utils.flash_read(begin+bytes_read, length-bytes_read)
        _hash.update(some_bytes)
        checksum = crc32(some_bytes, checksum)
        bytes_read += len(some_bytes)

        if verbose:
            print('.', end='')

    answer = _hash.digest(), checksum

    if verbose:
        print('\n%s bytes at %s:\n sha256: %s\n crc32: %s' % (
            bytes_read, hex(begin), hexlify(answer[0]).decode(), answer[1]
        ))

    return answer

