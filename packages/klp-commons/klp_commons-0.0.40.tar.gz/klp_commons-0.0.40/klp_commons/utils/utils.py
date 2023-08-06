def divide_chunks(l: list = None, n: int = 100) -> list:

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_full_class_name(obj):
    """
    get full class name error 
    """
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


