from scipy.integrate import quad
import numpy as np

def miau():
    """Make a miau.

    Based on: https://math.stackexchange.com/questions/2305597/integral-that-evaluates-to-42
    """
    integral,error=quad(lambda x:(2*x**4-x**3)*np.exp(-x),0,np.inf)
    return integral

def guau():
    """Make a guau.

    Based on: https://math.stackexchange.com/questions/2305597/integral-that-evaluates-to-42
    """
    integral,error=quad(lambda x:1/(2*np.pi)*x**5*((4-x)/x)**0.5,0,4)
    return integral
