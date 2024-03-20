# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT



import math as m
import cmath as cm
from collections import namedtuple
from uncertainty import ufloat as u
from ufractions import frac as fr
import sys

def current_function_name():
    frame = sys._getframe().f_back
    return frame.f_code.co_name

# create some immutable variables. 
# we use m.pi and m.e etc. directly. 
# TODO: Umrechnungskonstanten
ConstantsNamespace = namedtuple(
    "ConstantsNamespaces", ["c",
                            "g",
                            "h",
                            "hb",
                            "e",
                            "mu0",
                            "ep0",
                            "a",               
                            "mu",
                            "me",
                            "mp",
                            "mn",
                            "kb",
                            "na",
                            "fc",
                            "rc",
                            "vm",
                            "si",    
                           ]
)

c = ConstantsNamespace( 299792458.0,             # c     c0 (exact)                        m/s
                        6.67430e-11,             # g     Newton's gravitational constant   m³ / (kg * s²)
                        6.62607015e-34,          # h     Planck's constant (exact)         Js 
                        1.0545718176461565e-34,  # hb    h bar = h / 2 pi                  Js   
                        1.602176634e-19,         # e     elementary charge (exact)         As  
                        1.25663706212e-6,        # mu0   vacuum magnetic permeability      Vs / Am
                        8.8541878128e-12,        # ep0   vacuum electric permittivity      As / Vm
                        7.2973525693e-3,         # a     alpha (fine structure constant)
                        1.66053906660e-27,       # mu    atomic mass constant              kg
                        9.1093837015e-31,        # me    electron mass                     kg
                        1.67262192369e-27,       # mp    proton mass                       kg
                        1.6749274980437807e-27,  # mn    neutron mass                      kg
                        1.380649e-23,            # kb    Boltzmann's constant (exact)      J/K
                        6.02214076e23,           # na    Avogadro's constant  (exact)      1 / mol
                        96485.33212,             # fc    Faraday's constant NA * e         C / mol
                        8.31446261815324,        # rc    molar gas constant                J / (mol * K)
                        22.41396954e-3,          # vm    molar volume of ideal gas         m³ / mol
                        5.670374419e-8,          # si    sigma, Stefan-Boltzmann constant  W / (m² * K^4)
)


# all these math wrappers 

# TODO help


def acos(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Arkussinus_und_Arkuskosinus#Komplexe_Argumente
        return m.pi/2 - asin(x) 
    else:               # argument is type real, i.e. int, float
        return m.acos(x)


def acosh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        return cm.log(x + cm.sqrt(x*x - 1))
    else:               # argument is type real, i.e. int, float
        return m.acosh(x)


def asin(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Arkussinus_und_Arkuskosinus#Komplexe_Argumente
        r = x.real
        i = x.imag
        real_part = 0.5 * m.acos(m.sqrt((r*r + i*i - 1)**2 + 4*i*i) - (r*r + i*i)) * m.copysign(1, r)
        imag_part = 0.5 * m.acosh(m.sqrt((r*r + i*i - 1)**2 + 4*i*i) + (r*r + i*i)) * m.copysign(1, i)
        return complex(real_part, imag_part)
    else:               # argument is type real, i.e. int, float
        return m.asin(x)


def asinh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Areasinus_hyperbolicus_und_Areakosinus_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        return cm.log(x + cm.sqrt(x*x + 1))
    else:               # argument is type real, i.e. int, float
        return m.asinh(x)


def atan(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Arkustangens_und_Arkuskotangens#Komplexer_Arkustangens_und_Arkuskotangens
        r = x.real
        i = x.imag
        if r != 0:
            real_part = 0.5 * (m.atan((r*r + i*i - 1) / (2 * r)) + m.pi/2 * m.copysign(1, r))
        elif r == 0 and abs(i) <= 1:
            real_part = 0.0
        else:  # r == 0 and |i| > 1
            real_part = m.pi/2 * m.copysign(1, i)
        imag_part = 0.5 * m.atanh(2 * i / (r*r + i*i + 1)) 
        return complex(real_part, imag_part)
    else:               # argument is type real, i.e. int, float
        return m.atan(x)


def atan2(x, y):		
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
    	return m.atan2(x, y)


def atanh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Areatangens_hyperbolicus_und_Areakotangens_hyperbolicus
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.570
        return 0.5 * cm.log((1+x)/(1-x))
    else:               # argument is type real, i.e. int, float
        return m.atanh(x)


def cos(x):
    if isinstance (x, complex): 
        return cm.cos(x)
    else:               # argument is type real, i.e. int, float
        return m.cos(x)


def cosh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus#Komplexe_Argumente
        r = x.real
        i = x.imag
        real_part = m.cos(i) * m.cosh(r)
        imag_part = m.sin(i) * m.sinh(r)
        return complex(real_part, imag_part)
    else:               # argument is type real, i.e. int, float
        return m.cosh(x)


def degrees(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.degrees(x)

deg = degrees    

def erf(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.erf(x)


def erfc(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.erfc(x)


def exp(x):
    if isinstance (x, complex): 
        (r, theta) = polar(x)
        return complex(m.exp(r) * m.cos(theta), m.exp(r) * m.sin(theta))
    else:
        return m.exp(x)


def expm1(x):
    if isinstance (x, complex): 
        (r, theta) = polar(x)
        return complex(m.expm1(r) * m.cos(theta), m.exp,1(r) * m.sin(theta))
    else:
        return m.expm1(x)


def fabs(x):
    if isinstance (x, complex): 
        return m.sqrt(x.real*x.real + x.imag*x.imag)
    else:
        return m.fabs(x)


def gamma(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.gamma(x)


def lgamma(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.lgamma(x)


def log(x):
    if isinstance (x, complex) or x < 0: 
        return cm.log(x)
    else:               # argument is not negative and type real, i.e. int, float
        return m.log(x)

ln = log 

def log10(x):
    if isinstance (x, complex) or x < 0: 
        return cm.log10(x)
    else:               # argument is not negative and type real, i.e. int, float
        return m.log10(x)

lg = log10

def log2(x):
    if isinstance (x, complex) or x < 0: 
        return cm.log(x) / m.log(2.0)
    else:               # argument is not negative and type real, i.e. int, float
        return m.log2(x)


def radians(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    else:
        return m.radians(x)

rad = radians    

def sin(x):
    '''return the sin of x.'''
    if isinstance (x, complex): 
        return cm.sin(x)
    else:               # argument is type real, i.e. int, float
        return m.sin(x)


def sinh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus#Komplexe_Argumente
        r = x.real
        i = x.imag
        real_part = m.cos(i) * m.sinh(r)
        imag_part = m.sin(i) * m.cosh(r)
        return complex(real_part, imag_part)
    else:               # argument is type real, i.e. int, float
        return m.sinh(x)


def sqrt(x):
    if isinstance (x, complex) or x < 0: 
        return cm.sqrt(x)
    else:               # argument is not negative and type real, i.e. int, float
        return m.sqrt(x)


def tan(x):
    if isinstance (x, complex): 
        return cm.sin(x) / cm.cos(x)
    else:               # argument is type real, i.e. int, float
        return m.tan(x)


def tanh(x):
    if isinstance (x, complex): 
        # https://de.wikipedia.org/wiki/Tangens_hyperbolicus_und_Kotangens_hyperbolicus#Numerische_Berechnung
        # see also: Bronstein, Taschenbuch der Mathematik, 1979, p.567
        return sinh(x) / cosh(x)
    else:               # argument is type real, i.e. int, float
        return m.tanh(x)


# complex only

# TODO does not return anything here? 
def polar(x):		
	return cm.polar(x)


def rect(r, theta):		
	return cm.rect(r, theta)


def phase(x):		
	return cm.phase(x) 

# reals only

def hypot(x, y):
    # this will raise a complex error if needed. 
    return m.sqrt(x*x + y*y)



# TODO !!! but should be replaced by Fractions. 
#def as_integer_ratio(x):		
#    if context is None:
#        context = getcontext()
#	return D.as_integer_ratio(x, context=context)
	
	
'''
# ist wieder in py/modmath.c abgeklemmt...
def gcd(*args):
    return m.gcd(args)

def lcm(*args):
    return m.lcm(args)
'''

def gcd(x, y):		
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    if not isinstance(x, int) or not isinstance (y, int): 
        raise ValueError ("gcd(x, y), x and/or y not integer")
    if x == 0 or y == 0:
        raise ValueError ("gcd(x, y), x and/or y not integer")
    while y != 0:
        x, y = y, x % y
    return abs(x)


def lcm(x, y):	
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    if not isinstance(x, int) or not isinstance (y, int): 
        raise ValueError ("lcm(x, y), x and/or y not integer")
    if x == 0 or y == 0:
        raise ValueError ("lcm(x, y), x and/or y not integer")
    return abs(x * y) / gcd(x, y)

	
def factorial(x):
    if isinstance (x, complex): 
        raise NotImplementedError (f'function does not support type complex')  
    if not isinstance(x, int): 
        raise ValueError (f'factorial(x), x not integer. Use gamma()?')
    fact = 1
    if x >= 2:   # we return 1 for x == 0 or 1
        # recursive programming needs more memory and is not faster anyway... 
        for i in range (2, x+1):
            fact *= i
    return fact        
    
fact = factorial



