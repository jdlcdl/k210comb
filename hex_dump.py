class HexDumpSPIFlash:
    '''
    hex dump for maixpy 16MB SPI Flash

    assumes that utils.flash_read() behaves as if imported from Maix
    '''

    size = 2**24
    def __init__(self, begin=0x0, width=16, lines=16, squeeze=True):
        self.cursor = begin
        self.configure(width=width, lines=lines, squeeze=squeeze)

    def next(self):
        pass

    def prev(self):
        page_size = self.width * self.lines
        self.cursor = (self.size + self.cursor - (page_size * 2)) % self.size

    def seek(self, address):
        self.cursor = address % self.size

    def configure(self, width=None, lines=None, squeeze=True):
        if type(width) == int and width > 0: 
            self.width = width

        if type(lines) == int and lines > 0: 
            self.lines = lines

        if type(squeeze) == bool:
            self.squeeze = squeeze

        byte_format = '  '.join([' '.join(['{:02x}']*4)]*(self.width//4))
        if self.width % 4:
             byte_format = '  '.join([byte_format, ' '.join(['{:02x}']*(self.width%4))])
        self.fmt = '{}  {}  |{}|'.format('{:06x}', byte_format, '{:.1s}'*self.width)

    def read(self, update_cursor=False):
        def format_record(address, record):
            if len(record) == self.width:
                return self.fmt.format(
                    *[address]
                    +[x for x in record]
                    +[len(repr(str(chr(x))))==3 and str(chr(x)) or '.' for x in record]
                )
            else:
                return '{:06x}  {} [EOR]'.format(
                    address, 
                    ' '.join(['{:02x}'.format(x) for x in record])
                    )
        first = self.cursor
        answer, buf, i_buf, line_no, repeats, last_record = [], (None, b''), 0, 0, 0, (None, b'')
        while line_no < self.lines:
            if i_buf + 1 >= len(buf[1]):
                buf = (first, utils.flash_read(first, self.width*self.lines))
                i_buf = 0
 
            record = (first, buf[1][i_buf:i_buf+self.width])
            if repeats:
                if record[1] != last_record[1]:
                    answer.extend([
                        '... {:d} squeezed'.format(repeats-1) if repeats>1 else '', 
                        format_record(*last_record), 
                        format_record(*record)
                    ]) 
                    repeats = 0
                    line_no += 3
                else:
                    repeats += 1
            else:
                if self.squeeze and record[1] == last_record[1]:
                    repeats += 1
                else:
                    answer.append(format_record(*record))
                    line_no += 1
            i_buf += len(record[1])
            first = (first + len(record[1])) % self.size
            last_record = record
        if repeats:
            answer.extend([
                '... {:d} squeezed'.format(repeats-1) if repeats>1 else '', 
                format_record(*record)
            ]) 
        if update_cursor:
            self.cursor = first
        return '\n'.join(answer)

    def run(self):
        def set_lines():
            self.configure(lines=int(input('Enter number of lines: ')))

        def set_width():
            self.configure(width=int(input('Enter number of bytes per line: ')))

        def toggle_squeeze():
            self.configure(squeeze=not self.squeeze)

        def seek():
            address = input('Enter an address: ')
            if address[:2] == '0b':
                 address = int(address[2:], 2)
            elif address[:2] == '0x':
                 address = int(address[2:], 16)
            else:
                 address = int(address)
            self.seek(address)

        repl = {
        'j': self.next,
        'k': self.prev,
        'l': set_lines,
        'w': set_width,
        's': toggle_squeeze,
        '/': seek,
        }
        print(self.read(update_cursor=True))
        while True:
            _in = input('\b')
            if _in and _in[0] in repl:
                repl[_in]()
                print(self.read(update_cursor=True))
            elif _in == 'q':
                return
            else: print('Try one of %s or "q" to quit.' % [x for x in repl.keys()])

