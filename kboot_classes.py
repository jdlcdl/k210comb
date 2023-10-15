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

    def __str__(self):
        return '{}: flags: {}/{}/{}/{}, address: {}, size: {}'.format(
            self.app_name,
            'active' if self.is_active else 'NOT-active',
            'ck_crc32' if self.ck_crc32 else 'NO-ck_crc32',
            'ck_sha256' if self.ck_sha256 else 'NO-ck_sha256',
            'ck_size' if self.ck_size else 'NO-ck_size',
            hex(self.app_address),
            self.app_size
        )

class KbootConfigSector:
    def __init__(self,
        entries=[],
        config_flags=0,
        reserved=0,
        user_data=0
    ):
        if 0 <= len(entries) <= 8 and set([type(x)==KbootConfigEntry for x in entries]) == set([True]):
            self.entries = entries
        else:
            raise ValueError('entries must be of type KbootConfigEntry and of length 0-8')
        
        self.config_flags = config_flags
        self.reserved = reserved
        self.user_data = user_data

    @classmethod
    def from_bytes(cls, raw_bytes):
        if type(raw_bytes) != bytes or len(raw_bytes) != 4096:
            raise ValueError('raw_bytes must be of type bytes and of length 4096')

        entries = []
        for i in range(0, 32*8, 32):
            try: entries.append(KbootConfigEntry.from_bytes(raw_bytes[i:i+32]))
            except: pass

        config_flags = int.from_bytes(raw_bytes[256:260], 'big')
        reserved = int.from_bytes(raw_bytes[260:264], 'big')

        if raw_bytes[264:288] != b'\x00'*24:
            raise ValueError('24 bytes undocumented between reserved and user_data should be null')

        user_data = int.from_bytes(raw_bytes[288:292], 'big')

        if raw_bytes[292:] != b'\x00'*3804:
            raise ValueError('3804 bytes to pad end of sector should be null')

        return cls(
            entries=entries,
            config_flags=config_flags,
            reserved=reserved,
            user_data=user_data
        )

    def serialize(self):
        raw_bytes = b''
        for i in range(8):
            if len(self.entries) > i:
                raw_bytes += self.entries[i].serialize()
            else:
                raw_bytes += b'\x00' * 32

        raw_bytes += self.config_flags.to_bytes(4, 'big')
        raw_bytes += self.reserved.to_bytes(4, 'big')
        raw_bytes += b'\x00' * 24
        raw_bytes += self.user_data.to_bytes(4, 'big')
        raw_bytes += b'\x00' * 3804

        return raw_bytes

    def sha256(self):
        return sha256(self.serialize()).digest()

    def __str__(self):
        return 'config_flags: {}, user_data: {}, entries:\n  {}'.format(
            hexlify(self.config_flags.to_bytes(4, 'big')).decode(),
            hexlify(self.user_data.to_bytes(4, 'big')).decode(),
            '\n  '.join([str(x) for x in self.entries])
        )


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

    def __str__(self):
        return 'address: {}, sector_size: {}, app_size: {}, crc32: {},\n  app_sha256: {}'.format(
            hex(self.address),
            hex(self.sector_size),
            self.app_size,
            self.app_crc32,
            hexlify(self.app_sha256).decode()
        )


if __name__ == '__main__':

    from binascii import hexlify, unhexlify

    config_tuples = [
        ('main', utils.flash_read(KbootConstants.MAIN_CONFIG_ADDRESS, 4096)),
        ('backup', utils.flash_read(KbootConstants.BACKUP_CONFIG_ADDRESS, 4096))
    ]

    app_tuples = [
        ('stage0', 0x0), 
        ('stage1', 0x1000),
        ('default_app', 0x10000),
        ('firmware_slot1', 0x80000),
        ('firmware_slot2', 0x280000),
        ('firmware_slot3', 0x800000),
    ]

    configs = {}
    for name, raw_bytes in config_tuples:
        config = KbootConfigSector.from_bytes(raw_bytes)
        assert raw_bytes == config.serialize()
        configs[name] = config

    apps = {}
    for name, address in app_tuples:
        try: app = KbootAppSector(address)
        except: continue
        apps[name] = app

    for name in [x[0] for x in config_tuples]:
        if name in configs:
            print('\nKbootConfigSector: {}, {}'.format(name, configs[name]))

    for name in [x[0] for x in app_tuples]:
        if name in apps:
            print('\nKbootAppSector: {}, {}'.format(name, apps[name]))
