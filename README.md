# circuitpython-calculator
Handheld Calculator running on CircuitPython. The hardware is a Keyboard Featherwing V2 (https://www.solder.party/docs/keyboard-featherwing/rev2/) from arturo182 (https://github.com/arturo182), an Adafruit Feather M4 Express (https://www.adafruit.com/product/3857) and a 2000mAh LiPo battery. Circuitpython is a custom build which enables float64 (double) math as well as the cmath module. The diff is against CP 9.0.0 - the build script automates the build process, and sits on top of https://learn.adafruit.com/building-circuitpython/build-circuitpython. 

All of this is still very raw but workable.   

Update 2024-03-24: 
  
* The main documentation is on https://adafruit-playground.com/u/hmilz/pages/building-a-scientific-handheld-calculator-with-double-precision-math-complex-math-uncertainties-and-fractions

* The image now contains numeric integration as `ulab.scipy.integrate`. 

Add-ons: 

## Bitmaps
contains blinka images converted from the C source code. 


## Decimal
contains some math on top of jepler-udecimal (https://github.com/jepler/Jepler_CircuitPython_udecimal). umath.py complements hyperbolic and some other functions, and cdmath.py, well, complex decimal math. Abandoned in favor of modifying Circuitpython mainly due to memory consumption but workable. Maybe useful for someone. 



