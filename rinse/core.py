from pkg_resources import resource_filename

from rinse.utils import import_temp
from rinse import installr


def install_r(version, install_path):
    script = import_temp(resource_filename(installr.__name__, "installr.sh"))
    updated_script = script.format(rversion=version, prefix=install_path)
    return updated_script
