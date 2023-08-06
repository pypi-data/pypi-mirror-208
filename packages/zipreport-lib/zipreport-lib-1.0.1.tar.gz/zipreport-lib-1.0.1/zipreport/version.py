ZIPREPORT_VERSION = ["1", "0", "1"]


def get_version():
    return ".".join(ZIPREPORT_VERSION)


__version__ = get_version()
