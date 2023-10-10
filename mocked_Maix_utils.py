'''
   Because the tools here assume that utils has been imported from Maix, (to enable utils.flash_read()),
   ie: `from Maix import utils`, this can be used outside of a maixpy device, for instance
   to inspect a 16MB flash dump file that has been written to "/tmp/k210.flash_dump" on a computer.
'''

class MockedMaixUtils:
     def flash_read(self, address, length):
         with open('/tmp/k210.flash_dump', 'rb') as f:
              f.seek(address)
              return f.read(length)

try: from Maix import utils
except: utils = MockedMaixUtils()

