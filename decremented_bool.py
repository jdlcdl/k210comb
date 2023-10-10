def decremented_bool(value):
    '''
    returns value as a bool, or as value-1 when value >0

    used to decrement verbosity as functions call other functions.
    '''

    if type(value) == int:
        if value > 0:
            return value - 1

        elif value == 0:
            return False

        else:
            raise TypeError('if value is <int>, must be >= 0: found %d' % value)

    elif type(value) == bool:
        return value

    else:
        raise TypeError('value must be <int> >= 0 or <bool> found %s' % value)

