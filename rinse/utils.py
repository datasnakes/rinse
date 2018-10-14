from string import Template

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