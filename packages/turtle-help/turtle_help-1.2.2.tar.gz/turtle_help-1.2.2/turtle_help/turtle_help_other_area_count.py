def square_area(foot):
    A=foot*foot
    return A
def rectangle_area(long,wide):
    A=long*wide
    return A
def circle_area(pi,radius):
    A=pi*radius*radius
    return A
def trapezium_area(up_long,down_long,high):
    A=(up_long+down_long)*high/2
    return A
def trangle_area(down_long,high):
    A=down_long*high/2
    return A
def o_trangle(o,t,tr):
    import math as m
    s=(o+t+tr)/2
    A=int(m.sqrt(s*(s-o)*(s-t)*(s-tr)))
    return A
"""
this module is a other module for turtle_help
name:
     turtle_help_other_area_count
you can count area of graphics
thanks to use turtle_help!
                         -DanJamesThomas(developers)
"""
