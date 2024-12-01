from microcontroller import *
on_next_reset(RunMode.UF2)
reset()

Hi all, 

I flashed my Teensy40 with tinyuf2, after which the TNSY40BOOT comes up and I can drag and drop my favourite Circuitpython UF2. So far so good. But how do I get this thing to boot to UF2 later? It has no reset button or line, and the sole button switches it to JTAG download mode via the M0 Coprocessor. As a workaround, one could in theory do this: 

[code]
from microcontroller import *
on_next_reset(RunMode.UF2)
reset()
[/code]

but the 
