from string import Template
from rinse.core import LInstallR, MacInstallR, WInstallR
from os import name as osname
from sys import platform as sysplat


def import_temp(filepath):
    """Import a file that you need a template of and that has temp strings.

    :param filepath: The path/name of the template file.
    """

    file_temp = open(filepath, 'r')
    file_str = file_temp.read()
    file_temp.close()

    file_temp = Template(file_str)
    return file_temp


def file_to_str(filepath):
    """Turn the contents of a file into a string.

    :param filepath: Path of the input file.
    """

    file_temp = open(filepath, 'r')
    file_str = file_temp.read()
    return file_str


def get_system_installer():
    """
    Determine the proper R installation method to use based on the system.
    :return: A system dependent installation class that is uncalled.
    """
    if osname == "posix":
        if sysplat == "darwin":
            rinstall = MacInstallR()
            rinstall.raise_error()
        elif "linux" in str(sysplat):
            return LInstallR

        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)
    elif osname == "nt":
        if sysplat == "win32":
            rinstall = WInstallR()
            rinstall.raise_error()
        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)