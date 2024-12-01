# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT

# simplified and naive uncertainties class
#
# References: 
#   (1) https://en.wikipedia.org//wiki/Propagation_of_uncertainty 
#   (2) https://en.wikipedia.org/wiki/Covariance
#   (3) Vorlesung "Stochastische Signale", Prof. Dr. Utschick, TU München, WS 23/24
#   (4) Python uncertainties module
#   (5) Bronstein / Semendjajew, Handbuch der Mathematik, Verlag Harri Deutsch 1981
#   (6) https://de.wikipedia.org/wiki/Digamma-Funktion, https://de.wikipedia.org/wiki/Harmonische_Reihe

import math as m

erf_coef = 2.0 / m.sqrt(m.pi) # for erf / erfc

class ufloat(object):
    '''uncertainties class for float'''
    
    __slots__ = ("nomval", "stddev")
    
    def __new__(cls, nomval, stddev):
        self = object.__new__(cls)
        if not isinstance(nomval, (int, float)) or not isinstance (stddev, (int, float)):
            raise TypeError ("nomval and stderr must be int or float")
        else:
            # auto-convert int to float
            self.nomval = float(nomval)
            self.stddev = abs(float(stddev)) # by definition, the stddev is always non-negative. 
            # TODO parse other formats, like nomval+-stddev or nomval(stddev) 
            # use regexp. 
        return self
        

    def nominal_value(self):
        '''returns the nominal value of a ufloat.'''
        if isinstance(self, ufloat):
            return self.nomval
        else:
            return self
        

    def std_dev(self):
        '''returns the standard deviation of a ufloat.'''
        if isinstance(self, ufloat):
            return self.stddev
        else:
            return self
        
    
    def _significant_digits(self):
        # very naive way of determining the place of the first significant digit
        # and the number of significant digits in the stddev. 
        # Python uncertainties uses PDG_precision(std_dev) (core.py:891 ff) 
        if self.stddev == 0:
            return 2
        else:
            return 1 + m.ceil(abs(m.log10(self.stddev)))        #   number of decimals
    
    
    def __repr__(self):
        # TODO nomval and stddev auf denselben Exponenten bringen. 
        n = self._significant_digits()
        # we do not return the nomval+/-stddev format here. 
        return f'u({self.nomval:.{n}f}, {self.stddev:.{n}f})'
        
        
    def _covariance(self, other):
        # For now we return cov = 0 because in engineering practice, different 
        # measurement values can almost always be considered stochastically independent.
        # 
        return 0.
        #
        # (3), chapter 7
        # The correlation factor r(xy) for two random values will almost always be 1 or -1 
        # because you can always draw a straight line through two points. 
        # relself = self.stddev / self.nomval
        # relother = other.stddev / other.nomval
        # if relself == relother:
        #     rxy = 1.
        # elif relself == - relother:
        #     rxy = -1.
        # else:
        #     rxy = 0. 
        # cov = rxy * self.stddev * other.stddev
        # return cov
        
    # Gaussian error propagation, mostly. 
    
    def __add__(self, other):
        cov = self._covariance(other)
        return ufloat(self.nomval + other.nomval, m.sqrt(self.stddev**2 + other.stddev**2 + 2*cov))
        
    
    def __sub__(self, other):    
        cov = self._covariance(other)
        return ufloat(self.nomval - other.nomval, m.sqrt(self.stddev**2 + other.stddev**2 - 2*cov))


    def __mul__(self, other):
        cov = self._covariance(other)
        nomval = self.nomval * other.nomval
        stddev = abs(nomval) * m.sqrt((self.stddev / self.nomval)**2 + 
                                      (other.stddev / other.nomval)**2 + 
                                      2 * cov / nomval)
        return ufloat(nomval, stddev)
        
        
    def __truediv__(self, other):
        cov = self._covariance(other)
        nomval = self.nomval / other.nomval
        stddev = abs(nomval) * m.sqrt((self.stddev / self.nomval)**2 + 
                                      (other.stddev / other.nomval)**2 - 
                                      2 * cov / (self.nomval * other.nomval))
        return ufloat(nomval, stddev)
        
    
    # The nominal value of the function value is the function value at the location of the nominal 
    # value of the argument. 
    # The standard deviation of the function value can be approximated by the standard deviation 
    # of the argument times the slope of the function graph at the location of the argument 
    # (first-order Taylor approximation). 
    # This is simple for all functions that are continuous and differentiable at the argument, 
    # but may require more effort otherwise. 
    
    # (4) fixed_derivatives, umath_core.py:180 ff.
        
    def acos(self):
        if (abs(self)) >= 1:
            raise ValueError ("acos(x): |x| >= 1")
        nomval = m.acos(self.nomval)
        stddev = - self.stddev / m.sqrt(1 - self.nomval**2) # acos'(x) = -1 / sqrt(1 - x²), |x| < 1
        return ufloat(nomval, stddev)
        
        
    def acosh(self):
        if (self) <= 1:
            raise ValueError ("acosh(x): x <= 1")
        nomval = m.acosh(self.nomval)
        stddev = self.stddev / m.sqrt(self.nomval**2 - 1)   # acosh'(x) = 1 / sqrt(x² - 1), x > 1
        return ufloat(nomval, stddev)
        
        
    def asin(self):
        if (abs(self)) >= 1:
            raise ValueError ("asin(x): |x| >= 1")
        nomval = m.asin(self.nomval)
        stddev = self.stddev / m.sqrt(1 - self.nomval**2)   # asin'(x) = 1 / sqrt(1 - x²), |x| < 1
        return ufloat(nomval, stddev)
        
        
    def asinh(self):
        nomval = m.asinh(self.nomval)
        stddev = self.stddev / m.sqrt(1 + self.nomval**2)   # asinh'(x) = 1 / sqrt(x² + 1) 
        return ufloat(nomval, stddev)
        
        
    def atan(self):
        nomval = m.atan(self.nomval)
        stddev = self.stddev / (1 + self.nomval**2)         # atan'(x) = 1 / (x² + 1) 
        return ufloat(nomval, stddev)
        
        
    def atan2(self, other):
        # 'atan2': [lambda y, x: x/(x**2+y**2),  # Correct for x == 0
        #           lambda y, x: -y/(x**2+y**2)],  # Correct for x == 0
        y = self
        x = other
        nomval = m.atan2(y.nomval, x.nomval)
        stddev = m.sqrt((y.stddev * ( x.nomval/(x.nomval**2 + y.nomval**2)))**2 + 
                        (x.stddev * (-y.nomval/(x.nomval**2 + y.nomval**2)))**2) 
        return ufloat(nomval, stddev)
        
        
    def atanh(self):
        if (abs(self)) >= 1:
            raise ValueError ("atanh(x): |x| >= 1")
        nomval = m.atanh(self.nomval)
        stddev = self.stddev / (1 - self.nomval**2)         # atanh'(x) = 1 / (1 - x²), |x| < 1
        return ufloat(nomval, stddev)


    def _deriv_copysign(x, y):
        if x >= 0:
            return m.copysign(1, y)
        else:
            return -m.copysign(1, y)
    
    def copysign(self, other):
        # 'copysign': [_deriv_copysign,
        #          lambda x, y: 0],
        nomval = m.copysign(self.nomval, other.nomval)
        stddev = self.stddev * self._deriv_copysign(other)  # + other.stddev * 0
        return ufloat(nomval, stddev)

    
    def cos(self):
        nomval = m.cos(self.nomval)
        stddev = - self.stddev * m.sqrt(1 - nomval**2)      # cos'(x) = -sin(x) = -sqrt(1 - cos²(x))
        return ufloat(nomval, stddev)
        
        
    def cosh(self):
        nomval = m.cosh(self.nomval)
        stddev = self.stddev * m.sqrt(1 + nomval**2)        # cosh'(x) = sinh(x) = sqrt(1 + cosh²(x))
        return ufloat(nomval, stddev)
        
    
    def degrees(self):
        nomval = m.degrees(self.nomval)
        stddev = self.stddev * m.degrees(1)
        return ufloat(nomval, stddev)
        
    deg = degrees
        
    def erf(self):
        nomval = m.erf(self.nomval)
        stddev = self.stddev * m.exp(-self.nomval**2) * erf_coef    # erf'(x) = 2 / sqrt(pi) * exp(-x²)
        return ufloat(nomval, stddev)
    
        
    def erfc(self):
        nomval = m.erfc(self.nomval)
        stddev = - self.stddev * m.exp(-self.nomval**2) * erf_coef  # erfc'(x) = - 2 / sqrt(pi) * exp(-x²)
        return ufloat(nomval, stddev)
    

    def exp(self):
        nomval = m.exp(self.nomval)
        stddev = self.stddev * nomval                       # exp'(x) = exp(x)
        return ufloat(nomval, stddev)
    

    def expm1(self):
        nomval = m.expm1(self.nomval)
        stddev = self.stddev * nomval                       # expm1'(x) = expm1(x)
        return ufloat(nomval, stddev)
    

    def _deriv_fabs(x):
        return m.copysign(1, x)


    def fabs(self):
        nomval = m.fabs(self.nomval)
        stddev = self.stddev * _deriv_fabs(self.nomval)
        return ufloat(nomval, stddev)
    

    def _psi(self):
        '''psi(x) (or the Digamma function) is the logarithmic derivative of the Gamma 
        function, defined as psi(x) = d/dx ln(gamma(x)) = gamma'(x) / gamma(x)  
        Thus, it is also the derivative of the lgamma(x) function. 
        psi(x) is also identical to H(x-1) - gamma (the Euler-Mascheroni constant), 
        with H(x-1) being the (x-1)st partial sum of the harmonic series, which in turn 
        can be approximated by using an asymptotic development with great precision (5). '''
        x = self
        return (m.log(x) + 1/(2*x) - 1/(12*x**2) + 1/(120*x**4) - 1/(252*x**6) + 1/(240*x**8) - 1/(132*x**10))
        # TODO calculating it this way is not particularly efficient. 


    def gamma(self):
        '''gamma(x) is the generalized factorial function for real arguments.
        The derivative is gamma'(x) = gamma(x) * psi(x). '''
        nomval = m.gamma(self.nomval)
        stddev = self.stddev * nomval * self._psi()
        return ufloat(nomval, stddev)
        # not that the gamma function played a big role in engineerial error propagation, but hey. 
                

    def hypot(self, other):
        # 'hypot': [lambda x, y: x/math.hypot(x, y),
        #       lambda x, y: y/math.hypot(x, y)],
        x = self
        y = other
        nomval = m.sqrt(x.nomval*x.nomval + y.nomval*y.nomval)
        stddev = m.sqrt((x.stddev * x.nomval / nomval)**2 + 
                        (y.stddev * y.nomval / nomval)**2)
        return ufloat(nomval, stddev)
                

    def lgamma(self):
        '''lgamma(x) is the log of the generalized factorial function, gamma(x).
        The derivative is lgamma'(x) = psi(x). '''
        nomval = m.gamma(self.nomval)
        stddev = self.stddev * self._psi()
        return ufloat(nomval, stddev)
        # not that the lgamma function played a big role in engineerial error propagation, but hey. 
        
        
    def log(self):
        if (self) <= 0:
            raise ValueError ("log(x): x <= 0")
        nomval = m.log(self.nomval)
        stddev = self.stddev / self.nomval                  # log'(x) = 1 / x
        return ufloat(nomval, stddev)

    ln = log

    def log10(self):
        if (self) <= 0:
            raise ValueError ("log(x): x <= 0")
        nomval = m.log10(self.nomval)
        stddev = self.stddev / self.nomval / m.log(10.0)
        return ufloat(nomval, stddev)

    lg = log10                                      # which is what we used in the old days - bear with me.

    def log2(self):
        if (self) <= 0:
            raise ValueError ("log(x): x <= 0")
        nomval = m.log2(self.nomval)
        stddev = self.stddev / self.nomval / m.log(2.0)
        return ufloat(nomval, stddev)


    def __pow__(self, other):
        # (1) f = A**B
        if isinstance (other, (int, float)):
            # (1) f = a * A ** b
            other = ufloat(other, 0.0)              # saves us another code path -> more compact
        cov = self._covariance(other)
        nomval = self.nomval ** other.nomval
        stddev = abs(nomval) * m.sqrt((other.nomval * self.stddev / self.nomval)**2 + 
                                      (m.log(self.nomval) * other.stddev)**2 + 
                                      (2 * other.nomval * m.log(self.nomval) * cov / self.nomval)
                                     )
        return ufloat(nomval, stddev)

        
    def radians(self):
        nomval = m.radians(self.nomval)
        stddev = self.stddev * m.radians(1)
        return ufloat(nomval, stddev)
                
    rad = radians
       
    def sin(self):
        nomval = m.sin(self.nomval)
        stddev = self.stddev * m.sqrt(1 - nomval**2)        # sin'(x) = cos(x) = sqrt(1 - sin²(x))
        return ufloat(nomval, stddev)
        
        
    def sinh(self):
        nomval = m.sinh(self.nomval)
        stddev = self.stddev * m.sqrt(1 + nomval**2)        # sinh'(x) = cosh(x) = sqrt(1 + sinh²(x))
        return ufloat(nomval, stddev)
        

    def sqrt(self):
        # return self ** 0.5
        # (4) does deriv = 0.5/math.sqrt(x) - what is cheaper? 
        if (self) <= 0:
            raise ValueError ("sqrt(x): x <= 0")
        nomval = m.sqrt(self.nomval)
        stddev = self.stddev * 0.5 / nomval                 # sqrt'(x) = 0.5 / sqrt(x) but we want to calculate sqrt(x) only once. 
        return ufloat(nomval, stddev)

        
    def tan(self):
        nomval = m.tan(self.nomval)
        stddev = self.stddev * (1 + nomval**2)              # tan'(x) = 1 + tan²(x) but we want to calculate tan(x) only once. 
        return ufloat(nomval, stddev)
        
        
    def tanh(self):
        nomval = m.tanh(self.nomval)
        stddev = self.stddev * (1 - nomval**2)              # tanh'(x) = 1 - tanh²(x) but we want to calculate tanh(x) only once. 
        return ufloat(nomval, stddev)

        

        
        
        
