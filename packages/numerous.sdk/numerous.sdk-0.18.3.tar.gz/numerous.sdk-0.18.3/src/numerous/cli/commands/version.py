import pkg_resources

from ..utils import bold, green


def command_version():
    version = pkg_resources.get_distribution("numerous.sdk").version
    print(green(f"{bold('numerous.sdk')} command line tool v{bold(version)}"))
