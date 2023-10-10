Exploring krux -- under the hood -- on a Sipeed Maix Amigo TFT
---

Hardware: [Sipeed Maix Amigo](https://wiki.sipeed.com/soft/maixpy/en/develop_kit_board/maix_amigo.html)

Sofware: open-source project [krux](https://github.com/selfcustody/krux#readme)

Handling the Amigo
---

Krux expects it to be held in portrait mode, with the front-facing camera at the top.

There are 4 buttons that run along the right side for 5 basic functions.

On the top-right side are the navigation buttons:
* The long button has two functions: 'Up' and 'Down', or 'Prev' and 'Next' (aka: C and B respectively).
* The oval button functions as 'Enter' (aka: A).

On the bottom-right side, to start/stop the board:
* The small round button is 'Reset'.  It immediately resets the board, krux will be back shortly.
* The lower oval button is 'Power'.  When 'off': a 1s press blinks the front-facing white LED once -- and boots the board. 
  When the Amigo is 'on' (or soft-shutdown): a 6s press-and-hold will turn it 'off'.
  Is that the same as powered-off???  I don't know.  It feels off because it doesn't appear to do anything until
  you turn it 'on' again and see the white LED flash.

When the Amigo is 'on', you'll briefly see the 'k' splash screen, then krux will be functional.

---

Connecting to the console over usb.
---

It's the small USB-C port at the bottom-center, (not the one at the bottom-left side).


Use `screen` to connect; don't forget that `<ctrl>-a, k` is how to kill screen once inside.

```
screen /dev/ttyUSB1 115200
```

If lucky, we might see this:
```
K210 bootloader by LoBo v.1.4.1

                               * Find applications in MAIN parameters
                                                                         0: '       firmware', @ 0x00080000, size=1744896, app_size=1930944, App ok, ACTIVE
                                                                 * Loading app from flash at 0x00080000 (1930944 B)
                         * Starting at 0x80000000 ...


[MAIXPY] Pll0:freq:728000000
[MAIXPY] Pll1:freq:26000000
[MAIXPY] Pll2:freq:45066666
[MAIXPY] cpu:freq:364000000
[MAIXPY] kpu:freq:1625000
[MAIXPY] Flash:0xef:0x17
[MaixPy] gc heap=0x802045b0-0x802f45b0(983040)
[maixpy] mount sdcard failed
init i2c:2 freq:100000
[MAIXPY]: find ov7740
[MAIXPY]: find ov sensor
```
... or we might see a portion of that, or nothing at all.  We can press 'Reset' to see it again.

This is a python REPL.  

It feels as if we'd typed `python -i some_program.py` which started another window.  We might expect to see
messages output here, if some_program.py uses `print()` statements, but I don't know that krux does that.
This 'apparent' python process is busy running krux on the Amigo right now, which is still functional.
It won't pay much attention to our keystrokes, but it will gather them and use them as input if we could 
interrupt it.

We can interrupt the program w/ `<ctrl>-c` and we'll see the backtrace of the KeyboardInterupt we just provoked.

```
Traceback (most recent call last):
  File "boot.py", line 80, in <module>
  File "boot.py", line 52, in login
  File "krux/pages/__init__.py", line 345, in run
  File "krux/pages/__init__.py", line 417, in run_loop
  File "krux/input.py", line 131, in wait_for_button
  File "krux/input.py", line 121, in wait_for_press
  File "krux/input.py", line 76, in touch_value
KeyboardInterrupt: 
MicroPython v1.11 on 2023-09-22; Sipeed_M1 with kendryte-k210
Type "help()" for more information.
>>>
```

There's the python REPL we know and love. It looks like some_program.py was really "boot.py", as in `~/krux/src/boot.py` from a cloned krux repository.

Welcome home!

Wait for it...

Note: We want to be careful using `<ctrl>-d` (the one that tells python repl "goodbye" and logs us out) because this
'apparent' python process will immediately become unresponsive at the console.  In this event, the best we can do is
press 'Reset'; which reboots the board immediately w/o losing the console connection. We can also press-and-hold 'Power' for 6s,
then turn it 'on' again, but this will interrupt our screen connection to the console.  Otherwise, wait for a miracle?

---

Stopping the WDT (watchdog timer)
---

Krux uses one of two available WDT instances to reset the board if it is not constantly fed.
The board will reboot in ~30s if we ever interrupt the krux process, or if the app crashes, but we can easily stop this timer.

```
from machine import WDT
WDT().stop()
```
We need to complete that within 30s else the board will reset.  We have two choices, we can type fast enough,
or we can use cut/paste (fast enough).

To cut/paste, we can put the REPL into 'paste-mode' w/ `<ctrl>-e` at an empty `>>>` prompt:
```
>>> <ctrl>-e
paste mode; Ctrl-C to cancel, Ctrl-D to finish
===
```

Now we can paste from our clipboard, hitting `<ctrl>-d` (but just once!) when done.
If we don't use this special mode, the REPL will auto-indent our paste, leading to IndentationError exceptions.

Krux documentation explains how to disable the WDT timer via a "config.json" file that gets stored to SPI Flash, so krux will know to disable the WDT next time it boots.  This way you can connect to the console, interrupt krux, and get to exploring.  I prefer to `WDT().stop()` each time so that nothing is written to flash, and so that the device would auto-reboot in the event of an application crash and no console access.

If the 16MB SPI Flash memory interests you, see:
[sipeed maix amigo tft: flash exploration](https://gist.github.com/jdlcdl/a01dbf21771516581b4ccfda49622293).

---

Getting familiar with the REPL and krux.
---

[Sipeed MaixPy (micropython) api reference](https://wiki.sipeed.com/soft/maixpy/en/index.html)

Let's not forget that we're on a platform of limited resources, much different than a desktop w/ a full OS.
Many libraries are not available in this MaixPy port of micropython, and for the tools which are available,
often only a subset of what we'd normally expect has been implemented and is functional.  For instance, `help(an_object)`
will raise a NameError instead of informing us of what is available and how we might use it.  Thankfully, `dir(an_object)`
and `type(an_object)` are available for learning which names are bound and what they might be.  We'll figure-out
over time that often what we'd expect to be an attribute is implemented as a function that must be called.

Using `dir()`, we can inspect what the environment looked like before we interrupted krux (and stopped the WDT).
```
>>> dir()
['__name__', 'gc', 'Context', 'ctx', 'check_for_updates', 'splash', 'power_manager', 'WDT',
'sys', 'home', 'login']
>>> 
```
It might look different than above, depending on how soon we interrupt krux after boot.  This is what it looks like if we
let krux get to the screen that appears after the 'k' splash.

As for WDT, it's actually there because we just imported it.  We're on limited resources, so we might take the habit
of deleting names that we're no longer using; `del WDT` is sufficient to free that name for garbage-collection later.

Familiar names might be 'gc' and 'sys', which are maixpy's implementations of these well known modules.  There
are more which are available [here](https://wiki.sipeed.com/soft/maixpy/en/api_reference/standard/index.html) if we import them, but many are not, because krux doesn't need them; they're not in the firmware by design.

The REPL does auto-completion when we hit `<tab>`, often this is good enough when we know what we want but we're not sure
how to access it.  Let's try with 'ctx' (as we might guess, it's a Context instance for the krux app)
```
>>> ctx.<tab>
__class__       __init__        __module__      __qualname__
clear           __dict__        display         input
log             power_manager   wallet          printer
camera          light
>>> ctx.light.<tab>
__class__       __init__        __module__      __qualname__
__dict__        toggle          circuit         turn_off
is_on           turn_on
>>> ctx.light.is_on
<bound_method 80235f60 <Light object at 802068e0>.<function is_on at 0x80205f00>>
>>>
```
It looks like `ctx.light.is_on` is not an attribute, it's a method.

Fortunately, the REPL has history that we can scroll thru with the `up` and `down` keys on our keyboard.
```
>>> <up>
>>> ctx.light.is_on()
False
>>> ctx.light.toggle()
```
Wow, that's bright!!!
```
>>> <up>
>>> ctx.light.toggle()
```
Better!

All of the bound names in our current environment are there because when we flashed the firmware, it was configured to run
`boot.py` whenever the device powers on.  It feels as if we'd run `python -i boot.py` and now we're at the `__name__ == '__main__'` level of `boot.py`; everything imported and created is available because it did so.  We can restart krux without resetting the board, reinitializing everything that `boot.py` previously setup.
```
>>> import boot
init i2c:2 freq:100000
[MAIXPY]: find ov7740
[MAIXPY]: find ov sensor
```
And once again, krux is now running on the Amigo, and we'd have to interrupt krux w/ `<ctrl>-c` to regain control of the REPL from the console.  However, since we've just imported 'boot', this won't work again to restart krux unless we `sys.modules.pop('boot')` first.

The code for krux's `boot.py` is [here](https://github.com/selfcustody/krux/blob/main/src/boot.py)

According to that code, it looks like we can also restart krux w/o re-importing boot, since we're already setup. We can do so
by calling login() with our 'ctx'.
```
>>> login(ctx)
```
and now krux is running again.  We can interrupt it and restart it again, or we can use krux on the Amigo.
... right up until the point that we successfully load/create a wallet... and then... But what happened?

```
init i2c:2 freq:100000
[MAIXPY]: find ov7740
[MAIXPY]: find ov sensor
>>>
```
Ahhh, the Amigo is unresponsive and we're back in control inside the REPL.  That's because login() is done and returned, so
let's continue doing what `boot.py` would have done if not interrupted.  For now, let's assume that login() setup 
our `ctx` with our wallet info, then unbound some names that aren't needed any longer.  We'll have the garbage
collector cleanup, then we'll call home() passing it the same ctx that we're assuming is all setup for home().
```
>>> gc.collect()
>>> home(ctx)
```
And the Amigo has once again taken control, running the home() function.  We can interrupt it as before, and restart it again.

We can also access another name that `boot.py` made available for us, the 'power_manager', for board-level control.
```
>>> power_manager.<tab>
__class__       __init__        __module__      __qualname__
__dict__        shutdown        pmu             has_battery
battery_charge_remaining        charging        reboot
>>> power_manager.reboot()
```

Yep, that does what we'd think.  Let's get ready to stop the WDT again... or maybe take a break?
