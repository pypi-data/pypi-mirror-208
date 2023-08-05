import tempfile
from pathlib import Path
from unittest import TestCase

from ha_services.cli_tools.path_utils import backup, expand_user
from ha_services.cli_tools.test_utils.environment_fixtures import AsSudoCallOverrideEnviron


class PathUtilsTestCase(TestCase):
    def test_expand_user(self):
        real_home_path = Path.home()
        real_example = Path('~/example/').expanduser()

        self.assertEqual(expand_user(Path('~')), real_home_path)
        self.assertEqual(expand_user(Path('~/example/')), real_example)

        with AsSudoCallOverrideEnviron():
            self.assertEqual(Path('~').expanduser(), Path('/root'))
            self.assertEqual(expand_user(Path('~')), real_home_path)

            self.assertEqual(Path('~/example/').expanduser(), Path('/root/example'))
            self.assertEqual(expand_user(Path('~/example/')), real_example)

    def test_backup(self):
        with tempfile.TemporaryDirectory(prefix='test_') as temp_dir:
            temp_path = Path(temp_dir)

            test_path = temp_path / 'foobar.ext'
            test_path.write_text('one')

            bak1_path = backup(test_path)
            self.assertEqual(bak1_path, temp_path / 'foobar.ext.bak')
            self.assertEqual(bak1_path.read_text(), 'one')

            test_path.write_text('two')

            bak2_path = backup(test_path)
            self.assertEqual(bak2_path, temp_path / 'foobar.ext.bak2')
            self.assertEqual(bak2_path.read_text(), 'two')

            test_path.write_text('three')

            bak3_path = backup(test_path)
            self.assertEqual(bak3_path, temp_path / 'foobar.ext.bak3')
            self.assertEqual(bak3_path.read_text(), 'three')

            with self.assertRaises(RuntimeError) as cm:
                backup(test_path, max_try=3)
            self.assertEqual(cm.exception.args, ('No backup made: Maximum attempts to find a file name failed.',))
