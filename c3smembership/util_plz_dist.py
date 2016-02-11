from pyramid.view import view_config


from c3smembership.models import C3sMember


@view_config(
    renderer='templates/postal_codes_de.pt',
    permission='manage',
    route_name='plz_dist')
def plz_dist(request):  # pragma: no cover
    """
    XXX TODO: write a test case
    """
    codes = C3sMember.get_postal_codes_de()

    codes_and_freq = {}
    for c in codes:
        if c in codes_and_freq:
            codes_and_freq[c] += 1
        else:
            codes_and_freq[c] = 1
    import operator
    codes_and_freq_sorted = sorted(
        codes_and_freq.items(), key=operator.itemgetter(1))

    return {
        'codes': codes,  # the postal codes, raw, with duplicates
        'codes_and_freq': codes_and_freq_sorted,
    }
