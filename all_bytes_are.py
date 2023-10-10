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

