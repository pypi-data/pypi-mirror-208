def info():
    print("""
import sympy
from sympy import expand,factor,simplify,symbols
a=symbols('a')
b=symbols('b')
x=symbols('x')
expr=expand((a+b)**2)
print("The expansion of(a+b)^2 is =",expr)
fact=factor(expr)
print("The factor of",expr,"is =",fact)
simp1=simplify(2*x**2+x*(4*x+3))
print("The simplification of 2x^2+x(4x+3)=",simp1)
    """)