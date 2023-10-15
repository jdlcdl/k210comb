'''
classes to model Kboot bootloader, configuration, and application sectors

assumes that utils.flash_read() behaves as if imported from Maix:
ie: `from Maix import utils`
'''


from binascii import crc32
from hashlib import sha256


class KbootConstants:
    STAGE0_ADDRESS = 0x0
    STAGE1_ADDRESS = 0x1000
    MAIN_CONFIG_ADDRESS = 0x4000
    BACKUP_CONFIG_ADDRESS = 0x5000
    BASE_CONFIG_ENTRY_ID = 0x5aa5d0c0
    APP_ADDRESS_RANGE = (0x10000, 0x800000)
    APP_SIZE_RANGE = (0x4000, 0x300000)


class KbootConfigEntry:
    def __init__(self, app_address, 
        is_active=True, 
        ck_crc32=False,
        ck_sha256=False,
        ck_size=False,
        app_size=KbootConstants.APP_SIZE_RANGE[0],
        app_crc32=0,
        app_name='firmware'
    ):
        if KbootConstants.APP_ADDRESS_RANGE[0] <= app_address <= KbootConstants.APP_ADDRESS_RANGE[1]:
            self.app_address = app_address
        else:
            raise ValueError('Valid app address range is {} to {}'.format(
                *[hex(x) for x in KbootConstants.APP_ADDRESS_RANGE]
            ))

        if KbootConstants.APP_SIZE_RANGE[0] <= app_size <= KbootConstants.APP_SIZE_RANGE[1]:
            self.app_size = app_size
        else:
            raise ValueError('Valid app size range is {} to {} bytes'.format(
                *KbootConstants.APP_SIZE_RANGE
            )) 

        self.is_active = bool(is_active)
        self.ck_crc32 = bool(ck_crc32)
        self.ck_sha256 = bool(ck_sha256)
        self.ck_size = bool(ck_size)
        self.app_crc32 = int(app_crc32)
        self.app_name = str(app_name)

    @classmethod
    def from_bytes(cls, raw_bytes):
        if type(raw_bytes) != bytes or len(raw_bytes) != 32:
            raise ValueError('raw_bytes must be of type bytes and of length 32')

        id_flags = int.from_bytes(raw_bytes[:4], 'big')
        if KbootConstants.BASE_CONFIG_ENTRY_ID <= id_flags <= KbootConstants.BASE_CONFIG_ENTRY_ID+16:
            is_active = bool(id_flags & 1)
            ck_crc32 = bool(id_flags & 2)
            ck_sha256 = bool(id_flags & 4)
            ck_size = bool(id_flags & 8)
        else:
            raise ValueError('First 28 bits of Entry ID must be {}'.format(
                hex(KbootConstants.BASE_CONFIG_ENTRY_ID)[:-1]))

        app_address = int.from_bytes(raw_bytes[4:8], 'big')
        app_size = int.from_bytes(raw_bytes[8:12], 'big')
        app_crc32 = int.from_bytes(raw_bytes[12:16], 'big')
        app_name = raw_bytes[16:].decode('utf8')

        return cls(
            app_address=app_address,
            is_active=is_active,
            ck_crc32=ck_crc32,
            ck_sha256=ck_sha256,
            ck_size=ck_size,
            app_size=app_size,
            app_crc32=app_crc32,
            app_name=app_name
        )

    def serialize(self):
        id_entry = KbootConstants.BASE_CONFIG_ENTRY_ID
        if self.is_active: id_entry += 1
        if self.ck_crc32: id_entry += 2
        if self.ck_sha256: id_entry += 4
        if self.ck_size: id_entry += 8
        raw_bytes = id_entry.to_bytes(4, 'big')

        raw_bytes += self.app_address.to_bytes(4, 'big')
        raw_bytes += self.app_size.to_bytes(4, 'big')
        raw_bytes += self.app_crc32.to_bytes(4, 'big')
        raw_bytes += (self.app_name.encode('utf8') + b'\x00'*16)[:16]

        return raw_bytes


class KbootConfigSector:
    def __init__(self, main=True):
        if main:
            raw_bytes = utils.flash_read(KbootConstants.MAIN_CONFIG_ADDRESS, 4096)
        else:
            raw_bytes = utils.flash_read(KbootConstants.BACKUP_CONFIG_ADDRESS, 4096)

        if type(raw_bytes) == bytes and len(raw_bytes) == 4096:
            self.parse(raw_bytes)
        else:
            raise ValueError('raw_bytes must be of type bytes and of length 4096')

    def parse(self, raw_bytes):
        self.entries = []
        for i in range(0, 32*8, 32):
            try: self.entries.append(KbootConfigEntry.from_bytes(raw_bytes[i:i+32]))
            except: pass

        self.config_flags = int.from_bytes(raw_bytes[256:260], 'big')
        if self.config_flags == KbootConstants.BASE_CONFIG_ENTRY_ID:
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
            raw_bytes += KbootConstants.BASE_CONFIG_ENTRY_ID.to_bytes(4, 'big')
        else:
            raw_bytes += self.config_flags.to_bytes(4, 'big')

        raw_bytes += self.reserved
        raw_bytes += self.undocumented
        raw_bytes += self.user_data
        raw_bytes += self.padding

        return raw_bytes

    def sha256(self):
        return sha256(self.raw_bytes).digest()


class KbootAppSector:
    def __init__(self, address):
        if address % 0x1000 != 0:
            raise ValueError('Address must begin at a 4096-byte aligned sector')
        if address in (KbootConstants.STAGE0_ADDRESS, KbootConstants.STAGE1_ADDRESS):
            self.block_size = 0x1000
        elif KbootConstants.APP_ADDRESS_RANGE[0] <= address <= KbootConstants.APP_ADDRESS_RANGE[1]:
            self.block_size = 0x10000
        else:
            raise ValueError('Address must be {}, {}, or between {}'.format(
                hex(KbootConstants.STAGE0_ADDRESS),
                hex(KbootConstants.STAGE1_ADDRESS),
                [hex(x) for x in KbootConstants.APP_ADDRESS_RANGE]
            ))
        self.validate(address)

    def validate(self, address):
        a_block = utils.flash_read(address, self.block_size)
        if a_block[0:1] != b'\x00':
            raise ValueError('AES byte in header at {} must be 0x00'.format(hex(address)))

        expected_size = int.from_bytes(a_block[1:5], 'little')

        hdrapp_hash = sha256()
        app_hash = sha256()
        app_crc = 0
        bytes_read = 0

        begin = 5
        while bytes_read < expected_size:
            if expected_size >= bytes_read + self.block_size:
                end = self.block_size
            else:
                end = expected_size + begin - bytes_read
            
            hdrapp_hash.update(a_block[:end])
            app_hash.update(a_block[begin:end])
            app_crc = crc32(a_block[begin:end], app_crc)
          
            bytes_read += end - begin

            if self.block_size - end < 32:
                begin = 0
                a_block = utils.flash_read(address + bytes_read +5, self.block_size)

        hdrapp_hash = hdrapp_hash.digest()
        if a_block[end:end+32] != hdrapp_hash:
            ValueError('KbootApp at {} is corrupted; calculated sha256 does not match suffix'.format(
                hex(address)
            ))

        if a_block[end+32:] != b'\x00' * (self.block_size - end - 32):
            ValueError('KbootApp at {} should be null-byte padded to the end of the sector'.format(
                hex(address)
            ))

        self.address = address
        self.hdrapp_sha256 = hdrapp_hash
        self.app_sha256 = app_hash.digest()
        self.app_crc32 = app_crc
        self.sector_size = 5 + bytes_read + (self.block_size - end)
        self.app_size = expected_size



if __name__ == '__main__':

    from binascii import hexlify, unhexlify

    configurations = [
        ('main', KbootConfigSector(main=True)),
        ('backup', KbootConfigSector(main=False))
    ]

    applications = [
        ('stage0', KbootAppSector(0x0)), 
        ('stage1', KbootAppSector(0x1000)),
        ('firmware_slot1', KbootAppSector(0x80000)),
    ]
    try: applications.append(('firmware_slot2', KbootAppSector(0x280000)))
    except: pass
    try: applications.append(('firmware_slot3', KbootAppSector(0x800000)))
    except: pass

    for name, config in configurations:
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
                '\n config.entry #{}\n raw_bytes : {}'.format(i, hexlify(entry.serialize())),
                '\n  is_active: {}, ck_crc32: {}, ck_sha256: {}, ck_size: {}'.format(
                     entry.is_active, entry.ck_crc32, entry.ck_sha256, entry.ck_size
                ),
                '\n  app_address: {} {}'.format(entry.app_address, hex(entry.app_address)),
                '\n  app_size: {} {}'.format(entry.app_size, hex(entry.app_size)),
                '\n  app_crc32: {}'.format(entry.app_crc32),
                '\n  app_name: {}'.format(entry.app_name)
            )

        assert config.raw_bytes == config.serialize()

    for name, app in applications:
        print(
            '\nKboot app {} at {}'.format(name, hex(app.address)),
            '\n block_size: {}'.format(hex(app.block_size)),
            '\n sector_size: {} {}'.format(app.sector_size, hex(app.sector_size)),
            '\n app_size: {}'.format(app.app_size),
            '\n app_crc32: {}'.format(app.app_crc32),
            '\n hdrapp_sha256: {}'.format(hexlify(app.hdrapp_sha256)),
            '\n app_sha256: {}'.format(hexlify(app.app_sha256))
        )

