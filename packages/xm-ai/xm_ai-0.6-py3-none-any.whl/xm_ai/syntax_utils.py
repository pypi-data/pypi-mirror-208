def remove_duplicates(a: list, b: list):
    for element in a:
        while element in b:
            b.remove(element)
    return b
