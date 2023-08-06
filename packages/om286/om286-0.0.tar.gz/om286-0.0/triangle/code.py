from math import sqrt

def triangle_perimeter(a=7,b=2,c=8):
    return a+b+c

def triangle_area(a=7,b=2,c=8):
    p = triangle_perimeter(a,b,c)/2
    return sqrt(p*sqrt(p-a)*sqrt(p-b)*sqrt(p-c))