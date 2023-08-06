from math import pi, pow

def circle_perimeter(default_radius = 5):
    return 2*pi*default_radius

def circle_area(default_radius = 5):
    return pi*pow(default_radius,2)