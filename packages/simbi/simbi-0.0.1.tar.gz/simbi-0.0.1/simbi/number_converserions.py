def nbec_from_cf(cf, nth):
    return (cf * nth) / (1 - cf)


def nth_from_cf(cf, nbec):
    return nbec * (1 / cf - 1)


def get_cf(nth, nbec):
    return nbec / (nth + nbec)