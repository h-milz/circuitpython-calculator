# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT


"""
Math stuff including hyperbolic functions for real arguments using jepler_udecimal

Please see jepler_udecimal/utrig.py for more information. 

"""

import jepler_udecimal.utrig           # Needed for trig functions in Decimal
from jepler_udecimal import Decimal, localcontext, getcontext, InvalidOperation

__all__ = ["sinh", "cosh", "tanh", "asinh", "acosh", "atanh", "atan2", "pi", "e", "as_integer_ratio"]

_Zero = Decimal(0)
_One = Decimal(1)
_Two = Decimal(2)
_Ten = Decimal(10)
_point1 = Decimal("0.1")
e = _One.exp()
pi = Decimal(4) * _One.atan()
D = Decimal

# TODO: all that is in https://docs.python.org/3/library/math.html, eg. 
#  erf, erc, gamma, lgamma, comb, perm, cbrt, exp2, expm1?, log1p?, log2, hypot, degrees, radians, 

# factorial one level above. all integer stuff like gcd and lcm. Wrapper, der Decimal zurück gibt. 

# some functions primarily needed for programming, like isfinite(), are missing. 


def sinh(x, context=None):
    """Compute the sinus hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)

    ans = x._check_nans(context=context)
    if ans:
        return ans

    y = -x
    return (x.exp() - y.exp()) / _Two


def cosh(x, context=None):
    """Compute the cosinus hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)

    ans = x._check_nans(context=context)
    if ans:
        return ans

    y = -x
    return (x.exp() + y.exp()) / _Two


def tanh(x, context=None):
    """Compute the tangens hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Tangens_hyperbolicus_und_Kotangens_hyperbolicus      
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)

    ans = x._check_nans(context=context)
    if ans:
        return ans

    with localcontext(context) as ctx:
        n = getcontext().prec
        
        r = Decimal(n) * _Ten.ln() / _Two
        if x > r:
            return _One
        elif x < - r:
            return - _One
        elif x > -_point1 and x < _point1:
            return x.sinh() / (x.exp() - x.sinh())
        else:
            return x.sinh() / x.cosh()


def asinh(x, context=None):
    """Compute the area sinus hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus      
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)

    ans = x._check_nans(context=context)
    if ans:
        return ans

    n = context.prec                #   TODO 
            
    if x == 0:
        return Decimal(0)
    if x < 0:
        return -asinh(-x)
    if x > 10**(n/2):
        return _Two.ln() + x.ln()
    elif x < Decimal(0.125):                        # let's do some Taylor
        # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus#Reihenentwicklungen
        result = x
        a = Decimal(1)
        # TODO don't have a fixed number of summands but stop when the summand is smaller than 10**(-prec)
        for i in range (3, n + 3, 2):  
            j = Decimal(i)  
            # result = x * ( 1 - 1/2 * x^2/3 + 1/2 * 3/4 * x^4/5 ... 
            x *= x*x                                # x^3, x^5, x^7, ... 
            a *= -(j - _Two)/((j - _One)*j)         # -1/2 * 1/3, + 1/2 * 3/4 *1/5, -1/2 * 3/4 * 5/6 * 1/7, ... 
            result += a * x 
        return result
    else:
        return (x + (x**x + _One).sqrt()).ln()
            

def acosh(x, context=None):
    """Compute the area cosinus hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus      
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)

    ans = x._check_nans(context=context)
    if ans:
        return ans

    if x.compare_total_mag(Decimal(1)) < 0:
        return context._raise_error(InvalidOperation, "acosh(x), x < 1")

    n = context.prec                #   TODO 
    
    if x > 10**(n/2):
        return _Two.ln() + x.ln() 
    else:
        return (x + (x**x - 1).sqrt()).ln()


def atanh(x, context=None):
    """Compute the area tangens hyperbolicus of the specified value"""
    # https://de.wikipedia.org/wiki/Areatangens_hyperbolicus_und_Areakotangens_hyperbolicus
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)
    
    ans = x._check_nans(context=context)
    if ans:
        return ans

    # atanh is not defined for |x| > 1
    if x.compare_total_mag(Decimal(1)) >= 0:
        return context._raise_error(InvalidOperation, "atanh(x), |x| > 1")
        
    return ((1 + x)/(1 - x)).ln() / _Two


def atan2(y, x, context=None):
    # Note: this is atan2(y, x) and thus follows the Fortran convention. 
    # https://en.wikipedia.org/wiki/Atan2, see Notes
    if context is None:
        context = getcontext()

    if not isinstance(x, Decimal):
        x = Decimal(x)
        
    if not isinstance(y, Decimal):
        y = Decimal(y)
        
    ans = x._check_nans(context=context)
    if ans:
        return ans
    
    ans = y._check_nans(context=context)
    if ans:
        return ans

    if x > 0:
        return (y/x).atan()
    elif x < 0 and y >= 0:                  # this includes x<0 y==0; the principle value for atan2(-1,0) is +pi
        return (y/x).atan() + pi            # and we disregard the branch (the negative x axis)
    elif x < 0 and y < 0:
        return (y/x).atan() - pi
    elif x == 0 and y > 0:
        return pi/_Two
    elif x == 0 and y < 0:
        return - pi/_Two
    else:    #  x == 0 and y == 0
        return context._raise_error(InvalidOperation, "atan2(y, x), x == 0 and y == 0")


# cloned from Python decimal (cpython/Lib/_pydecimal.py)
def as_integer_ratio(self, context=None):
    """Express a finite Decimal instance in the form n / d.

    Returns a pair (n, d) of integers.  When called on an infinity
    or NaN, raises OverflowError or ValueError respectively.

    >>> Decimal('3.14').as_integer_ratio()
    (157, 50)
    >>> Decimal('-123e5').as_integer_ratio()
    (-12300000, 1)
    >>> Decimal('0.00').as_integer_ratio()
    (0, 1)

    """
    if context is None:
        context = getcontext()

    if not isinstance(self, Decimal):
        self = Decimal(self)

    if self._is_special:
        if self.is_nan():
            raise ValueError("cannot convert NaN to integer ratio")
        else:
            raise OverflowError("cannot convert Infinity to integer ratio")

    if not self:
        return 0, 1

    # Find n, d in lowest terms such that abs(self) == n / d;
    # we'll deal with the sign later.
    n = int(self._int)
    if self._exp >= 0:
        # self is an integer.
        n, d = n * 10**self._exp, 1
    else:
        # Find d2, d5 such that abs(self) = n / (2**d2 * 5**d5).
        d5 = -self._exp
        while d5 > 0 and n % 5 == 0:
            n //= 5
            d5 -= 1

        # (n & -n).bit_length() - 1 counts trailing zeros in binary
        # representation of n (provided n is nonzero).
        d2 = -self._exp
        shift2 = min((n & -n).bit_length() - 1, d2)
        if shift2:
            n >>= shift2
            d2 -= shift2

        d = 5**d5 << d2

    if self._sign:
        n = -n
    return n, d


# for non-integer values, TODO Gamma. 



for name in __all__:
    setattr(Decimal, name, globals()[name])
    
    
