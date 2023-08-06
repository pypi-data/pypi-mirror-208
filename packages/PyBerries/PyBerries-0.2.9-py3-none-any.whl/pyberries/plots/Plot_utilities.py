from warnings import warn

def get_error_func(error=None):
    if callable(error):
        return error
    elif error == 'sd':
        return lambda x: x.std()
    elif error == 'se':
        return lambda x: x.sem()
    elif error == None:
        return None
    else:
        warn(f'Unknown error method: "{error}"')
        return None