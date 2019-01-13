# Contains some useful utility functions

def shiftBytes(list):
    sum_to_return = 0
    for count, item in enumerate(list):
        sum_to_return += item << ((len(list)-1-count)*8)
    return sum_to_return