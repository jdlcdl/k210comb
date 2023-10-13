def hash_flash(begin=0x00, length=2**24, block_size=2**12, verbose=False):
    '''
    SHA256 Hash of the entirety, or from begin to begin+length, of SPI Flash memory

    assumes that utils.flash_read() behaves as if imported from Maix,
    ie: `from Maix import utils`
    '''

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

