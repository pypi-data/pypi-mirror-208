import logging
import shutil
import subprocess


logger = logging.getLogger(__name__)


COMMANDS = (
    'sensible-editor',
    'mcedit',
    'nano',
    'edit',
    'open',
)


def open_editor_for(file_path):
    """
    Try to open the given file in a editor.
    """
    for command in COMMANDS:
        if bin := shutil.which(command):
            logger.debug('Call: "%s %s"', bin, file_path)
            try:
                return subprocess.check_call([bin, file_path])
            except subprocess.SubprocessError as err:
                print(f'Error open {file_path} with {bin}: [red]{err}')
        else:
            logger.debug(f'No "{command}" found.')

    print(f'Error not editor found to open {file_path}!')
