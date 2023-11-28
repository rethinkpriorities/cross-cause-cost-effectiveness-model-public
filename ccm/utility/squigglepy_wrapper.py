import squigglepy as sq


def sample(dist: sq.OperableDistribution | None, n: int = 1, **kwargs):
    kwargs["n"] = n
    return sq.sample(dist, **kwargs)


def sample_probabilities(number):
    return sample(sq.uniform(0, 1), n=number)


RNG = sq.rng._squigglepy_internal_rng
