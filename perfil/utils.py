def calcula_total(objeto, campo):
    total = 0
    for item in objeto:
        total += getattr(item, campo)
    return total
