def isset(array, index):
    try:
        array[index]
        return True
    except KeyError:
        return False
