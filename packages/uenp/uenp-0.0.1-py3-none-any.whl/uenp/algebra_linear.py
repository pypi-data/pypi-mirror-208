def lista_par(len):
    arr = [] * len
    i = 0

    while (i < len * 2):
        if (i % 2 == 0):
            arr.append(i)
        i += 1

    return arr
