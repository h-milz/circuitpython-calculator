# circuitpython-calculator
Handheld Calculator running on CircuitPython. The hardware is a Keyboard Featherwing V2 (https://www.solder.party/docs/keyboard-featherwing/rev2/) from arturo182 (https://github.com/arturo182), an Adafruit Feather M4 Express (https://www.adafruit.com/product/3857) and a 2000mAh LiPo battery. Circuitpython is a custom build which enables float64 (double) math as well as the cmath module (see circuitpython.diff and the build script). 

All of this is still very raw but workable. 

## code.py
The main file running the keyboard and display, as well as command dispatching. The UI looks and feels much like a real Python prompt but is fully terminalio emulated because you cannot simply run a local, interactive REPL. Runs Python expressions, statements and compound statements. The eval() and exec() calls are not yet hardened. 


## umath.py
umath.py is a wrapper for real and complex values. Depending on the argument type, the appropriate function from math or cmath is executed. Most complex functions are implemented here in python.


## uncertainty.py
Small, simplified version of Python uncertainties for Circuitpython. Tested with CP 9.0.0 and Python 3.10.0. Should be mostly complete. 


## ufractions.py
Small, simplified version of Python Fractions for Circuitpython. Tested with CP 9.0.0 and Python 3.10.0. Incomplete as of yet. 


## Bitmaps
contains blinka images converted from the C source code. 