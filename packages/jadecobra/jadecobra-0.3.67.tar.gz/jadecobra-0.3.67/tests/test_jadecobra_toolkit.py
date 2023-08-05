import src.jadecobra
import src.jadecobra.tester
import src.jadecobra.toolkit
import src.jadecobra.versioning


class TestJadeCobraToolkit(src.jadecobra.tester.TestCase):

    def test_toolkit(self):
        self.assert_attributes_equal(
            src.jadecobra.toolkit,
            [
                '__builtins__',
                '__cached__',
                '__doc__',
                '__file__',
                '__loader__',
                '__name__',
                '__package__',
                '__spec__',
                'datetime',
                'delete',
                'delimiter',
                'error',
                'file_exists',
                'get_commit_message',
                'get_latest_published_version',
                'git_commit',
                'git_diff',
                'header',
                'json',
                'log_performance',
                'logger',
                'make_parent_directory',
                'os',
                'package',
                'pathlib',
                'publish',
                'read_json',
                'run_in_shell',
                'subprocess',
                'time',
                'time_it',
                'to_camel_case',
                'write_config',
                'write_file'
            ]
        )

    def test_to_camel_case(self):
        self.assertEqual(
            src.jadecobra.toolkit.to_camel_case('abc-def-hij'),
            'AbcDefHij'
        )