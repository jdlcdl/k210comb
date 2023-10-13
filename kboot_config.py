'''
Kboot configuration classes

assumes that utils.flash_read() behaves as if imported from Maix:
ie: `from Maix import utils`
'''

from hashlib import sha256

class KbootConfigEntry:
    BASE_ENTRY_ID = 0x5aa5d0c0
    APP_ADDRESS_RANGE = (0x10000, 0x8000000)
    APP_SIZE_RANGE = (0x4000, 0x300000)

    def __init__(self, raw_bytes):
        if type(raw_bytes) == bytes and len(raw_bytes) == 32:
            self.parse(raw_bytes)
        else:
            raise ValueError('raw_bytes must be of type bytes and of length 32')
 
    def parse(self, raw_bytes):
        id_flags = int.from_bytes(raw_bytes[:4], 'big')
        if self.BASE_ENTRY_ID <= id_flags <= self.BASE_ENTRY_ID+16:
            self.is_active = bool(id_flags & 1)
            self.ck_crc32 = bool(id_flags & 2)
            self.ck_sha256 = bool(id_flags & 4)
            self.ck_size = bool(id_flags & 8)
        else:
            raise ValueError('First 28 bits of Entry ID must be {}'.format(
                hex(self.BASE_ENTRY_ID)[:-1]))

        app_address = int.from_bytes(raw_bytes[4:8], 'big')
        if self.APP_ADDRESS_RANGE[0] <= app_address <= self.APP_ADDRESS_RANGE[1]:
            self.app_address = app_address
        else:
            raise ValueError('Valid app address range is {} to {}'.format(
                *[hex(x) for x in self.APP_ADDRESS_RANGE]
            ))

        app_size = int.from_bytes(raw_bytes[8:12], 'big')
        if self.APP_SIZE_RANGE[0] <= app_size <= self.APP_SIZE_RANGE[1]:
            self.app_size = app_size
        else:
            raise ValueError('Valid app size range is {} to {} bytes'.format(
                *self.APP_SIZE_RANGE
            )) 

        self.app_crc32 = raw_bytes[12:16]
        self.app_name = raw_bytes[16:].decode('utf8')
        
        self.raw_bytes = raw_bytes

    def serialize(self):
        id_entry = self.BASE_ENTRY_ID
        if self.is_active: id_entry += 1
        if self.ck_crc32: id_entry += 2
        if self.ck_sha256: id_entry += 4
        if self.ck_size: id_entry += 8
        raw_bytes = id_entry.to_bytes(4, 'big')

        raw_bytes += self.app_address.to_bytes(4, 'big')
        raw_bytes += self.app_size.to_bytes(4, 'big')
        raw_bytes += self.app_crc32
        raw_bytes += (self.app_name.encode('utf8') + b'\x00'*16)[:16]

        return raw_bytes


class KbootConfigSector:
    MAIN_ADDRESS = 0x4000
    BACKUP_ADDRESS = 0x5000

    def __init__(self, raw_bytes, main=True):
        self.main = main

        if type(raw_bytes) == bytes and len(raw_bytes) == 4096:
            self.parse(raw_bytes)
        else:
            raise ValueError('raw_bytes must be of type bytes and of length 4096')

    def parse(self, raw_bytes):
        self.entries = []
        for i in range(0, 32*8, 32):
            try: self.entries.append(KbootConfigEntry(raw_bytes[i:i+32]))
            except: pass

        self.config_flags = int.from_bytes(raw_bytes[256:260], 'big')
        if self.config_flags == KbootConfigEntry.BASE_ENTRY_ID:
            self.interactive_disabled = True
        else:
            self.interactive_disabled = False

        self.reserved = raw_bytes[260:264]

        undocumented = raw_bytes[264:288]
        if undocumented == b'\x00'*24:
            self.undocumented = undocumented
        else:
            raise ValueError('24 bytes undocumented between reserved and user_data should be null')

        self.user_data = raw_bytes[288:292]

        padding = raw_bytes[292:]
        if padding == b'\x00'*3804:
            self.padding = padding
        else:
            raise ValueError('3804 bytes to end of sector should be null padded')

        self.raw_bytes = raw_bytes

    def serialize(self):
        raw_bytes = b''
        for i in range(8):
            if len(self.entries) > i:
                raw_bytes += self.entries[i].serialize()
            else:
                raw_bytes += b'\x00' * 32

        if self.interactive_disabled:
            raw_bytes += KbootConfigEntry.BASE_ENTRY_ID.to_bytes(4, 'big')
        else:
            raw_bytes += self.config_flags.to_bytes(4, 'big')

        raw_bytes += self.reserved
        raw_bytes += self.undocumented
        raw_bytes += self.user_data
        raw_bytes += self.padding

        return raw_bytes

    def sha256(self):
        return sha256(self.raw_bytes).digest()


if __name__ == '__main__':

    from binascii import hexlify, unhexlify

    configurations = {
        'main': KbootConfigSector(utils.flash_read(0x4000, 0x1000)),
        'backup': KbootConfigSector(utils.flash_read(0x5000, 0x1000))
    }

    for name, config in configurations.items():
        print(
            '\nconfig {}\n raw_bytes: {} (null padding trimmed)'.format(
                name, hexlify(config.raw_bytes[:-3804])
            ),
            '\n sha256: {}'.format(hexlify(config.sha256())),
            '\n num entries: {}'.format(len(config.entries)),
            '\n config_flags: {}, interactive_disabled: {}'.format(
                hexlify(config.config_flags.to_bytes(4, 'big')), config.interactive_disabled),
            '\n reserved: {}'.format(hexlify(config.reserved)),
            '\n undocumented: {}'.format(hexlify(config.undocumented)),
            '\n user_data: {}'.format(hexlify(config.user_data)),
            '\n length of null padding: {}'.format(len(config.padding))
        )

        for i, entry in enumerate(config.entries):
            print(
                '\nconfig.entry #{}\n raw_bytes : {}'.format(i, hexlify(entry.raw_bytes)),
                '\n is_active: {}, ck_crc32: {}, ck_sha256: {}, ck_size: {}'.format(
                     entry.is_active, entry.ck_crc32, entry.ck_sha256, entry.ck_size
                ),
                '\n app_address: {} {}'.format(entry.app_address, hex(entry.app_address)),
                '\n app_size: {} {}'.format(entry.app_size, hex(entry.app_size)),
                '\n app_crc32: {}'.format(hexlify(entry.app_crc32)),
                '\n app_name: {}'.format(entry.app_name)
            )
            assert entry.raw_bytes == entry.serialize()

        assert config.raw_bytes == config.serialize()
