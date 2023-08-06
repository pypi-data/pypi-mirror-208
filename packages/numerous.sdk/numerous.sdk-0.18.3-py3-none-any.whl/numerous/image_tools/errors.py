import traceback


def tb_str(e):
    s = traceback.format_exception(e, value=e, tb=e.__traceback__)
    es = [ss.strip() for ss in s]
    return "\n".join(es)


class SimulationError(Exception):
    pass
