from string import Template
from rinse.core import LinuxInstallR, MacInstallR, WindowsInstallR
from os import name as osname
from sys import platform as sysplat
import subprocess as sp
from subprocess import TimeoutExpired


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
            MacInstallR()
        elif "linux" in str(sysplat):
            return LinuxInstallR
        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)
    elif osname == "nt":
        if sysplat == "win32":
            WindowsInstallR()
        else:
            raise OSError("rinse does not support the %s operating system at this time." % sysplat)


def system_cmd(cmd, timeout=None, **kwargs):
    """
    A function for making system calls, while preforming proper exception handling.
    :param cmd:  A list that contains the arguments for Popen.
    :param timeout:  A timeout variable.
    :param kwargs:  Any other keyword arguments for Popen.
    :return:  Returns the stdout and stderr as a tuple.
    """
    proc = sp.Popen(cmd, stderr=sp.PIPE, stdout=sp.PIPE, **kwargs)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    return stdout, stderr


