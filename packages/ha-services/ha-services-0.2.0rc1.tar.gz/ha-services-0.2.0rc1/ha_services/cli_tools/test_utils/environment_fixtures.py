import getpass
import os
import shlex
import sys

from bx_py_utils.environ import OverrideEnviron


class AsSudoCallOverrideEnviron(OverrideEnviron):
    """
    Manipulate the environment variables so it looks like a "sudo" call.
    Compare with: "sudo env | sort" ;)
    """

    def __init__(self, **overrides):
        overrides = {
            'SUDO_COMMAND': shlex.join(sys.argv),
            'SUDO_UID': str(os.getuid()),
            'SUDO_GID': str(os.getgid()),
            'SUDO_USER': getpass.getuser(),
            'LOGNAME': 'root',
            'HOME': '/root',
            **overrides,
        }
        super().__init__(**overrides)
