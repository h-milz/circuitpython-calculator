# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT

"""
ComplexDecimal class for Python. Written for jepler_udecimal, but should also work with standard
Python decimal. 

Uses also my jepler_udecimal.utrig extension umath.py which implements a number of math functions omitted 
from there, namely hyperbolic functions for real arguments. 

This class implements a subset of the Python cmath class, but with Decimals instead of float. 

Copyright (C) Harald Milz <hm@seneca.muc.de>

"""

import jepler_udecimal.utrig        # Needed for trig functions in Decimal
import umath                        # my extensions
from jepler_udecimal import Decimal, getcontext, localcontext, InvalidOperation

pi = Decimal.pi

_Zero = Decimal(0)
_One = Decimal(1)
_Two = Decimal(2)
_Ten = Decimal(10)
_point1 = Decimal("0.1")
_point5 = Decimal("0.5")

# TODO: all that is in https://docs.python.org/3/library/cmath.html


# we leave all the NaN checking to the Decimal class. 

# Functions like __eq__ primarily needed for programming are missing. __le__ and consorts are not defined for complex numbers. 

class ComplexDecimal(object):
    """Floating point class for complex decimal arithmetic."""
    
    __slots__ = ("real", "imag")
    def __new__(cls, real="0", imag="0", context=None):
        self = object.__new__(cls)
        if isinstance(real, complex):           # we also accept the standard complex notation a+bj
            self.real = Decimal(real.real)
            self.imag = Decimal(real.imag)
        else:
            self.real = Decimal(real)
            self.imag = Decimal(imag)
        return self
        

    def __repr__(self):
        # strip trailing zeros. 
        return f'C({self.real.normalize()}, {self.imag.normalize()})'


    def _conjugate(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        return ComplexDecimal(self.real, -self.imag)
        
    
    def __add__(self, other, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
            
        if isinstance(other, (int, float, complex)):
            other = ComplexDecimal(other)
        
        return ComplexDecimal(self.real + other.real, self.imag + other.imag)
                

    def __sub__(self, other, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
            
        if isinstance(other, (int, float, complex)):
            other = ComplexDecimal(other)
        
        return ComplexDecimal(self.real - other.real, self.imag - other.imag)


    def __mul__(self, other, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
            
        if isinstance(other, (int, float, complex)):
            other = ComplexDecimal(other)
        
        real_part = self.real * other.real - self.imag * other.imag
        imag_part = self.imag * other.real + self.real * other.imag
        
        return ComplexDecimal(real_part, imag_part)
        

    def __truediv__(self, other, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
            
        if isinstance(other, (int, float, complex)):
            other = ComplexDecimal(other)
        
        # we conjugate in pace ; other.imag must be taken with a negative sign
        denominator = other.real * other.real + other.imag * other.imag
        real_part = (self.real * other.real - self.imag * (- other.imag)) / denominator
        imag_part = (self.imag * other.real + self.real * (- other.imag)) / denominator
        
        return ComplexDecimal(real_part, imag_part)


    def polar(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        r = self.abs()
        if r == 0:
            return context._raise_error(InvalidOperation, "polar(z), |z| == 0")

        return (r, self.phase())


    def rect(self, other, context=None):
        if context is None:
            context = getcontext()
    
        # (self, other) must be the tuple (r, theta) as returned by polar(). 
        # i.e. rect() needs to be called as rect(r, theta). 
        # TODO how do we check this? 
        real_part = self * other.cos()
        imag_part = self * other.sin()
        
        return ComplexDecimal(real_part, imag_part)


    def phase(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        return Decimal.atan2(self.imag, self.real)  


    def __pow__(self, other, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
            
        if isinstance(other, (int, float)):
            other = Decimal(other)
            (r, theta) = self.polar() 
            r = r ** other          # context = Decimal
            theta = theta * other
            return ComplexDecimal.rect(r, theta)
        else:
            return NotImplemented       #   z^w = e^(w⋅log(z))   TODO 

    def sqrt(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
        
        return self ** 0.5
            

    def abs(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        return Decimal.sqrt(self.real * self.real + self.imag * self.imag)
    

    def sin(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        real_part = Decimal.sin(self.real) * Decimal.cosh(self.imag)
        imag_part = Decimal.cos(self.real) * Decimal.sinh(self.imag)

        return ComplexDecimal(real_part, imag_part)
            

    def cos(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        real_part = Decimal.cos(self.real) * Decimal.cosh(self.imag)
        imag_part = - Decimal.sin(self.real) * Decimal.sinh(self.imag)

        return ComplexDecimal(real_part, imag_part)

        
    def tan(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)
            
        return self.sin() / self.cos()


    def asin(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        # https://de.wikipedia.org/wiki/Arkussinus_und_Arkuskosinus#Komplexe_Argumente
        a = self.real
        b = self.imag
        real_part = _point5 * Decimal.acos(Decimal.sqrt((a*a + b*b - _One)**2 + 4*b*b) - (a*a + b*b)).copy_sign(a)
        imag_part = _point5 * Decimal.acosh(Decimal.sqrt((a*a + b*b - _One)**2 + 4*b*b) + (a*a + b*b)).copy_sign(b)
  
        return ComplexDecimal(real_part, imag_part)


    def acos(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        # https://de.wikipedia.org/wiki/Arkussinus_und_Arkuskosinus#Komplexe_Argumente
        return ComplexDecimal(pi/_Two) - self.casin()


    def atan(self, context=None):
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        # https://de.wikipedia.org/wiki/Arkustangens_und_Arkuskotangens#Komplexer_Arkustangens_und_Arkuskotangens
        a = self.real
        b = self.imag
        if a != 0:
            real_part = _point5 * ((a*a + b*b - _One) / ((_Two * a) + (pi/_Two)).atanh().copy_sign(a))
        elif a == 0 and b.abs() <= 1:
            real_part = _Zero
        else:  # a == 0 and |b| > 1
            real_part = (pi/_Two).copy_sign(b)
        imag_part = _point5 * (_Two * b / (a*a + b*b + _One)).atanh()
  
        return ComplexDecimal(real_part, imag_part)


    def sinh(self, context=None):
        # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus#Komplexe_Argumente
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        real_part = Decimal.cos(self.imag) * Decimal.sinh(self.real)
        imag_part = Decimal.sin(self.imag) * Decimal.cosh(self.real)

        return ComplexDecimal(real_part, imag_part)

            
    def cosh(self, context=None):
        # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus#Komplexe_Argumente
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        real_part = Decimal.cos(self.imag) * Decimal.cosh(self.real)
        imag_part = Decimal.sin(self.imag) * Decimal.sinh(self.real)
       
        return ComplexDecimal(real_part, imag_part)
            

    def tanh(self, context=None):
        # https://de.wikipedia.org/wiki/Tangens_hyperbolicus_und_Kotangens_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.567
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        return self.sinh() / self.cosh()
        

    # complex natural log. We return only the principle value. 
    def ln(self, context=None):
        # https://en.wikipedia.org/wiki/Complex_logarithm
        if context is None:
            context = getcontext()

        if isinstance(self, (int, float, complex)):           
            self = ComplexDecimal(self)
        
        r = self.abs()
        if r == 0:
            return context._raise_error(InvalidOperation, "ln(z), |z| == 0")

        arg = Decimal.atan2(self.imag, self.real)

        return ComplexDecimal(r.ln(), arg)
        

    def asinh(self, context=None):
        # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        return(self + (self*self + _cdOne).sqrt()).ln()

            
    def acosh(self, context=None):
        # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        return (self + (self*self - _cdOne).sqrt()).ln()


    def atanh(self, context=None):
        # https://de.wikipedia.org/wiki/Areatangens_hyperbolicus_und_Areakotangens_hyperbolicus
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        return ((_cdOne + self) / (_cdOne - self)).ln() / 2

    
    def acoth(self, context=None):
        # https://de.wikipedia.org/wiki/Areatangens_hyperbolicus_und_Areakotangens_hyperbolicus
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        if context is None:
            context = getcontext()

        if isinstance(self, complex):           
            self = ComplexDecimal(self)

        return ((self + _cdOne) / (self - _cdOne)).ln() / 2
        
        

C = ComplexDecimal
_cdOne = C(1)


