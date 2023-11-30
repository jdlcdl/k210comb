'''
classes to model SPI Flash File System as laid-out by krux in k210 flash

assumes that utils.flash_read() behaves as if imported from Maix:
ie: `from Maix import utils`
'''

from binascii import hexlify

START_ADDRESS = 0xd00000    # spiffs starts here in flash
SIZE = 0x300000		    # spiffs extends 3MB to the end of 16MB
PHYS_BLOCK_SIZE = 0x1000    # physical block write/erase size
LOG_BLOCK_SIZE = 0x20000    # spiffs logical block size 128k
LOG_PAGE_SIZE = 0x1000      # spiffs logical page size 4k
OBJ_NAME_LEN = 128          # spiffs filename length


class SPIFFSPage:
    def __init__(self, address, obj_size_tuple=None):
        assert START_ADDRESS <= address <= START_ADDRESS + SIZE - LOG_PAGE_SIZE
        self.address = int(address)
        self.status = None
        self.empty = None
        self.header = None
        self.object = None
        self.data_size = None
        self.name = None
        self.contents = None
        self.parse(obj_size_tuple)

    def parse(self, obj_size_tuple=None):

        if self.address == START_ADDRESS:
            return # TODO learn to process the first page

        page = utils.flash_read(self.address, LOG_PAGE_SIZE)

        if page == b'\xff' * LOG_PAGE_SIZE:
            self.empty = True
        elif page[0:LOG_PAGE_SIZE-4] == b'\xff' * (LOG_PAGE_SIZE-4) and page[-3:] == b'\x15\x00\x00':
            self.empty = True
        else:
            self.empty = False

            prefix = page[:12]
            assert page[0] != 0xff, prefix.decode() + " " + hex(self.address)

            # byte 0
            self.object = page[0]

            # byte 1
            if page[1] == 0x80:
                self.header = True
            elif page[1] == 0x00:
                self.header = False
            else:
                assert page[1] == 0x01, prefix.decode() + " " + hex(self.address)

            # bytes 2,3
            if self.header != None:
                assert page[2:4] == b'\x00\x00', hexlify(page[2:4]).decode() + " " + hexlify(prefix).decode() + " " + hex(self.address)

            # byte 4
            if page[4] == 0x7e:
                self.status = 'deleted'
            elif page[4] in (0xf8, 0xfc):
                self.status = 'used'
            elif page[4] in (0x7c, 0xfe):
                self.status = hex(page[4])
            else:
                assert page[4] == 0x00, hexlify(prefix).decode() + " " + hex(self.address)

            if obj_size_tuple:
                if self.header == False and self.object == obj_size_tuple[0]:
                    data_size = obj_size_tuple[1]
                else:
                    data_size = LOG_PAGE_SIZE-5
            else:
                data_size = None

            if self.header:
                # header byte 8
                self.data_size = int.from_bytes(page[8:10], 'little')

                # header bytes 13-
                self.contents = page[13:13+OBJ_NAME_LEN]
            else:
                if data_size:
                    self.contents = page[5:5+data_size]


class SPIFFSBlock:
    def __init__(self, address):
        assert START_ADDRESS <= address <= START_ADDRESS + SIZE - LOG_BLOCK_SIZE
        self.address = int(address)
        self.parse()

    def parse(self):
        self.pages = []
        obj_size_tuple = None
        for address in range(self.address, self.address + LOG_BLOCK_SIZE, LOG_PAGE_SIZE):
            page = SPIFFSPage(address, obj_size_tuple)
            if page.header and page.object and page.data_size:
                obj_size_tuple = (page.object, page.data_size)
            else:
                obj_size_tuple = None
            self.pages.append(page)


class SPIFFSObject:
    def __init__(self, _object):
        self.object = _object
        self.used_head = []
        self.used_data = []
        self.old_head = []
        self.old_data = []

    def add_page(self, page):
        assert self.object == page.object
        if page.status == "used":
            if page.header:
                self.used_head.append(page)
            else:
                self.used_data.append(page)
        else:
            if page.header:
                self.old_head.append(page)
            else:
                self.old_data.append(page)


class SPIFlashFileSystem:
    def __init__(self):
        if START_ADDRESS + SIZE > 2**24:
            raise ValueError('SPIFFS will overflow end of Flash')

        if SIZE % LOG_BLOCK_SIZE != 0:
            raise ValueError('SPIFFS SIZE must align with Logical Block Size.')

        if LOG_BLOCK_SIZE % PHYS_BLOCK_SIZE != 0:
            raise ValueError('SPIFFS Logical Block Size must align with Physical Block Size.')

        if LOG_BLOCK_SIZE % LOG_PAGE_SIZE != 0:
            raise ValueError('SPIFFS Logical Block Size must align with Logical Page Size.')

        self.objects = None
        self.num_empty = None
        self.num_pages = None

        self.parse()

    def parse(self):
        self.objects = {}
        self.num_empty = 0
        self.num_pages = 0

        last_object_size = None
        for address in range(START_ADDRESS, START_ADDRESS + SIZE, LOG_PAGE_SIZE):
            # parse the next page
            page = SPIFFSPage(address, last_object_size)
            if page.object and page.data_size:
                last_object_size = (page.object, page.data_size)
            else:
                last_object_size = None

            # tally empty pages
            if page.empty:
                self.num_empty += 1
            self.num_pages += 1
            
            # object pages
            if page.object:
                if page.object not in self.objects:
                    self.objects[page.object] = SPIFFSObject(page.object)
                _object = self.objects[page.object]
                if page.status == "used" and page.header and page.contents:
                    _object.filename = page.contents.replace(b'\x00', b'').decode()
                if page.status == "used" and not page.header and page.contents:
                    _object.contents = page.contents.decode()
                _object.add_page(page)

    def __str__(self):
        answer = "SPI Flash File System: {}MB at {}".format(SIZE // 1024 // 1024, hex(START_ADDRESS))
        answer += "\n  {}-byte pages: {}, non-empty: {}".format(LOG_PAGE_SIZE, self.num_pages, self.num_pages - self.num_empty)
        for k in sorted(self.objects):
            v = self.objects[k]
            answer += "\n  {}: {:20s} header+data pages: {}+{}, deleted: {}+{}\n    `{}`".format(
                k, 
                v.filename, 
                len(v.used_head),
                len(v.used_data),
                len(v.old_head),
                len(v.old_data),
                v.contents)
        return answer


if __name__ == '__main__':

    spiffs = SPIFlashFileSystem()
    print(spiffs)
