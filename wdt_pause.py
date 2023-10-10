# stop the two WDT watchdog timers

from machine import WDT
WDT(0).stop()
WDT(1).stop()


# clean-up
del WDT

