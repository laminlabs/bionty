# inheriting from SystemExit has the sole purpose of suppressing
# the traceback - this isn't optimal but the current best solution
# https://laminlabs.slack.com/archives/C04A0RMA0SC/p1726856875597489


class OrganismNotSet(SystemExit):
    """The `organism` parameter was not passed or is not globally set."""

    pass
