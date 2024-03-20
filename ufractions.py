# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT

# simplified and naive fractions class
#
# lazy shortcut: num = numerator, den = denominator

import math as m


def _gcd(x, y):
    while y != 0:
        x, y = y, x % y
    return abs(x)
    

class frac(object):
    '''simple fractions class'''
    
    # __slots__ = ("_num", "_den")
    
    def __new__(cls, numerator, denominator):
        self = object.__new__(cls)
        if not isinstance(numerator, int) or not isinstance (denominator, int):
            raise TypeError ("numerator and denominator must be int")
        if denominator == 0:
            raise ZeroDivisionError ("denominator == 0")
        # TODO parse other formats, like num / den 
        # use regexp. 
        # reduce to lowest denominator
        gcd = _gcd(numerator, denominator)
        # mul = 1 if den > 0 else -1
        mul = m.copysign(1, denominator)
        self._num = numerator // gcd  * mul    # and make sure the denominator is positive. 
        self._den = denominator // gcd  * mul
        return self
        

    @property
    def numerator(self):
        '''returns the numerator of a fraction.'''
        if isinstance(self, frac):
            return self._num
        else:
            return self
    
    num = numerator  

    @property
    def denominator(self):
        '''returns the denominator of a fraction.'''
        if isinstance(self, frac):
            return self._den
        else:
            return 1
        
    den = denominator
    
    def __repr__(self):
        '''repr(self)'''
        # we do not return the num/den format here. 
        return f'fr({self._num:d}, {self._den:d})'
        

    def __str__(self):
        '''str(self)'''
        if self._den == 1:
            return str(self._num)
        else:
            return '%s/%s' % (self._num, self._den)


    def __add__(self, other):
        if isinstance(other, int):
            other = frac(other, 1)          # so that we can also add, sub etc. ints. 
        num = self._num * other.den + self._den * other._num
        den = self._den * other.den
        return frac(num, den)

    
    def __sub__(self, other):
        if isinstance(other, int):
            other = frac(other, 1)
        num = self._num * other.den - self._den * other._num
        den = self._den * other.den
        return frac(num, den)

    
    def __mul__(self, other):
        if isinstance(other, int):
            other = frac(other, 1)
        num = self._num * other._num
        den = self._den * other.den
        return frac(num, den)

    
    def __truediv__(self, other):
        if isinstance(other, int):
            other = frac(other, 1)
        num = self._num * other.den
        den = self._den * other._num
        return frac(num, den)

    
    def __pow__(self, other):
        return self
    
    @classmethod
    def from_float(x, decimals=None):
        # this is interesting given that we only have floats, not Decimal. 
        if isinstance(x, (int, complex)):
            raise TypeError ("seriously?")         # seriously? 
        if isinstance (x, str):
            if x.find('.') == -1: # no decimal point found -> we actually have an integer!
                raise TypeError ("seriously?")         # seriously? 
            else: 
                (ints, decimals) = x.split('.') 
                num = int(ints + decimals)          # generate an integer of len(ints + decimals)
                den = 10**(len(ints + decimals))
        elif isinstance (x, float) and decimals == None:
            raise ValueError ("pass arg as string or add number of decimals as second arg")
        else:           # here we know it's a float and the number of decimals
            mul = 10**decimals
            num = int(m.floor(x * mul + 0.5))
            den = 10**(m.ceil(m.log10(num)))
        return frac(num, den)
        
        
        
        
    def limit_denominator(self, max_denominator=1000000):
        return self

    limit_den = limit_denominator

    def _round_to_exponent(self):
        return self
        
    
    def _round_to_figures(self):
        return self
        

        
        
        
        
        
        
        
        
        
        
